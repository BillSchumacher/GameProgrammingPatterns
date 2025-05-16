import unittest
from gpp.patterns.service_locator import (
    Service,
    ServiceLocator,
    NullService,
    get_service,
    register_service,
)


class ConcreteServiceA(Service):
    def execute(self):
        return "Executing ConcreteServiceA"


class ConcreteServiceB(Service):
    def execute(self):
        return "Executing ConcreteServiceB"

  
class TestServiceLocator(unittest.TestCase):
    def setUp(self):
        # Ensure a clean state for each test
        ServiceLocator.clear_services()

    def test_register_and_get_service(self):
        service_a = ConcreteServiceA()
        ServiceLocator.register_service("ServiceA", service_a)

        retrieved_service = ServiceLocator.get_service("ServiceA")
        self.assertIs(retrieved_service, service_a)
        self.assertEqual(retrieved_service.execute(), "Executing ConcreteServiceA")

    def test_get_unregistered_service(self):
        with self.assertRaises(ValueError) as context:
            ServiceLocator.get_service("NonExistentService")
        self.assertTrue("Service NonExistentService not found." in str(context.exception))

    def test_multiple_services(self):
        service_a = ConcreteServiceA()
        service_b = ConcreteServiceB()
        ServiceLocator.register_service("ServiceA", service_a)
        ServiceLocator.register_service("ServiceB", service_b)

        self.assertEqual(ServiceLocator.get_service("ServiceA").execute(), "Executing ConcreteServiceA")
        self.assertEqual(ServiceLocator.get_service("ServiceB").execute(), "Executing ConcreteServiceB")

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
        service_b = ConcreteServiceB()
        register_service("GlobalServiceB", service_b) # Using global helper

        retrieved_service = get_service("GlobalServiceB") # Using global helper
        self.assertIs(retrieved_service, service_b)
        self.assertEqual(retrieved_service.execute(), "Executing ConcreteServiceB")

    def test_clear_services(self):
        service_a = ConcreteServiceA()
        ServiceLocator.register_service("ServiceA", service_a)
        self.assertIsNotNone(ServiceLocator.get_service("ServiceA"))

        ServiceLocator.clear_services()
        with self.assertRaises(ValueError):
            ServiceLocator.get_service("ServiceA")

if __name__ == '__main__':
    unittest.main()
