from abc import ABC, abstractmethod

class Service(ABC):
    @abstractmethod
    def execute(self):
        pass

class ServiceLocator:
    _services = {}

    @classmethod
    def register_service(cls, name: str, service: Service):
        cls._services[name] = service

    @classmethod
    def get_service(cls, name: str) -> Service:
        service = cls._services.get(name)
        if not service:
            raise ValueError(f"Service {name} not found.")
        return service

    @classmethod
    def clear_services(cls):
        # Helper method for testing to reset state
        cls._services = {}

# Optional: A Null Service for cases where a service might be optional
class NullService(Service):
    def execute(self):
        return "Executing NullService (default)"

# Global access point for convenience, though direct use of ServiceLocator is also fine
def get_service(name: str) -> Service:
    return ServiceLocator.get_service(name)

def register_service(name: str, service: Service):
    ServiceLocator.register_service(name, service)
