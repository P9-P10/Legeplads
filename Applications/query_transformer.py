from Structures.Query import Query
from Structures.Schema import Schema
from Structures.Changes import *
from sqlglot import exp
from Applications.exceptions import *


class Relation:
    def __init__(self, name: str, alias: str, index: int):
        self.name = name
        self.alias = alias
        self.index = index

    def __repr__(self):
        return f'Relation(Name: {self.name}, Alias: {self.alias}, Index: {self.index})'

    def change_alias(self, new_alias: str):
        self.alias = new_alias


class Attribute:
    def __init__(self, name, relation_index):
        self.name = name
        self.relation_index = relation_index

    def __repr__(self):
        return f'Attribute(Name: {self.name}, Relation_index: {self.relation_index})'

    def change_relation(self, new_index: int):
        self.relation_index = new_index

    def change_name(self, new_name):
        self.name = new_name


class Expression:
    """
    An Expression is some part of a query that contains attributes.
    The purpose of the class is to be able to manipulate the attributes that appear in elements of the query,
    without having to be concerned with the type of the element.
    """

    def __init__(self, expression: exp.Expression, attributes: list[Attribute]):
        self.expression = expression
        self.attributes = attributes

    def change_attributes(self, new_attributes: list[Attribute]):
        self.attributes = new_attributes

    def change_references_to_relations_in_attributes(self, indicies_to_replace: list[int], new_index: int):
        for attr in self.attributes:
            if attr.relation_index in indicies_to_replace:
                attr.change_relation(new_index)


class RangeTable:
    def __init__(self):
        self.relations = []
        self.relation_names = []

    def append(self, name: str, alias: str) -> int:
        relation = Relation(name, alias, len(self.relations))
        self.relations.append(relation)
        self.relation_names.append(name)
        # Return the index of the added item
        return relation.index

    def contains(self, table_name) -> bool:
        return table_name in self.relation_names

    def index_of_entries_with_name(self, table_name) -> list[int]:
        return [relation.index for relation in self.relations if relation.name == table_name]

    def index_of_matching_relation(self, name: str, alias: str):
        return self.get_matching_relation(name, alias).index

    def get_matching_relation(self, name: str, alias: str) -> Relation:
        for relation in self.relations:
            if relation.name == name and relation.alias == alias:
                return relation
                # TODO raise exception if there is no match

    def get_relation_for_attribute(self, attribute: Attribute) -> Relation:
        return self.relations[attribute.relation_index]

    def get_relation_with_alias(self, alias: str):
        for relation in self.relations:
            if relation.alias == alias or relation.name == alias:
                return relation
        # TODO raise exception if there is no match

    def get_relation_with_index(self, index: int):
        return self.relations[index]


class ExpressionCompiler:
    def __init__(self, range_table: RangeTable):
        self.range_table = range_table

    def compile(self, expression: Expression):
        empty_query = Query("")
        if isinstance(expression.expression, exp.Column) or expression.expression is None:
            # An instance of query is needed as it has methods for creating nodes
            # TODO: This is a hint that this should not be the case
            selection_expressions = []
            for attribute in expression.attributes:
                relation = self.range_table.get_relation_for_attribute(attribute)
                selection_expressions.append(empty_query.create_column(attribute.name, relation.alias))
            return selection_expressions
        else:
            for column, attribute in zip(expression.expression.find_all(exp.Column), expression.attributes):
                relation = self.range_table.get_relation_for_attribute(attribute)
                column.replace(empty_query.create_column(attribute.name, relation.alias))
            return [expression.expression]


