from sqlglot import parse_one, exp


def test_sqlglot_parse_one_result():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"

    result = repr(parse_one(query))
    assert result == """(SELECT expressions: 
  (STAR ), from: 
  (FROM expressions: 
    (TABLE this: 
      (IDENTIFIER this: Users, quoted: False))), joins: 
  (JOIN this: 
    (ALIAS this: 
      (TABLE this: 
        (IDENTIFIER this: Orders, quoted: False)), alias: 
      (TABLEALIAS this: 
        (IDENTIFIER this: O, quoted: False))), on: 
    (EQ this: 
      (COLUMN this: 
        (IDENTIFIER this: id, quoted: False), table: 
        (IDENTIFIER this: Users, quoted: False)), expression: 
      (COLUMN this: 
        (IDENTIFIER this: owner, quoted: False), table: 
        (IDENTIFIER this: O, quoted: False)))), where: 
  (WHERE this: 
    (EQ this: 
      (COLUMN this: 
        (IDENTIFIER this: owner, quoted: False), table: 
        (IDENTIFIER this: O, quoted: False)), expression: 
      (LITERAL this: bob, is_string: True))))"""


def test_remove_aliases():
    query = "SELECT owner, id FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"
    expected = "SELECT owner, id FROM Users JOIN Orders AS O ON Users.id = owner WHERE owner = 'bob'"

    alias_map = {}

    for alias in parse_one(query).find_all(exp.Alias):
        table = alias.find(exp.Table).name
        table_alias = alias.find(exp.TableAlias).name
        alias_map[table_alias] = table

    def transformer(node):
        if isinstance(node, exp.Column) and node.table in alias_map.keys():
            return node.replace(exp.Column(this=exp.Identifier(this=node.name, quoted=False), table=''))
        return node

    transformed_tree = parse_one(query).transform(transformer)
    assert transformed_tree.sql() == expected


def test_sqlglot_find_all_aliases():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"

    result = repr(list(parse_one(query).find_all(exp.Alias)))

    assert result == """[(ALIAS this: \n  (TABLE this: \n    (IDENTIFIER this: Orders, quoted: False)), alias: \n  (TABLEALIAS this: \n    (IDENTIFIER this: O, quoted: False)))]"""


def test_sqlglot_insert_join():
    query = """SELECT U.email, UD.name, question, P.name,SUM(quantity) as total_quantity, wants_letter 
        from Users U 
        JOIN UserData UD on U.id = UD.user_id 
        JOIN NewsLetter NL on UD.id = NL.user_id 
        JOIN Orders O on U.id = O.owner 
        JOIN Products P on P.product_id = O.product 
        GROUP BY UD.name,P.name"""

    expected = (
        "SELECT U.email, UD.name, question, P.name, SUM(quantity) AS total_quantity, wants_letter "
        "FROM Users AS U "
        "JOIN UserData AS UD ON U.id = UD.user_id "
        "JOIN NewsLetter AS NL ON UD.id = NL.user_id "
        "JOIN Orders AS O ON U.id = O.owner "
        "JOIN Products AS P ON P.product_id = O.product "
        "JOIN RecoveryQuestions AS RQ ON U.id = RQ.user_id "
        "GROUP BY UD.name, P.name")

    result = parse_one(query).join("RecoveryQuestions", join_alias="RQ", on="U.id = RQ.user_id").sql()

    assert result == expected


def test_sqlglot_modify_join():
    query = """SELECT U.email, UD.name, question, P.name,SUM(quantity) as total_quantity, wants_letter 
        from Users U 
        JOIN UserData UD on U.id = UD.user_id 
        JOIN NewsLetter NL on UD.id = NL.user_id 
        GROUP BY UD.name,P.name"""

    expected = (
        "SELECT U.email, UD.name, question, P.name, SUM(quantity) AS total_quantity, wants_letter "
        "FROM Users AS U "
        "JOIN UserData AS UD ON U.id = UD.user_id "
        "JOIN OtherTable AS NL ON UD.id = NL.user_id "
        "GROUP BY UD.name, P.name")

    def transformer(node):
        if isinstance(node, exp.Table) and node.name == "NewsLetter":
            return parse_one("OtherTable")
        return node

    expression_tree = parse_one(query)
    result = expression_tree.transform(transformer).sql()

    assert result == expected
