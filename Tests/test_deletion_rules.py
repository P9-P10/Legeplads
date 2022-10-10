import pytest

from Helpers.deletion_rules import DeletionRule as Dr


def test_deletion_rule_instantiation_raises_exception_with_too_many_arguments():
    with pytest.raises(Exception):
        Dr(True, True)


def test_deletion_query_set_to_null():
    deletion_rule = Dr(set_to_null=True)
    result_query = deletion_rule.deletion_query("Name", "someVariable", "x==y")
    assert result_query == "UPDATE Name SET someVariable=null WHERE x==y"


def test_deletion_query_set_to_custom():
    deletion_rule = Dr(set_to_custom=(True,"Custom"))
    result_query = deletion_rule.deletion_query("Name", "someVariable", "x==y")
    assert result_query == "UPDATE Name SET someVariable='Custom' WHERE x==y"
