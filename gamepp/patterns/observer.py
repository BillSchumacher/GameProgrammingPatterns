from abc import ABC, abstractmethod
from typing import List, Any


class ObserverMixin(ABC):
    """
    Mixin class for Observers. Classes that want to observe subjects
    can inherit from this mixin and must implement on_notify.

    It's important to note that this mixin does not enforce any cleanup
    or detachment logic. Observers should manage their own lifecycle.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, **kwargs
        )  # Call super() to cooperate with other bases/mixins
        self.subjects: List["Subject"] = []

    @abstractmethod
    def on_notify(self, subject: Any, event_data: Any = None) -> None:
        """
        Called by the Subject when an event occurs.
        'subject' is the instance of the Subject that notified this observer.
        'event_data' is any data passed by the subject regarding the event.
        """
        pass

    def attached(self, subject: "Subject") -> None:
        """
        Attach this observer to a subject.
        This method is optional and can be overridden by subclasses.
        """
        if subject not in self.subjects:
            self.subjects.append(subject)

    def detached(self, subject: "Subject") -> None:
        """
        Detach this observer from a subject.
        This method is optional and can be overridden by subclasses.
        """
        if subject in self.subjects:
            self.subjects.remove(subject)


class ObserverNode:
    """
    A node in a singly linked list to manage observers.
    """

    def __init__(self, observer: ObserverMixin):
        self.observer = observer
        self.next: "ObserverNode" = None  # Type hint for the next node
        self.prev: "ObserverNode" = None


class Subject:
    """
    The Subject class manages a list of observers and notifies them of changes.
    """

    def __init__(self):
        self._observers: List[ObserverMixin] = []

    def attach(self, observer: ObserverMixin) -> None:
        """Attach an observer to the subject."""
        if observer not in self._observers:
            self._observers.append(observer)
            observer.attached(self)

    def detach(self, observer: ObserverMixin) -> None:
        """Detach an observer from the subject."""
        try:
            self._observers.remove(observer)
            observer.detached(self)
        except ValueError:
            pass  # Observer not found, do nothing

    def notify(self, event_data: Any = None) -> None:
        """
        Notify all attached observers about an event.
        Iterates over a copy of the observer list in case
        observers detach themselves during notification.
        """
        for observer in list(self._observers):
            observer.on_notify(self, event_data)


class LinkedSubject(Subject):
    """
    A subject that uses a linked list to manage observers.

    This avoid the overhead of list operations and allows for
    more efficient insertion and deletion of observers.

    This is particularly useful if observers are frequently
    added and removed.
    """

    def __init__(self):
        super().__init__()
        self._head: ObserverNode = None
        self._tail: ObserverNode = None

    def attach(self, observer: ObserverMixin) -> None:
        """Attach an observer to the subject."""
        new_node = ObserverNode(observer)
        if not self._head:
            self._head = new_node
            self._tail = new_node
        else:
            self._tail.next = new_node
            new_node.prev = self._tail
            self._tail = new_node
        observer.attached(self)

    def detach(self, observer: ObserverMixin) -> None:
        """Detach an observer from the subject."""
        current = self._head
        while current:
            if current.observer == observer:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self._head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self._tail = current.prev
                observer.detached(self)
                return
            current = current.next

    def notify(self, event_data: Any = None) -> None:
        """
        Notify all attached observers about an event.
        Iterates over a copy of the observer list in case
        observers detach themselves during notification.
        """
        current = self._head
        while current:
            current.observer.on_notify(self, event_data)
            current = current.next
