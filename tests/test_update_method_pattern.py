import unittest
from unittest.mock import MagicMock

from gamepp.patterns.update_method import UpdateMethodManager, Entity
from gamepp.patterns.game_loop import GameLoop  # For integration example/test


class ConcreteEntity:
    def __init__(self, name: str):
        self.name = name
        self.updates_called = 0
        self.total_time_elapsed = 0.0

    def update(self, dt: float) -> None:
        self.updates_called += 1
        self.total_time_elapsed += dt
        # print(f"{self.name} updated by {dt:.4f}s. Total updates: {self.updates_called}, Total time: {self.total_time_elapsed:.2f}s")

    def __repr__(self) -> str:
        return f"ConcreteEntity(name='{self.name}')"


class TestUpdateMethod(unittest.TestCase):
    def setUp(self):
        self.manager = UpdateMethodManager()
        self.entity1 = ConcreteEntity("Entity1")
        self.entity2 = ConcreteEntity("Entity2")

    def test_add_entity(self):
        self.manager.add_entity(self.entity1)
        self.assertIn(self.entity1, self.manager.entities)
        self.assertEqual(len(self.manager.entities), 1)

        self.manager.add_entity(self.entity1)
        self.assertEqual(len(self.manager.entities), 1)

    def test_remove_entity(self):
        self.manager.add_entity(self.entity1)
        self.manager.add_entity(self.entity2)
        self.manager.remove_entity(self.entity1)
        self.assertNotIn(self.entity1, self.manager.entities)
        self.assertIn(self.entity2, self.manager.entities)
        self.assertEqual(len(self.manager.entities), 1)

        self.manager.remove_entity(self.entity1)
        self.assertEqual(len(self.manager.entities), 1)

    def test_update_all_entities(self):
        self.manager.add_entity(self.entity1)
        self.manager.add_entity(self.entity2)

        dt = 0.1
        self.manager.update_all(dt)

        self.assertEqual(self.entity1.updates_called, 1)
        self.assertEqual(self.entity1.total_time_elapsed, dt)
        self.assertEqual(self.entity2.updates_called, 1)
        self.assertEqual(self.entity2.total_time_elapsed, dt)

        self.manager.update_all(dt * 2)
        self.assertEqual(self.entity1.updates_called, 2)
        self.assertEqual(self.entity1.total_time_elapsed, dt + dt * 2)
        self.assertEqual(self.entity2.updates_called, 2)
        self.assertEqual(self.entity2.total_time_elapsed, dt + dt * 2)

    def test_update_with_mock_entities(self):
        mock_entity1 = MagicMock(spec=Entity)
        mock_entity2 = MagicMock(spec=Entity)

        self.manager.add_entity(mock_entity1)
        self.manager.add_entity(mock_entity2)

        dt = 0.05
        self.manager.update_all(dt)

        mock_entity1.update.assert_called_once_with(dt)
        mock_entity2.update.assert_called_once_with(dt)

        mock_entity1.update.reset_mock()
        mock_entity2.update.reset_mock()

        self.manager.update_all(dt * 3)
        mock_entity1.update.assert_called_once_with(dt * 3)
        mock_entity2.update.assert_called_once_with(dt * 3)

    def test_update_no_entities(self):
        try:
            self.manager.update_all(0.1)
        except Exception as e:
            self.fail(f"update_all crashed with no entities: {e}")

    def test_integration_with_game_loop(self):
        game_loop = GameLoop(fixed_time_step=1 / 60)
        update_manager = UpdateMethodManager()

        entity_a = ConcreteEntity("AgentA_Imported")
        entity_b = ConcreteEntity("AgentB_Imported")
        update_manager.add_entity(entity_a)
        update_manager.add_entity(entity_b)

        updates_to_run = 3
        actual_updates_done_in_handler = 0

        def update_handler_wrapper(dt: float):
            nonlocal actual_updates_done_in_handler
            update_manager.update_all(dt)
            actual_updates_done_in_handler += 1
            if actual_updates_done_in_handler >= updates_to_run:
                game_loop.stop()

        game_loop.set_update_handler(update_handler_wrapper)

        max_outer_loop_iterations = updates_to_run * 5
        outer_loop_iterations = 0

        def safe_process_input_handler():
            nonlocal outer_loop_iterations
            outer_loop_iterations += 1
            if outer_loop_iterations > max_outer_loop_iterations:
                if game_loop.is_running:
                    game_loop.stop()

        game_loop.set_process_input_handler(safe_process_input_handler)
        game_loop.set_render_handler(lambda alpha: None)

        game_loop.start()

        self.assertFalse(game_loop.is_running, "Game loop should have stopped.")

        self.assertEqual(
            actual_updates_done_in_handler,
            updates_to_run,
            f"Update handler wrapper should be called {updates_to_run} times, but was called {actual_updates_done_in_handler} times.",
        )

        self.assertEqual(
            entity_a.updates_called,
            updates_to_run,
            f"Entity A should be updated {updates_to_run} times, got {entity_a.updates_called}.",
        )
        self.assertEqual(
            entity_b.updates_called,
            updates_to_run,
            f"Entity B should be updated {updates_to_run} times, got {entity_b.updates_called}.",
        )

        expected_total_time = updates_to_run * game_loop._fixed_time_step
        self.assertAlmostEqual(
            entity_a.total_time_elapsed,
            expected_total_time,
            places=5,
            msg=f"Entity A total time elapsed is incorrect. Expected ~{expected_total_time:.5f}, got {entity_a.total_time_elapsed:.5f}.",
        )
        self.assertAlmostEqual(
            entity_b.total_time_elapsed,
            expected_total_time,
            places=5,
            msg=f"Entity B total time elapsed is incorrect. Expected ~{expected_total_time:.5f}, got {entity_b.total_time_elapsed:.5f}.",
        )


if __name__ == "__main__":
    unittest.main()
