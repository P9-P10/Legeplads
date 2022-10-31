from Structures.Structure import Structure

class TestStructure(Structure):
    def copy(self):
        new = TestStructure()
        new.value = self.value
        return new

def test_transform_returns_new_transformed_object():
    structure = TestStructure()
    structure.value = "ValueBefore"

    def transformation(structure):
        structure.value = "ValueAfter"

    new_structure = structure.transform(transformation)

    # Original should not be changed
    assert structure.value == "ValueBefore"
    # New instance should be changed
    assert new_structure.value == "ValueAfter"

def test_transform_ignores_return_value_of_transformation():
    structure = TestStructure()
    structure.value = "ValueBefore"

    def transformation(structure):
        return "SomeValue"

    new_structure = structure.transform(transformation)

    # No change to the old or the new structure
    assert structure.value == "ValueBefore"
    assert new_structure.value == "ValueBefore"