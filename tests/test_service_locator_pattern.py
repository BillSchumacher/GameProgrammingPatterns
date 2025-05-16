import unittest
from gamepp.patterns.service_locator import (
    ServiceLocator,
    NullService,
    get_service,
    register_service,
)

# Example Services for Testing

class SingletonService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonService, cls).__new__(cls)
            # Initialize any attributes here
            cls._instance.data = "Singleton Data"
        return cls._instance

    def get_data(self):
        return self.data

    def set_data(self, value):
        self.data = value

class StaticUtilService:
    @staticmethod
    def perform_action(input_val):
        return f"Static action performed with {input_val}"

    @classmethod
    def get_info(cls):
        return "Information from StaticUtilService class"

# Concrete services (can be instances or classes with static methods)
class ConcreteServiceA:
    def execute(self):
        return "Executing ConcreteServiceA"

class ConcreteServiceB:
    def execute(self):
        return "Executing ConcreteServiceB"


class TestServiceLocator(unittest.TestCase):
    def setUp(self):
        ServiceLocator.clear_services()

    def test_register_and_get_instance_service(self):
        service_a_instance = ConcreteServiceA()
        ServiceLocator.register_service("ServiceA", service_a_instance)

        retrieved_service = ServiceLocator.get_service("ServiceA")
        self.assertIs(retrieved_service, service_a_instance)
        self.assertEqual(retrieved_service.execute(), "Executing ConcreteServiceA")

    def test_register_and_get_singleton_service(self):
        # Register the singleton instance
        singleton_instance = SingletonService()
        ServiceLocator.register_service("MySingleton", singleton_instance)

        # Retrieve it multiple times, should be the same instance
        s1 = ServiceLocator.get_service("MySingleton")
        s2 = ServiceLocator.get_service("MySingleton")
        self.assertIs(s1, s2)
        self.assertIs(s1, singleton_instance)
        self.assertEqual(s1.get_data(), "Singleton Data")

        s1.set_data("New Singleton Data")
        self.assertEqual(s2.get_data(), "New Singleton Data")

    def test_register_and_get_static_service_class(self):
        # Register the class itself
        ServiceLocator.register_service("MyStaticUtil", StaticUtilService)

        retrieved_util_class = ServiceLocator.get_service("MyStaticUtil")
        self.assertIs(retrieved_util_class, StaticUtilService)
        self.assertEqual(retrieved_util_class.perform_action("test"), "Static action performed with test")
        self.assertEqual(retrieved_util_class.get_info(), "Information from StaticUtilService class")

    def test_get_unregistered_service(self):
        with self.assertRaises(ValueError) as context:
            ServiceLocator.get_service("NonExistentService")
        self.assertTrue("Service NonExistentService not found." in str(context.exception))

    def test_multiple_services(self):
        service_a = ConcreteServiceA()
        service_b = ConcreteServiceB()
        singleton_s = SingletonService()
        ServiceLocator.register_service("ServiceA", service_a)
        ServiceLocator.register_service("ServiceB", service_b)
        ServiceLocator.register_service("SingletonS", singleton_s)
        ServiceLocator.register_service("StaticUtil", StaticUtilService)

        self.assertEqual(ServiceLocator.get_service("ServiceA").execute(), "Executing ConcreteServiceA")
        self.assertEqual(ServiceLocator.get_service("ServiceB").execute(), "Executing ConcreteServiceB")
        self.assertEqual(ServiceLocator.get_service("SingletonS").get_data(), "Singleton Data")
        self.assertEqual(ServiceLocator.get_service("StaticUtil").perform_action("multi"), "Static action performed with multi")

    def test_replace_service(self):
        service_a1 = ConcreteServiceA()
        ServiceLocator.register_service("ServiceA", service_a1)
        self.assertEqual(ServiceLocator.get_service("ServiceA").execute(), "Executing ConcreteServiceA")

        service_a2 = ConcreteServiceA() # A different instance
        ServiceLocator.register_service("ServiceA", service_a2)
        retrieved_service = ServiceLocator.get_service("ServiceA")
        self.assertIs(retrieved_service, service_a2)
        self.assertIsNot(retrieved_service, service_a1)

    def test_null_service_pattern(self):
        null_service = NullService()
        ServiceLocator.register_service("OptionalService", null_service)
        
        retrieved_service = ServiceLocator.get_service("OptionalService")
        self.assertEqual(retrieved_service.execute(), "Executing NullService (default)")

        # Attempt to get a service that isn't registered, even with a null service available for others
        with self.assertRaises(ValueError):
            ServiceLocator.get_service("AnotherService")

    def test_global_access_functions(self):
        service_b_instance = ConcreteServiceB()
        register_service("GlobalServiceB", service_b_instance) # Using global helper

        retrieved_service = get_service("GlobalServiceB") # Using global helper
        self.assertIs(retrieved_service, service_b_instance)
        self.assertEqual(retrieved_service.execute(), "Executing ConcreteServiceB")

        # Test with a static service class via global functions
        register_service("GlobalStaticUtil", StaticUtilService)
        retrieved_static_class = get_service("GlobalStaticUtil")
        self.assertIs(retrieved_static_class, StaticUtilService)
        self.assertEqual(retrieved_static_class.get_info(), "Information from StaticUtilService class")

    def test_clear_services(self):
        service_a = ConcreteServiceA()
        ServiceLocator.register_service("ServiceA", service_a)
        self.assertIsNotNone(ServiceLocator.get_service("ServiceA"))

        ServiceLocator.clear_services()
        with self.assertRaises(ValueError):
            ServiceLocator.get_service("ServiceA")

if __name__ == '__main__':
    unittest.main()