class Selection:
    def __init__(self, range_table: RangeTable, selection: list[Attribute], select_star: bool):
        self.range_table = range_table
        self.selection_list = selection
        self.select_star = select_star
        self.initial_selection = selection.copy()

    # manipulation
    def change_source_relation_for_column(self, column_name: str, current_source_name: str, new_source_index: int):
        indicies = self.range_table.index_of_entries_with_name(current_source_name)
        for expr in self.selection_list:
            new_list = []
            for attribute in expr.attributes:
                if attribute.name == column_name and attribute.relation_index in indicies:
                    new_attr = Attribute(column_name, new_source_index)
                else:
                    new_attr = attribute
                new_list.append(new_attr)

            expr.change_attributes(new_list)

    def change_relations(self, old_indicies: list[int], new_index: int):
        for expr in self.selection_list:
            for attribute in expr.attributes:
                if attribute.relation_index in old_indicies:
                    attribute.change_relation(new_index)

    # compilation
    def create_select_expressions(self):
        compiler = ExpressionCompiler(self.range_table)
        selection_expressions = []
        for expr in self.selection_list:
            selection_expressions.extend(compiler.compile(expr))
        return selection_expressions

    # manipulation
    def get_unused_relations(self):
        if self.select_star:
            return []

        unused_relations = []
        for relation in self.range_table.relations:
            used = False
            for expr in self.selection_list:
                for attribute in expr.attributes:
                    if attribute.relation_index == relation.index:
                        used = True
            if not used:
                unused_relations.append(relation)

        return unused_relations

    def change_name_of_attributes(self, old_name, new_name, indexes):
        for expression in self.selection_list:
            for attribute in expression.attributes:
                if attribute.name == old_name and attribute.relation_index in indexes:
                    attribute.change_name(new_name)


class Join:
    def __init__(self, relation_index: int, attributes: list[Attribute], condition):
        self.relation_index = relation_index
        self.attributes = attributes
        self.condition = condition

    def change_relation(self, new_index: int):
        self.relation_index = new_index

    def change_attributes(self, new_attributes: list[Attribute]):
        self.attributes = new_attributes

    def change_condition(self, new_condition):
        self.condition = new_condition


class JoinTree:
    def __init__(self, range_table: RangeTable, joins: list[Join]):
        self.range_table = range_table
        self.joins = joins

    # manipulation
    def add_join_without_condition(self, relation_index):
        relation = self.range_table.get_relation_with_index(relation_index)
        self.joins.append(Join(relation.index, [], None))

    # compilation
    def create_join_expressions(self):
        # Empty query needed to create AST Nodes
        # See comment in Selection.create_select_expressions
        empty_query = Query("")
        new_joins = []
        for join in self.joins:
            # Change the columns in the condition
            if join.condition:
                for column, attr in zip(join.condition.find_all(exp.Column), join.attributes):
                    attr_relation = self.range_table.get_relation_for_attribute(attr)
                    if attr_relation.alias == '':
                        relation_name = attr_relation.name
                    else:
                        relation_name = attr_relation.alias
                    column.replace(empty_query.create_column(attr.name, relation_name))

            relation = self.range_table.get_relation_with_index(join.relation_index)
            alias = None if relation.alias == "" else relation.alias
            new_joins.append(empty_query.create_join_with_condition(relation.name, join.condition, alias))

        return new_joins

    # manipulation
    def remove_relations_with_name(self, relation_name: str):
        self.joins = [join for join in self.joins if
                      not self.range_table.get_relation_with_index(join.relation_index).name == relation_name]

    def remove_relation(self, relation: Relation):
        self.joins = [join for join in self.joins if not join.relation_index == relation.index]

    # manipulation
    def change_references_to_relations_in_attributes(self, indicies_to_replace: list[int], new_index: int):
        for join in self.joins:
            for attr in join.attributes:
                if attr.relation_index in indicies_to_replace:
                    attr.change_relation(new_index)

    # manipulation
    def move_condition(self, indicies_to_replace: list[int], new_index: int):
        for join in self.joins:
            if join.relation_index == new_index:
                new_join = join
                break

        for join in self.joins:
            if join.relation_index in indicies_to_replace:
                new_join.change_attributes(join.attributes)
                new_join.change_condition(join.condition)

    def relations_used_in_conditions(self):
        indicies = []
        for join in self.joins:
            for attribute in join.attributes:
                indicies.append(attribute.relation_index)

        return set(indicies)


