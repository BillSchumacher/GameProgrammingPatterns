import unittest
from gpp.patterns.observer import Subject, ObserverMixin, LinkedSubject
from typing import Any

# --- Concrete Subject Example ---
class GameEventManager(Subject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_event_name = None
        self._last_event_data = None

    def trigger_event(self, event_name: str, data: Any = None):
        print(f"\nGameEventManager: Event '{event_name}' triggered with data: {data}")
        self._last_event_name = event_name
        self._last_event_data = data
        self.notify({"event_name": event_name, "details": data})

    @property
    def last_event_name(self):
        return self._last_event_name

# --- Concrete Observer Examples using the Mixin ---
class AchievementSystem(ObserverMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.achievements_unlocked = []
        self.notifications_received = 0

    def on_notify(self, subject: Any, event_data: Any = None) -> None:
        self.notifications_received += 1
        event_name = event_data.get("event_name")
        details = event_data.get("details", {})
        print(f"AchievementSystem: Notified by {subject.__class__.__name__} about event: {event_name}, details: {details}")
        if event_name == "ENEMY_DEFEATED" and details.get("enemy_type") == "BOSS":
            achievement = "BOSS_SLAYER"
            if achievement not in self.achievements_unlocked:
                self.achievements_unlocked.append(achievement)
                print(f"AchievementSystem: Unlocked '{achievement}'!")

class SoundSystem(ObserverMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_sound_played = None
        self.notifications_received = 0

    def on_notify(self, subject: Any, event_data: Any = None) -> None:
        self.notifications_received += 1
        event_name = event_data.get("event_name")
        print(f"SoundSystem: Notified by {subject.__class__.__name__} about event: {event_name}")
        if event_name == "PLAYER_JUMP":
            self.last_sound_played = "JUMP_SOUND"
            print(f"SoundSystem: Playing {self.last_sound_played}")
        elif event_name == "ENEMY_DEFEATED":
            self.last_sound_played = "VICTORY_STINGER"
            print(f"SoundSystem: Playing {self.last_sound_played}")

# --- Helper Observer for specific tests ---
class TestObserver(ObserverMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.received_subject: Any = None
        self.received_data: Any = None
        self.notification_count = 0
        self.attached_to_subject_calls = 0
        self.detached_from_subject_calls = 0
        self.last_attached_subject: Any = None
        self.last_detached_subject: Any = None

    def on_notify(self, subject: Any, event_data: Any = None) -> None:
        self.received_subject = subject
        self.received_data = event_data
        self.notification_count += 1
        print(f"TestObserver: Notified by {subject.__class__.__name__} with data: {event_data}")

    def attached(self, subject: Subject) -> None:
        super().attached(subject)
        self.attached_to_subject_calls += 1
        self.last_attached_subject = subject
        print(f"TestObserver: Attached to {subject.__class__.__name__}. Total subjects: {len(self.subjects)}")

    def detached(self, subject: Subject) -> None:
        super().detached(subject)
        self.detached_from_subject_calls += 1
        self.last_detached_subject = subject
        print(f"TestObserver: Detached from {subject.__class__.__name__}. Total subjects: {len(self.subjects)}")

# --- Unit Tests ---
class TestObserverPattern(unittest.TestCase):
    def setUp(self):
        self.event_manager = GameEventManager()
        self.achievements = AchievementSystem()
        self.sounds = SoundSystem()
        self.test_observer = TestObserver()

    def test_attach_and_notify(self):
        self.event_manager.attach(self.achievements)
        self.event_manager.attach(self.sounds)
        self.event_manager.attach(self.test_observer)

        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        self.assertIn(self.event_manager, self.test_observer.subjects)

        self.event_manager.trigger_event("PLAYER_JUMP", {"height": 10})
        self.assertEqual(self.achievements.notifications_received, 1)
        self.assertEqual(self.sounds.notifications_received, 1)
        self.assertEqual(self.sounds.last_sound_played, "JUMP_SOUND")
        self.assertEqual(self.test_observer.notification_count, 1)

        self.event_manager.trigger_event("ENEMY_DEFEATED", {"enemy_type": "GRUNT"})
        self.assertEqual(self.achievements.notifications_received, 2)
        self.assertNotIn("BOSS_SLAYER", self.achievements.achievements_unlocked)
        self.assertEqual(self.sounds.notifications_received, 2)
        self.assertEqual(self.sounds.last_sound_played, "VICTORY_STINGER")
        self.assertEqual(self.test_observer.notification_count, 2)

    def test_boss_slayer_achievement(self):
        self.event_manager.attach(self.achievements)
        self.event_manager.attach(self.test_observer)
        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        self.assertIn(self.event_manager, self.test_observer.subjects)

        self.event_manager.trigger_event("ENEMY_DEFEATED", {"enemy_type": "BOSS"})
        self.assertIn("BOSS_SLAYER", self.achievements.achievements_unlocked)
        self.assertEqual(self.test_observer.notification_count, 1)

    def test_detach_observer(self):
        self.event_manager.attach(self.sounds)
        self.event_manager.attach(self.test_observer)
        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        self.assertIn(self.event_manager, self.test_observer.subjects)
        self.assertEqual(len(self.test_observer.subjects), 1)

        self.event_manager.trigger_event("PLAYER_JUMP")
        self.assertEqual(self.sounds.notifications_received, 1)
        self.assertEqual(self.test_observer.notification_count, 1)

        self.event_manager.detach(self.sounds)
        self.event_manager.detach(self.test_observer)
        self.assertEqual(self.test_observer.detached_from_subject_calls, 1)
        self.assertNotIn(self.event_manager, self.test_observer.subjects)
        self.assertEqual(len(self.test_observer.subjects), 0)

        self.event_manager.trigger_event("PLAYER_JUMP")
        self.assertEqual(self.sounds.notifications_received, 1)
        self.assertEqual(self.test_observer.notification_count, 1)

    def test_notify_no_observers(self):
        try:
            self.event_manager.trigger_event("TEST_EVENT_NO_OBSERVERS")
        except Exception as e:
            self.fail(f"Notifying with no observers raised an exception: {e}")

    def test_observer_receives_correct_data_and_subject(self):
        self.event_manager.attach(self.test_observer)
        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        self.assertIn(self.event_manager, self.test_observer.subjects)

        event_payload = {"key": "value", "number": 123}
        self.event_manager.trigger_event("DATA_CHECK_EVENT", event_payload)

        self.assertEqual(self.test_observer.notification_count, 1)
        self.assertIs(self.test_observer.received_subject, self.event_manager)
        self.assertIsNotNone(self.test_observer.received_data)
        self.assertEqual(self.test_observer.received_data.get("event_name"), "DATA_CHECK_EVENT")
        self.assertEqual(self.test_observer.received_data.get("details"), event_payload)

    def test_attach_same_observer_multiple_times(self):
        self.event_manager.attach(self.test_observer)
        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        initial_subjects_count = len(self.test_observer.subjects)

        self.event_manager.attach(self.test_observer)
        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        self.assertEqual(len(self.test_observer.subjects), initial_subjects_count)

        self.event_manager.trigger_event("SINGLE_NOTIFICATION_TEST")
        self.assertEqual(self.test_observer.notification_count, 1)

    def test_detach_non_attached_observer(self):
        initial_detached_calls = self.test_observer.detached_from_subject_calls
        initial_subjects_count = len(self.test_observer.subjects)
        try:
            self.event_manager.detach(self.test_observer)
            self.assertEqual(self.test_observer.detached_from_subject_calls, initial_detached_calls)
            self.assertEqual(len(self.test_observer.subjects), initial_subjects_count)
        except Exception as e:
            self.fail(f"Detaching a non-attached observer raised an exception: {e}")

# --- Concrete Subject Example for LinkedSubject ---
class GameEventManagerLinked(LinkedSubject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_event_name = None
        self._last_event_data = None

    def trigger_event(self, event_name: str, data: Any = None):
        print(f"\nGameEventManagerLinked: Event '{event_name}' triggered with data: {data}")
        self._last_event_name = event_name
        self._last_event_data = data
        self.notify({"event_name": event_name, "details": data})

    @property
    def last_event_name(self):
        return self._last_event_name

# --- Unit Tests for LinkedSubject ---
class TestLinkedSubjectObserverPattern(unittest.TestCase):
    def setUp(self):
        self.event_manager = GameEventManagerLinked()
        self.achievements = AchievementSystem()
        self.sounds = SoundSystem()
        self.test_observer = TestObserver()

    def test_attach_and_notify_linked(self):
        self.event_manager.attach(self.achievements)
        self.event_manager.attach(self.sounds)
        self.event_manager.attach(self.test_observer)

        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        self.assertIn(self.event_manager, self.test_observer.subjects)

        self.event_manager.trigger_event("PLAYER_JUMP", {"height": 10})
        self.assertEqual(self.achievements.notifications_received, 1)
        self.assertEqual(self.sounds.notifications_received, 1)
        self.assertEqual(self.sounds.last_sound_played, "JUMP_SOUND")
        self.assertEqual(self.test_observer.notification_count, 1)

    def test_detach_observer_linked(self):
        self.event_manager.attach(self.test_observer)
        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        self.assertIn(self.event_manager, self.test_observer.subjects)

        self.event_manager.trigger_event("PRE_DETACH_LINKED")
        self.assertEqual(self.test_observer.notification_count, 1)

        self.event_manager.detach(self.test_observer)
        self.assertEqual(self.test_observer.detached_from_subject_calls, 1)
        self.assertNotIn(self.event_manager, self.test_observer.subjects)

        self.event_manager.trigger_event("POST_DETACH_LINKED")
        self.assertEqual(self.test_observer.notification_count, 1)

    def test_observer_receives_correct_data_and_subject_linked(self):
        self.event_manager.attach(self.test_observer)
        event_payload = {"link_key": "link_value"}
        self.event_manager.trigger_event("DATA_CHECK_LINKED", event_payload)

        self.assertEqual(self.test_observer.notification_count, 1)
        self.assertIs(self.test_observer.received_subject, self.event_manager)
        self.assertEqual(self.test_observer.received_data.get("event_name"), "DATA_CHECK_LINKED")
        self.assertEqual(self.test_observer.received_data.get("details"), event_payload)

    def test_attach_same_observer_multiple_times_linked(self):
        self.event_manager.attach(self.test_observer)
        self.assertEqual(self.test_observer.attached_to_subject_calls, 1)
        self.assertEqual(len(self.test_observer.subjects), 1)

        self.event_manager.attach(self.test_observer)
        self.assertEqual(self.test_observer.attached_to_subject_calls, 2)
        self.assertEqual(len(self.test_observer.subjects), 1)

        self.event_manager.trigger_event("MULTI_ATTACH_LINKED_TEST")
        self.assertEqual(self.test_observer.notification_count, 2)

    def test_detach_non_attached_observer_linked(self):
        initial_detached_calls = self.test_observer.detached_from_subject_calls
        try:
            self.event_manager.detach(self.test_observer)
            self.assertEqual(self.test_observer.detached_from_subject_calls, initial_detached_calls)
        except Exception as e:
            self.fail(f"Detaching a non-attached observer from LinkedSubject raised an exception: {e}")

    def test_notify_empty_linked_subject(self):
        try:
            self.event_manager.trigger_event("EMPTY_LINKED_NOTIFY")
        except Exception as e:
            self.fail(f"Notifying with no observers in LinkedSubject raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
