from steel.fields.numbers import Integer


class Structure:
    value = Integer(size=1)

    def __init__(self, value: int):
        # Just to give a way to optionally set an instance value
        if value > 0:
            self.value = value


class TestField:
    def test_descriptor_behavior(self):
        # Test that the descriptor returns itself when accessed on class
        assert isinstance(Structure.value, Integer)

        # Test that the descriptor returns itself when no instance value is set
        instance = Structure(0)
        assert isinstance(instance.value, Integer)

        # Test that the field does *not* get returned if an instance value is set
        instance = Structure(10)
        assert isinstance(instance.value, int)
