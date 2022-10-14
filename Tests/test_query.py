from Helpers.query import Query as Q


def test_get_query_type_update():
    query = Q("UPDATE Users SET Users.password = 'secure' WHERE Users.email =='test' ")
    assert query.get_query_type() == "UPDATE"


def test_get_query_type_delete():
    query = Q("DELETE FROM Users WHERE Users.email =='test' ")
    assert query.get_query_type() == "DELETE"


def test_get_where_clause():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")
    result = query.get_where_clause()
    assert result == " O.owner = 'bob'"


def test_get_query_type_select():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")
    assert query.get_query_type() == "SELECT"


def test_split_query_components():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")
    print(query.split_query_components())
    assert query.split_query_components() == ['SELECT', '*', 'FROM', 'Users', 'JOIN', 'Orders', 'O', 'on', 'Users.id',
                                              '=', 'O.owner', 'WHERE', 'O.owner', '=', "'bob'"]

def test_split_query_components_contains_newLine():
    query = Q("""SELECT * FROM Users JOIN Orders O on
    Users.id = O.owner WHERE O.owner = 'bob'""")
    print(query.split_query_components())
    assert query.split_query_components() == ['SELECT', '*', 'FROM', 'Users', 'JOIN', 'Orders', 'O', 'on', 'Users.id',
                                              '=', 'O.owner', 'WHERE', 'O.owner', '=', "'bob'"]

def test_split_query_components_contains_abnormal_amount_of_spaces():
    query = Q("""SELECT * FROM Users                                                 JOIN Orders O on
    Users.id = O.owner           
    WHERE               O.owner = 'bob'""")
    print(query.split_query_components())
    assert query.split_query_components() == ['SELECT', '*',
                                              'FROM',
                                              'Users',
                                              'JOIN',
                                              'Orders', 'O', 'on', 'Users.id',
                                              '=', 'O.owner', 'WHERE', 'O.owner', '=', "'bob'"]
