from Applications.query_transformer import transform
from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
from Helpers.Change import Change

def test_transform_does_nothing_when_no_changes_are_required():
    actual = Query("SELECT * FROM testTable JOIN other_table")
    expected = Query("SELECT * FROM testTable JOIN other_table")

    transform(Query("SELECT * FROM testTable JOIN other_table"), [], [])

    assert actual == expected

def test_transform_does_nothing_when_no_changes_are_required_multiple_joins_on_same_table():
    actual = Query("SELECT NL.user_id, UD.user_id "
                   "FROM Users "
                   "JOIN UserData AS UD ON Users.id= UD.user_id "
                   "JOIN main.UserData NL ON UD.id = NL.user_id")

    expected = Query("SELECT NL.user_id, UD.user_id "
                     "FROM Users "
                     "JOIN UserData AS UD ON Users.id= UD.user_id "
                     "JOIN main.UserData AS NL ON UD.id = NL.user_id")

    transform(actual, [], [])
    assert actual == expected

def test_transform_changes_occurrences_of_table():
    actual = Query("SELECT col1 FROM testTable JOIN other_table")
    expected = Query("SELECT col1 FROM testTable JOIN correct_table")

    changes = [Change((Table('other_table'), Column('col1')), (Table('correct_table'), Column('col1')))]
    transform(actual, changes, [])

    assert actual == expected

def test_apply_changes_adds_aliases():
    actual = Query(
        "SELECT U.email, UD.name, question, P.name,SUM(quantity) as total_quantity, wants_letter "
        "from Users U "
        "JOIN UserData UD on U.id = UD.user_id "
        "JOIN NewsLetter NL on UD.id = NL.user_id "
        "JOIN Orders O on U.id = O.owner "
        "JOIN Products P on P.product_id = O.product "
        "JOIN RecoveryQuestions RQ on U.id = RQ.user_id "
        "GROUP BY UD.name,P.name")

    expected = Query(
        "SELECT U.email, UD.name, RQ.question, P.name,SUM(O.quantity) as total_quantity, NL.wants_letter "
        "from Users U "
        "JOIN UserData UD on U.id = UD.user_id "
        "JOIN NewsLetter NL on UD.id = NL.user_id "
        "JOIN Orders O on U.id = O.owner "
        "JOIN Products P on P.product_id = O.product "
        "JOIN RecoveryQuestions RQ on U.id = RQ.user_id "
        "GROUP BY UD.name,P.name")

    news_letter = Table("NewsLetter", [Column("wants_letter")])
    orders = Table("Orders", [Column("quantity")])
    recovery_questions = Table("RecoveryQuestions", [Column("question")])
    tables = [news_letter, orders, recovery_questions]
    transform(actual, [], tables)
    assert actual == expected

def test_transform_fully_qualifies_known_column_names():
    actual = Query("SELECT name FROM UserData")

    expected = Query("SELECT UserData1.name FROM UserData AS UserData1")
    transform(actual, [], [Table("UserData", [Column("name")])])

    assert actual == expected

def test_fully_qualify_column_names_creates_aliases_for_multiple_tables():
    actual = Query("SELECT name "
                   "FROM UserData "
                   "JOIN RecoveryQuestions on UserData.user_id = RecoveryQuestions.user_id")

    expected = Query("SELECT UserData1.name "
                     "FROM UserData AS UserData1 "
                     "JOIN RecoveryQuestions as RecoveryQuestions1 on UserData1.user_id = RecoveryQuestions1.user_id")

    userdata = Table("UserData", [Column("name")])
    recovery_questions = Table("RecoveryQuestions", [Column("question")])
    tables = [userdata, recovery_questions]
    transform(actual, [], tables)

    assert actual == expected