# TODO: Change to use Expression instead of list of attributes and condition
class FromExpr:
    def __init__(self, relation_indicies: list[int], attributes: list[Attribute], condition):
        self.relation_indicies = relation_indicies
        self.attributes = attributes
        self.condition = condition

    def change_references_to_relations_in_attributes(self, indicies_to_replace: list[int], new_index: int):
        for attr in self.attributes:
            if attr.relation_index in indicies_to_replace:
                attr.change_relation(new_index)


######################
# Parser
######################
class Parser:
    def __init__(self, db_structure: Schema):
        self.db_structure = db_structure

    def parse(self, ast: exp.Expression):
        self.ast = ast
        range_table = self.create_range_table()
        selection = self.create_selection(range_table)
        join_tree = self.create_join_tree(range_table)

        return range_table, selection, join_tree

    # Range Table
    def create_range_table(self) -> RangeTable:
        range_table = RangeTable()
        self.populate_range_table(range_table, self.get_from_expressions(), self.get_join_expressions())
        return range_table

    def populate_range_table(self, range_table: RangeTable, from_expressions: list[exp.Expression],
                             join_expressions: list[exp.Expression]):
        all_expressions = from_expressions + [join_exp.this for join_exp in join_expressions]
        entries = [self.create_range_table_entry(expression) for expression in all_expressions]
        for name, alias in entries:
            range_table.append(name, alias)

    def create_range_table_entry(self, expression):
        if isinstance(expression, exp.Alias):
            return (expression.this.name, expression.alias)
        elif isinstance(expression, exp.Table):
            return (expression.name, "")

    # Selection
    def create_selection(self, range_table: RangeTable) -> Selection:
        if isinstance(self.ast.expressions[0], exp.Star):
            select_star = True
            selection_list = self.from_star_expression(range_table)
        else:
            select_star = False
            selection_list = self.from_expressions(self.ast.expressions, range_table)

        return Selection(range_table, selection_list, select_star)

    def from_star_expression(self, range_table: RangeTable) -> list[Attribute]:
        result = []
        for relation in range_table.relations:
            columns_in_table = self.db_structure.get_columns_in_table(relation.name)
            result.extend(
                [Expression(None, [Attribute(column_name, relation.index) for column_name in columns_in_table])])
        return result

    def from_expressions(self, expressions: list[exp.Expression], range_table: RangeTable) -> list[Attribute]:
        result = []
        for expression in expressions:
            if isinstance(expression, exp.Column):
                expr = Expression(expression, [self.attribute_from_column(expression, range_table)])
            else:
                expr = Expression(expression, [self.attribute_from_column(column, range_table) for column in
                                               expression.find_all(exp.Column)])

            result.append(expr)
        return result

    def attribute_from_column(self, expression: exp.Column, range_table: RangeTable) -> Attribute:
        column_name = expression.name
        # if the column uses an alias
        if expression.table:
            # The alias is either the full name of the table or an alias
            column_alias = expression.table
            for relation in range_table.relations:
                if column_alias == relation.name or column_alias == relation.alias:
                    return Attribute(column_name, relation.index)
        # Otherwise we need the database structure to find what table a column belongs to
        else:
            table_name = self.db_structure.table_containing_column(column_name, range_table.relation_names)
            # Index is the first (and hopefully only) occurence in the range table
            index = range_table.index_of_entries_with_name(table_name)[0]
            return Attribute(column_name, index)

    # Join Tree
    def create_join_tree(self, range_table: RangeTable) -> JoinTree:
        joins = []
        for node in self.get_join_expressions():
            relation_index = self.get_relation_from_node(node.this, range_table).index
            attributes = self.get_attributes_from_join_condition(node, range_table)
            condition = None
            # Add the 'on' expression node to the tuple if it exists 
            if 'on' in node.args.keys():
                condition = node.args['on'].copy()
            joins.append(Join(relation_index, attributes, condition))

        return JoinTree(range_table, joins)

    # (duplication from range_table)
    def get_relation_from_node(self, node: exp.Expression, range_table: RangeTable) -> Relation:
        if isinstance(node, exp.Alias):
            return range_table.get_matching_relation(node.this.name, node.alias)
        elif isinstance(node, exp.Table):
            return range_table.get_matching_relation(node.name, "")

    def get_attributes_from_join_condition(self, node: exp.Expression, range_table: RangeTable) -> list[Attribute]:
        result = []
        for column in node.find_all(exp.Column):
            if column.table:
                result.append(Attribute(column.name, range_table.get_relation_with_alias(column.table).index))
            else:
                table_name = self.db_structure.table_containing_column(column.name, range_table.relation_names)
                result.append(Attribute(column.name, range_table.index_of_matching_relation(table_name, "")))
        return result

    # From expression
    def create_from_expression(self, range_table: RangeTable):
        expressions = self.get_from_expressions()
        relation_indicies = [self.get_relation_from_node(expr, range_table).index for expr in expressions]
        if self.get_where_expression():
            attributes = self.get_attributes_from_join_condition(self.get_where_expression(), range_table)
        else:
            attributes = []
        condition = self.get_where_expression()

        return FromExpr(relation_indicies, attributes, condition)

    def get_from_expressions(self):
        return self.ast.args['from'].expressions

    def get_join_expressions(self):
        if 'joins' in self.ast.args.keys():
            return self.ast.args['joins']
        else:
            return []

    def get_where_expression(self):
        if 'where' in self.ast.args.keys():
            return self.ast.args['where'].this
        else:
            return []

    # ORDER BY and GROUP BY
    def get_other_expressions(self, range_table: RangeTable) -> list[Expression]:
        result = []
        if 'group' in self.ast.args.keys():
            result.extend(self.ast.args['group'].expressions)
        if 'order' in self.ast.args.keys():
            result.extend(self.ast.args['order'].expressions)

        return self.parse_expressions(result, range_table)

    # From AST expression to our expression
    def parse_expressions(self, expressions: list[exp.Expression], range_table: RangeTable) -> list[Expression]:
        result = []
        for expression in expressions:
            if isinstance(expression, exp.Column):
                expr = Expression(expression, [self.attribute_from_column(expression, range_table)])
            else:
                expr = Expression(expression, [self.attribute_from_column(column, range_table) for column in
                                               expression.find_all(exp.Column)])

            result.append(expr)
        return result


