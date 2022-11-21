from .primitives import *
from .datastructures import *
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Query import Query
import Applications.Compilation.ast_factory as AST

class ExpressionParser:
    def __init__(self, db_structure: DatabaseStructure, range_table: RangeTable):
        self.db_structure = db_structure
        self.range_table = range_table

    def parse(self, expression: exp.Expression) -> Expression:
        if isinstance(expression, exp.Column):
            return Expression(expression, [self.attribute_from_column(expression)])
        else:
            return Expression(expression, [self.attribute_from_column(column) for column in expression.find_all(exp.Column)])

    def parse_list(self, expression_list: list[exp.Expression]) -> list[Expression]:
        return [self.parse(expression) for expression in expression_list]


    def attribute_from_column(self, expression: exp.Column) -> Attribute:
        column_name = expression.name
        # if the column uses an alias
        if expression.table:
            # The alias is either the full name of the table or an alias
            column_alias = expression.table
            for relation in self.range_table.relations:
                if column_alias == relation.name or column_alias == relation.alias:
                    return Attribute(column_name, relation.index)
        # Otherwise we need the database structure to find what table a column belongs to
        else:
            table_name = self.db_structure.table_containing_column(column_name, self.range_table.relation_names)
            # Index is the first (and hopefully only) occurence in the range table
            index = self.range_table.index_of_entries_with_name(table_name)[0]
            return Attribute(column_name, index)


class RangeTableParser:

    def parse(self, ast):
        self.ast = ast
        return self.create_range_table()

    def create_range_table(self) -> RangeTable:
        range_table = RangeTable()
        self.populate_range_table(range_table, self.get_from_expressions(), self.get_join_expressions())
        return range_table

    def populate_range_table(self, range_table: RangeTable, from_expressions: list[exp.Expression], join_expressions: list[exp.Expression]):
        all_expressions = from_expressions + [join_exp.this for join_exp in join_expressions]
        entries = [self.create_range_table_entry(expression) for expression in all_expressions]
        for name, alias in entries:
            range_table.append(name, alias)

    def create_range_table_entry(self, expression):
        if isinstance(expression, exp.Alias):
            return (expression.this.name, expression.alias)
        elif isinstance(expression, exp.Table):
            return (expression.name, "")

    def get_from_expressions(self):
        return self.ast.args['from'].expressions

    def get_join_expressions(self):
        if 'joins' in self.ast.args.keys():
            return self.ast.args['joins']
        else:
            return []


class SelectionParser:
    def __init__(self, expression_parser: ExpressionParser, db_structure: DatabaseStructure, range_table: RangeTable):
        self.db_structure = db_structure
        self.range_table = range_table
        self.expr_parser = expression_parser

    def parse(self, ast):
        self.ast = ast
        return self.create_selection()

    def create_selection(self) -> Selection:
        if isinstance(self.ast.expressions[0], exp.Star):
            select_star = True
            selection_list = self.from_star_expression()
        else:
            select_star = False
            selection_list = self.expr_parser.parse_list(self.ast.expressions)
        
        return Selection(self.range_table, selection_list, select_star)


    def from_star_expression(self) -> list[Expression]:
        result = []
        for relation in self.range_table.relations:
            columns_in_table = self.db_structure.get_columns_in_table(relation.name)
            result.extend([Expression(AST.create_column(column_name), [Attribute(column_name, relation.index)]) for column_name in columns_in_table])
        return result
        

class JoinTreeParser:
    def __init__(self, expression_parser: ExpressionParser, range_table: RangeTable):
        self.expr_parser = expression_parser
        self.range_table = range_table

    def parse(self, ast):
        self.ast = ast
        return self.create_join_tree()

    def create_join_tree(self) -> JoinTree:
        joins = []
        for node in self.get_join_expressions():
            relation_index = self.get_relation_from_node(node.this).index
            condition = Expression(None, [])
            if 'on' in node.args.keys():
                condition = self.expr_parser.parse(node.args['on'])
            joins.append(Join(relation_index, condition))

        return JoinTree(self.range_table, joins)

    # (duplication from range_table)
    def get_relation_from_node(self, node: exp.Expression) -> Relation:
        if isinstance(node, exp.Alias):
            return self.range_table.get_matching_relation(node.this.name, node.alias)
        elif isinstance(node, exp.Table):
            return self.range_table.get_matching_relation(node.name, "")

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


class Parser:
    def __init__(self,db_structure: DatabaseStructure):
        self.db_structure = db_structure

    def parse(self, ast: exp.Expression):
        self.ast = ast
        range_table = RangeTableParser().parse(ast)
        self.expression_parser = ExpressionParser(self.db_structure, range_table)
        selection = SelectionParser(self.expression_parser, self.db_structure, range_table).parse(ast)
        join_tree = JoinTreeParser(self.expression_parser, range_table).parse(ast)

        return range_table, selection, join_tree


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


    # (duplication from range_table)
    def get_relation_from_node(self, node: exp.Expression, range_table: RangeTable) -> Relation:
        if isinstance(node, exp.Alias):
            return range_table.get_matching_relation(node.this.name, node.alias)
        elif isinstance(node, exp.Table):
            return range_table.get_matching_relation(node.name, "")


    def get_attributes_from_join_condition(self, node: exp.Expression, range_table: RangeTable) -> list[Attribute]:
        return [self.attribute_from_column(column, range_table) for column in node.find_all(exp.Column)]


    # From expression
    def create_from_expression(self, range_table: RangeTable):
        expressions = self.get_from_expressions()
        relation_indicies = [self.get_relation_from_node(expr, range_table).index for expr in expressions]

        where_expr = self.get_where_expression()
        expression = Expression(None, [])
        if where_expr:
            expression = self.expression_parser.parse(self.get_where_expression())
        
        return FromExpr(relation_indicies, expression)


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
    def get_other_expressions(self) -> list[Expression]:
        result = []
        if 'group' in self.ast.args.keys():
            result.extend(self.ast.args['group'].expressions)
        if 'order' in self.ast.args.keys():
            result.extend(self.ast.args['order'].expressions)

        return self.expression_parser.parse_list(result)