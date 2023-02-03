from Applications.Parsing import *

class ExpressionCompiler:
    def __init__(self, range_table: RangeTable):
        self.range_table = range_table


    def compile(self, expression: Expression):
        if expression.ast is None:
            return None
        if isinstance(expression.ast, exp.Column):
            self.compile_single_column(expression)
        else:
            self.compile_multiple_columns(expression)
        
        return expression.ast


    def compile_single_column(self, expression: Expression):
        relation = self.range_table.get_relation_for_attribute(expression.attributes[0])
        expression.ast = AST.create_column(expression.attributes[0].name, relation.alias)

    
    def compile_multiple_columns(self, expression: Expression):
        new_columns = [self.compile_attribute(attribute) for attribute in expression.attributes]
        # Each column should correspond to an attribute
        for column, new_column in zip(expression.ast.find_all(exp.Column), new_columns):
            column.replace(new_column)

        
    def compile_attribute(self, attribute: Attribute) -> exp.Column:
        attr_relation = self.range_table.get_relation_for_attribute(attribute)
        if attr_relation.alias == '':
            relation_name = attr_relation.name
        else:
            relation_name = attr_relation.alias
        return AST.create_column(attribute.name, relation_name)


class SelectionCompiler:
    def __init__(self, expression_compiler: ExpressionCompiler):
        self.expr_compiler = expression_compiler


    def compile(self, selection: Selection):
        selection_expressions = []
        for expr in selection.selection_list:
            selection_expressions.append(self.expr_compiler.compile(expr))

        return selection_expressions


class JoinTreeCompiler:
    def __init__(self, expression_compiler: ExpressionCompiler):
        self.expr_compiler = expression_compiler


    def compile(self, join_tree: JoinTree):
        new_joins = []
        for join in join_tree.joins:
            # Change the columns in the condition
            if join.expression.ast:
                self.expr_compiler.compile(join.expression)
                
            relation = join.relation
            alias = None if relation.alias == "" else relation.alias
            new_joins.append(AST.create_join_with_condition(relation.name, join.expression.ast, alias))

        return new_joins


class FromExprCompiler:
    def __init__(self, range_table: RangeTable, expression_compiler: ExpressionCompiler):
        self.range_table = range_table
        self.expr_compiler = expression_compiler

    def compile(self, join_tree: JoinTree):          
        # Create and insert from expressions
        expressions = []
        for index in join_tree.from_indicies:
            relation = self.range_table.get_relation_with_index(index)
            if relation.alias:
                expressions.append(AST.create_table_with_alias(relation.name, relation.alias))
            else:
                expressions.append(AST.create_table(relation.name))
        from_expr = exp.From(expressions=expressions)

        where_expr = None
        # Adjust attributes used in WHERE condition
        if join_tree.where_expr.ast:
            compiler = ExpressionCompiler(self.range_table)
            result = compiler.compile(join_tree.where_expr)
            where_expr = AST.create_where_with_condition(result)

        return from_expr, where_expr


class GroupbyAndOrderbyCompiler:
    def __init__(self, expression_compiler: ExpressionCompiler):
        self.expr_compiler = expression_compiler

    def compile(self, expressions):
        new_expressions = []
        for expr in expressions:
            new_expressions.append(self.expr_compiler.compile(expr))

        return new_expressions