######################
# Transformer
######################
class Transformer:
    def __init__(self, old_db_structure: Schema, new_db_structure: Schema):
        self.old_db = old_db_structure
        self.new_db = new_db_structure

    def transform(self, query: Query, changes):
        self.query = query
        self.ast = query.get_ast()

        # Only handle SELECT queries
        if len(list(self.ast.find_all(exp.Select))) == 0:
            return

        # Extract and transform subqueries separately
        subqueries = self.query.extract_subqueries()
        for subquery in subqueries:
            Transformer(self.old_db, self.new_db).transform(subquery, changes)

        self.preprocess_query()
        self.apply_changes(changes)
        self.postprocess_query()

        self.query.insert_subqueries(subqueries)

    def preprocess_query(self):
        self.verify_selection_is_valid_given_structure(self.old_db)
        parser = Parser(self.old_db)
        range_table, selection, join_tree = parser.parse(self.ast)
        self.range_table = range_table
        self.selection = selection
        self.join_tree = join_tree
        self.from_expr = parser.create_from_expression(self.range_table)
        self.other_expressions = parser.get_other_expressions(range_table)

    def apply_changes(self, changes):
        for change in changes:
            if isinstance(change, RemoveTable):
                self.remove_relation_from_query(self.range_table.get_matching_relation(change.table_name, ""))
            elif isinstance(change, AddTable):
                self.add_table_to_query(change.table_name)
            elif isinstance(change, MoveColumn):
                if change.src_table_name in self.range_table.relation_names:
                    self.move_column(change)
            elif isinstance(change, ReplaceTable):
                self.replace_table(change)
            elif isinstance(change, RenameColumn):
                index = self.range_table.index_of_entries_with_name(table_name=change.table)
                self.selection.change_name_of_attributes(change.old_column, change.new_column, index)

    def postprocess_query(self):
        self.resolve_ambiguities()
        self.remove_unused_tables()
        self.ensure_from_not_empty()
        self.adjust_query_select_expression()
        self.adjust_query_join_expressions()
        self.adjust_other_expressions()

    def move_column(self, change):
        new_table_index = self.get_existing_or_create_new_relation(change.dst_table_name)
        self.selection.change_source_relation_for_column(change.column_name, change.src_table_name, new_table_index)
        indicies_to_replace = self.range_table.index_of_entries_with_name(change.src_table_name)
        self.join_tree.change_references_to_relations_in_attributes(indicies_to_replace, new_table_index)
        self.from_expr.change_references_to_relations_in_attributes(indicies_to_replace, new_table_index)

    def replace_table(self, change):
        if not change.old_table_name in self.range_table.relation_names:
            return

        indicies_to_replace = self.range_table.index_of_entries_with_name(change.old_table_name)

        for old_index in indicies_to_replace:
            new_index = self.get_index_of_new_relation(change.new_table_name)
            new_relation = self.range_table.get_relation_with_index(new_index)
            old_relation = self.range_table.get_relation_with_index(old_index)
            new_relation.change_alias(old_relation.alias)

            self.join_tree.change_references_to_relations_in_attributes([old_index], new_index)
            self.join_tree.move_condition([old_index], new_index)
            self.selection.change_relations([old_index], new_index)
            self.remove_relation_from_query(self.range_table.get_relation_with_index(old_index))

            for expression in self.other_expressions:
                expression.change_references_to_relations_in_attributes([old_index], new_index)

    def get_index_of_new_relation(self, relation_name: str):
        return self.add_table_to_query(relation_name)

    def get_existing_or_create_new_relation(self, relation_name: str):
        if not self.range_table.contains(relation_name):
            # Add it to the query
            return self.add_table_to_query(relation_name)
        else:
            # Find the first occurence of the table in the range_table
            return self.range_table.index_of_entries_with_name(relation_name)[0]

    def adjust_query_select_expression(self):
        selection_expressions = self.selection.create_select_expressions()
        self.query.ast.set('expressions', selection_expressions)

    def adjust_query_join_expressions(self):
        new_joins = self.join_tree.create_join_expressions()
        self.query.ast.set('joins', new_joins)

    def adjust_other_expressions(self):
        compiler = ExpressionCompiler(self.range_table)
        new_expressions = []
        for expr in self.other_expressions:
            new_expressions.extend(compiler.compile(expr))

        for old_expr, new_expr in zip(self.other_expressions, new_expressions):
            old_expr.expression.replace(new_expr)

    def remove_unused_tables(self):
        for unused_relation in self.selection.get_unused_relations():
            if unused_relation.index not in self.join_tree.relations_used_in_conditions():
                self.remove_relation_from_query(unused_relation)

    def get_relation_from_node(self, node: exp.Expression) -> Relation:
        if isinstance(node, exp.Alias):
            return self.range_table.get_matching_relation(node.this.name, node.alias)
        elif isinstance(node, exp.Table):
            return self.range_table.get_matching_relation(node.name, "")

    def add_table_to_query(self, table_name):
        new_table_index = self.range_table.append(table_name, "")
        self.ensure_table_is_not_ambiguous(table_name)
        # This could be simplified, as the case of an empty 'from' clause is handled.
        # However, that would not communicate the purpose of this operation as effectively
        if len(self.range_table.relations) > 1:  # If there is at least one table in the query
            self.join_tree.add_join_without_condition(new_table_index)
        else:
            self.from_expr.relation_indicies = [new_table_index]
            # self.ast.set("from", self.query.create_from_with_table(table_name))
        return new_table_index

    def ensure_table_is_not_ambiguous(self, table_name):
        indicies_of_relations_with_name = self.range_table.index_of_entries_with_name(table_name)
        if len(indicies_of_relations_with_name) > 1:
            for occurence, index in enumerate(indicies_of_relations_with_name):
                relation = self.range_table.get_relation_with_index(index)
                if relation.alias == "" or relation.alias == relation.name:
                    relation.change_alias(relation.name + str(occurence + 1))

    def remove_relation_from_query(self, relation):
        self.join_tree.remove_relation(relation)
        self.from_expr.relation_indicies = [index for index in self.from_expr.relation_indicies if
                                            not index == relation.index]

    def resolve_ambiguities(self):
        for expr in self.selection.selection_list:
            for attribute in expr.attributes:
                if len(self.new_db.get_tables_containing_column(attribute.name)) > 1:
                    relation = self.range_table.get_relation_with_index(attribute.relation_index)
                    if relation.alias == "" or relation.alias == relation.name:
                        relation.change_alias(relation.name)

    # Mix of parsing, manipulation, and compilation
    def ensure_from_not_empty(self):
        # If from is empty, move the first join into from
        if len(self.from_expr.relation_indicies) == 0:
            first_join = self.join_tree.joins.pop(0)
            self.from_expr.relation_indicies = [first_join.relation_index]
            self.from_expr.attributes = first_join.attributes
            if first_join.condition:
                self.from_expr.condition = first_join.condition

        # Create and insert from expressions
        expressions = []
        for index in self.from_expr.relation_indicies:
            relation = self.range_table.get_relation_with_index(index)
            if relation.alias:
                expressions.append(self.query.create_table_with_alias(relation.name, relation.alias))
            else:
                expressions.append(self.query.create_table(relation.name))
        self.ast.set('from', exp.From(expressions=expressions))

        # Adjust attributes used in WHERE condition
        if self.from_expr.condition:
            for column, attr in zip(self.from_expr.condition.find_all(exp.Column), self.from_expr.attributes):
                attr_relation = self.range_table.get_relation_for_attribute(attr)
                if attr_relation.alias == '':
                    relation_name = attr_relation.name
                else:
                    relation_name = attr_relation.alias
                column.replace(self.query.create_column(attr.name, relation_name))
        if self.from_expr.condition:
            self.ast.args['where'] = self.query.create_where_with_condition(self.from_expr.condition)

    # parsing
    def verify_selection_is_valid_given_structure(self, structure: Schema):
        column_nodes_in_expressions = self.flatten(
            [list(expression.find_all(exp.Column)) for expression in self.ast.expressions])
        column_names_in_selection = [column.name for column in column_nodes_in_expressions]

        table_nodes_in_from_expression = list(self.ast.find(exp.From).find_all(exp.Table))
        table_names = [table.name for table in table_nodes_in_from_expression]
        # This part is sort of sketchy
        # Need to somehow encapsulate selection and joins
        table_nodes_in_joins = self.flatten(
            [list(join.find_all(exp.Table)) for join in self.query.get_join_expressions()])
        table_names.extend([table.name for table in table_nodes_in_joins])

        for column_name in column_names_in_selection:
            if not structure.is_column_in_tables(column_name, table_names):
                raise InvalidSelectionException(
                    f'Column {column_name} is not present in the tables {",".join(table_names)}')

    def flatten(self, list):
        return [item for sublist in list for item in sublist]
