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


def test_current_returns_first_element_of_query():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert query.current() == "SELECT"


def test_current_returns_empty_string_with_empty_query():
    query = Q("")

    assert query.current() == ""


def test_current_is_idempotent():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    first_current_value = query.current()
    assert query.current() == first_current_value
    assert query.current() == first_current_value
    assert query.current() == first_current_value


def test_current_stays_at_last_value():
    query = Q("SELECT * FROM")

    assert query.current() == "SELECT"
    query.next()
    assert query.current() == "*"
    query.next()
    assert query.current() == "FROM"
    query.next()
    assert query.current() == "FROM"


def test_peek_returns_next_value_by_default():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert query.peek() == "*"


def test_peek_returns_value_at_given_position_relative_to_current():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert query.peek(3) == "Users"
    assert query.peek(11) == "WHERE"


def test_peek_does_not_change_value_of_current():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert query.current() == "SELECT"
    query.peek()
    assert query.current() == "SELECT"


def test_peek_is_idempotent():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    first_peek_value = query.peek()
    assert query.peek() == first_peek_value
    assert query.peek(2) == "FROM"
    assert query.peek() == first_peek_value
    assert query.peek(89) == None
    assert query.peek() == first_peek_value


def test_peek_is_idempotent():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    first_peek_value = query.peek()
    assert query.peek() == first_peek_value
    assert query.peek() == first_peek_value
    assert query.peek() == first_peek_value


def test_peek_returns_None_with_empty_query():
    query = Q("")

    assert query.peek() == None


def test_peek_returns_None_when_current_is_last_element():
    query = Q("SELECT * FROM")
    query.next()
    query.next()
    assert query.current() == "FROM"
    assert query.peek() == None


def test_next_returns_next_value_by_default():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert query.next() == "*"


def test_next_returns_value_at_given_position_relative_to_current():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert query.next(2) == "FROM"
    assert query.next(2) == "JOIN"
    assert query.next(7) == "WHERE"


def test_next_returns_None_when_current_is_last_element():
    query = Q("SELECT * FROM")
    query.next()
    query.next()
    assert query.current() == "FROM"
    assert query.next() is None


def test_next_called_after_peek_returns_same_value():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert query.peek() == query.next()


def test_peek_called_after_next_returns_different_value():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert not query.next() == query.peek()


def test_next_changes_current_to_value_returned_by_peek():
    query = Q("SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'")

    assert query.current() == "SELECT"

    second_value_peek = query.peek()
    second_value_from_next = query.next()
    second_value = query.current()

    assert second_value_from_next == second_value_peek
    assert second_value == second_value_from_next
