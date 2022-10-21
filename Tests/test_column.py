from Applications.DatabaseRepresenations.Column import Column

def test_column_comparison_fails_if_other_is_not_column():
    assert not Column("name") == ["name"] 

def test_column_comparison_succeeds_on_same_column_names():
    column1 = Column("name")
    column2 = Column("name")
    
    assert column1 == column2

def test_column_comparison_fails_on_different_column_names():
    column1 = Column("name")
    column2 = Column("other_name")

    assert not column1 == column2

