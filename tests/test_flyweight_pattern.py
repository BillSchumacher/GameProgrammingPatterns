import unittest
from gpp.patterns.flyweight import FlyweightFactory


class TestFlyweightPattern(unittest.TestCase):
    def test_flyweight_factory_dict_keys(self):
        """
        Tests the flyweight factory with dictionary-based intrinsic states.
        """
        factory = FlyweightFactory(
            {
                "ColorRed": {"color": "Red"},  # Changed initial key for clarity
                "TextureWood": {"texture": "Wood"},
                "ShapeCircle": {"shape": "Circle"},
            }
        )

        factory.list_flyweights()

        # Client requests a flyweight with a given intrinsic state
        flyweight1 = factory.get_flyweight({"color": "Red"})
        flyweight1.operation("ExtrinsicState1_Dict")

        # Client requests another flyweight with a different intrinsic state
        flyweight2 = factory.get_flyweight({"color": "Blue"})
        flyweight2.operation("ExtrinsicState2_Dict")

        # Client requests a flyweight with an existing intrinsic state
        flyweight3 = factory.get_flyweight({"color": "Red"})
        flyweight3.operation("ExtrinsicState3_Dict")

        self.assertIs(
            flyweight1,
            flyweight3,
            "Flyweight1 and Flyweight3 (dict keys) should be the same object",
        )
        self.assertIsNot(
            flyweight1,
            flyweight2,
            "Flyweight1 and Flyweight2 (dict keys) should be different objects",
        )

        factory.list_flyweights()

    def test_flyweight_factory_tuple_keys(self):
        """
        Tests the flyweight factory with tuple-based intrinsic states.
        """
        factory = FlyweightFactory(
            {
                "Position1": (10, 20),
                "Position2": (30, 40, 50),
            }
        )
        factory.list_flyweights()

        # Request a flyweight with a tuple state
        flyweight_pos1 = factory.get_flyweight((10, 20))
        flyweight_pos1.operation("ExtrinsicState_Tuple1")

        # Request another flyweight with a different tuple state
        flyweight_pos2 = factory.get_flyweight((10, 21))
        flyweight_pos2.operation("ExtrinsicState_Tuple2")

        # Request the first tuple state again, should be the same object
        flyweight_pos3 = factory.get_flyweight((10, 20))
        flyweight_pos3.operation("ExtrinsicState_Tuple3")

        self.assertIs(
            flyweight_pos1,
            flyweight_pos3,
            "Flyweight_pos1 and Flyweight_pos3 (tuple keys) should be the same object",
        )
        self.assertIsNot(
            flyweight_pos1,
            flyweight_pos2,
            "Flyweight_pos1 and Flyweight_pos2 (tuple keys) should be different objects",
        )

        # Test with a 3D coordinate tuple, initially in factory
        flyweight_pos4 = factory.get_flyweight((30, 40, 50))
        flyweight_pos4.operation("ExtrinsicState_Tuple4")

        # Test with a new 3D coordinate tuple
        flyweight_pos5 = factory.get_flyweight((30, 40, 51))
        flyweight_pos5.operation("ExtrinsicState_Tuple5")

        initial_pos2_flyweight = factory.get_flyweight(
            (30, 40, 50)
        )  # Should be same as flyweight_pos4
        self.assertIs(
            flyweight_pos4,
            initial_pos2_flyweight,
            "Flyweight_pos4 and initial_pos2_flyweight should be the same",
        )

        factory.list_flyweights()

    def test_flyweight_factory_string_keys(self):
        """
        Tests the flyweight factory with simple string intrinsic states.
        """
        factory = FlyweightFactory(
            {
                "Name1": "SimpleName",
                "Name2": "AnotherName",
            }
        )
        factory.list_flyweights()

        flyweight_str1 = factory.get_flyweight("SimpleName")
        flyweight_str1.operation("ExtrinsicState_Str1")

        flyweight_str2 = factory.get_flyweight("NewName")
        flyweight_str2.operation("ExtrinsicState_Str2")

        flyweight_str3 = factory.get_flyweight("SimpleName")
        flyweight_str3.operation("ExtrinsicState_Str3")

        self.assertIs(
            flyweight_str1,
            flyweight_str3,
            "String flyweights should be the same object",
        )
        self.assertIsNot(
            flyweight_str1,
            flyweight_str2,
            "String flyweights should be different objects",
        )
        factory.list_flyweights()


if __name__ == "__main__":
    unittest.main()
