import unittest
from gamepp.patterns.event_queue import Event, EventQueue, global_event_queue


class TestEvent(unittest.TestCase):
    def test_event_creation_and_repr(self):
        event = Event("test_event", key1="value1", key2=123)
        self.assertEqual(event.type, "test_event")
        self.assertEqual(event.payload, {"key1": "value1", "key2": 123})
        self.assertEqual(
            repr(event),
            "Event(type='test_event', payload={'key1': 'value1', 'key2': 123})",
        )


class TestEventQueue(unittest.TestCase):
    def setUp(self):
        # Ensure the global_event_queue is clean before each test
        # This is a bit tricky with singletons if tests run in parallel or affect each other.
        # For robust testing, it might be better to allow creating fresh instances for tests,
        # or provide a reset method on the singleton.
        # For now, we'll try to clear its internal queue.
        while global_event_queue.get_event() is not None:
            pass  # Clear out any existing events

    def tearDown(self):
        # Clean up after tests if necessary
        while global_event_queue.get_event() is not None:
            pass

    def test_singleton_instance(self):
        eq1 = EventQueue()
        eq2 = EventQueue()
        self.assertIs(eq1, eq2, "EventQueue should be a singleton.")
        self.assertIs(
            eq1, global_event_queue, "Global instance should be the same singleton."
        )

    def test_queue_and_get_event(self):
        self.assertFalse(
            global_event_queue.has_events(), "Queue should be initially empty."
        )

        global_event_queue.queue_event("event1", data="foo")
        self.assertTrue(
            global_event_queue.has_events(), "Queue should have an event after queuing."
        )

        event = global_event_queue.get_event()
        self.assertIsNotNone(event, "Should get an event from the queue.")
        self.assertEqual(event.type, "event1")
        self.assertEqual(event.payload, {"data": "foo"})
        self.assertFalse(
            global_event_queue.has_events(),
            "Queue should be empty after getting the event.",
        )

        self.assertIsNone(
            global_event_queue.get_event(),
            "Getting from empty queue should return None.",
        )

    def test_fifo_order(self):
        global_event_queue.queue_event("event_A", id=1)
        global_event_queue.queue_event("event_B", id=2)
        global_event_queue.queue_event("event_C", id=3)

        event1 = global_event_queue.get_event()
        self.assertEqual(event1.type, "event_A")
        self.assertEqual(event1.payload["id"], 1)

        event2 = global_event_queue.get_event()
        self.assertEqual(event2.type, "event_B")
        self.assertEqual(event2.payload["id"], 2)

        event3 = global_event_queue.get_event()
        self.assertEqual(event3.type, "event_C")
        self.assertEqual(event3.payload["id"], 3)

        self.assertIsNone(global_event_queue.get_event())

    def test_peek_event(self):
        self.assertIsNone(
            global_event_queue.peek_event(),
            "Peeking an empty queue should return None.",
        )

        global_event_queue.queue_event("peek_event_1", detail="first")
        self.assertTrue(global_event_queue.has_events())

        event = global_event_queue.peek_event()
        self.assertIsNotNone(event)
        self.assertEqual(event.type, "peek_event_1")
        self.assertEqual(event.payload["detail"], "first")

        # Ensure peek doesn't remove the event
        self.assertTrue(
            global_event_queue.has_events(),
            "Queue should still have event after peeking.",
        )
        event_after_peek = global_event_queue.get_event()
        self.assertIs(
            event,
            event_after_peek,
            "Event retrieved by get should be the same as peeked.",
        )

        self.assertFalse(
            global_event_queue.has_events(),
            "Queue should be empty after getting the peeked event.",
        )
        self.assertIsNone(
            global_event_queue.peek_event(),
            "Peeking an empty queue should return None again.",
        )

    def test_has_events(self):
        self.assertFalse(global_event_queue.has_events())
        global_event_queue.queue_event("some_event")
        self.assertTrue(global_event_queue.has_events())
        global_event_queue.get_event()
        self.assertFalse(global_event_queue.has_events())


if __name__ == "__main__":
    unittest.main()
