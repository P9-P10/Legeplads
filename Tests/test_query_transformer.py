from Applications.query_transformer import transform
from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
from Helpers.Change import Change
from Helpers.equality_constraint import EqualityConstraint




def test_transform_changes_occurrences_of_table():
    actual = Query("SELECT col1 FROM testTable JOIN other_table")
    expected = Query("SELECT col1 FROM testTable as testTable1 JOIN correct_table as other_table1")

    changes = [Change((Table('other_table'), Column('col1')), (Table('correct_table'), Column('col1')))]
    transform(actual, changes, [], [])

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
    transform(actual, [], [], tables)
    assert actual == expected


def test_transform_fully_qualifies_known_column_names():
    actual = Query("SELECT name FROM UserData")

    expected = Query("SELECT UserData1.name FROM UserData AS UserData1")
    transform(actual, [], [], [Table("UserData", [Column("name")])])

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
    transform(actual, [], [], tables)

    assert actual == expected


def test_transform_joins():

    actual = Query("SELECT col2, col3, col6 FROM T3 JOIN T1 on T1.col1 = T3.col5")

    expected = Query("SELECT T11.col2,T31.col3,T31.col6 FROM T3 AS T31 JOIN T2 AS T11 on T11.col4 = T31.col5")
    t1 = Table("T1", [Column("col1"), Column("col2"), Column("col3")])
    t2 = Table("T2", [Column("col4"), Column("col2")])
    t3 = Table("T3", [Column("col5"), Column("col3"), Column("col6")])
    equality_constraint = EqualityConstraint(t1, Column("col1"), t2, Column("col4"))

    new_tables = [t2, t3]
    changes = [Change((t1, Column("col2")), (t2, Column("col2")),
                      constraint=equality_constraint),
               Change((t1, Column("col3")), (t3, Column("col3")))]
    old_tables = [t1, t3]
    transform(actual, changes, old_tables, new_tables)

    assert actual == expected
