from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column

def test_table_comparison_fails_if_other_is_not_table():
    assert not Table("name") == ["name"] 

def test_table_comparison_succeeds_on_same_table_without_column():
    table1 = Table("name")
    table2 = Table("name")
    
    assert table1 == table2

def test_table_comparison_succeeds_on_same_table_with_same_columns():
    table1 = Table("name", [Column("col1"), Column("col2")])
    table2 = Table("name", [Column("col1"), Column("col2")])
    
    assert table1 == table2

def test_table_comparison_fails_on_table_with_different_name():
    table1 = Table("name")
    table2 = Table("other_name")
    
    assert not table1 == table2

def test_table_comparison_fails_on_table_with_different_columns():
    table1 = Table("name", [Column("col1"), Column("col2")])
    table2 = Table("name", [Column("col1"), Column("other_col2")])
    
    assert not table1 == table2

def test_table_comparison_succeeds_on_same_columns_in_different_order():
    table1 = Table("name", [Column("col1"), Column("col2")])
    table2 = Table("name", [Column("col2"), Column("col1")])
    
    assert table1 == table2

def test_table_has_column():
    table = Table("name", [Column("col1"), Column("col2")])
    assert table.has_column(Column("col1"))
    assert table.has_column(Column("col2"))
    assert not table.has_column(Column("col3"))
    assert not table.has_column(Column("no_such_column"))
