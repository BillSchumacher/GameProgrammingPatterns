import unittest
from gamepp.patterns.command import Command, CommandManager
from gamepp.common.game_object import GameObject


# A concrete command for testing
class MoveCommand(Command):
    def __init__(self, dx: int, dy: int, dz: int):
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self._previous_x = 0
        self._previous_y = 0
        self._previous_z = 0

    def execute(self, game_object: GameObject, *args, **kwargs) -> None:
        self._previous_x = game_object.x
        self._previous_y = game_object.y
        self._previous_z = game_object.z
        game_object.x += self.dx
        game_object.y += self.dy
        game_object.z += self.dz
        print(
            f"Executed MoveCommand: Moved {game_object} to ({game_object.x}, {game_object.y}, {game_object.z})"
        )

    def undo(self, game_object: GameObject, *args, **kwargs) -> None:
        game_object.x = self._previous_x
        game_object.y = self._previous_y
        game_object.z = self._previous_z
        print(
            f"Undid MoveCommand: Moved {game_object} back to ({game_object.x}, {game_object.y}, {game_object.z})"
        )

    def redo(self, game_object: GameObject, *args, **kwargs) -> None:
        # In this simple case, redo is the same as execute without storing previous again
        # For more complex commands, redo might need its own logic or to store/restore more state.
        self._previous_x = game_object.x  # Store current state before redoing
        self._previous_y = game_object.y
        self._previous_z = game_object.z
        game_object.x += self.dx
        game_object.y += self.dy
        game_object.z += self.dz
        print(
            f"Redid MoveCommand: Moved {game_object} to ({game_object.x}, {game_object.y}, {game_object.z})"
        )


class TestCommandPattern(unittest.TestCase):
    def setUp(self):
        self.command_manager = CommandManager()
        self.game_object = GameObject(0, 0, 0)

    def test_execute_command(self):
        move_command = MoveCommand(10, 5, 2)
        self.command_manager.execute_command(move_command, self.game_object)
        self.assertEqual(self.game_object.x, 10)
        self.assertEqual(self.game_object.y, 5)
        self.assertEqual(self.game_object.z, 2)
        self.assertEqual(len(self.command_manager._history), 1)
        self.assertEqual(len(self.command_manager._redo_stack), 0)

    def test_undo_command(self):
        move_command = MoveCommand(10, 5, 2)
        self.command_manager.execute_command(
            move_command, self.game_object
        )  # x=10, y=5, z=2
        self.command_manager.undo(self.game_object)
        self.assertEqual(self.game_object.x, 0)
        self.assertEqual(self.game_object.y, 0)
        self.assertEqual(self.game_object.z, 0)
        self.assertEqual(len(self.command_manager._history), 0)
        self.assertEqual(len(self.command_manager._redo_stack), 1)

    def test_redo_command(self):
        move_command = MoveCommand(10, 5, 2)
        self.command_manager.execute_command(
            move_command, self.game_object
        )  # x=10, y=5, z=2
        self.command_manager.undo(self.game_object)  # x=0, y=0, z=0
        self.command_manager.redo(self.game_object)  # x=10, y=5, z=2
        self.assertEqual(self.game_object.x, 10)
        self.assertEqual(self.game_object.y, 5)
        self.assertEqual(self.game_object.z, 2)
        # After redo, the command moves from redo_stack back to history
        self.assertEqual(len(self.command_manager._history), 1)
        self.assertEqual(len(self.command_manager._redo_stack), 0)

    def test_undo_empty_history(self):
        initial_x = self.game_object.x
        initial_y = self.game_object.y
        initial_z = self.game_object.z
        self.command_manager.undo(self.game_object)  # Should do nothing
        self.assertEqual(self.game_object.x, initial_x)
        self.assertEqual(self.game_object.y, initial_y)
        self.assertEqual(self.game_object.z, initial_z)
        self.assertEqual(len(self.command_manager._history), 0)
        self.assertEqual(len(self.command_manager._redo_stack), 0)

    def test_redo_empty_stack(self):
        initial_x = self.game_object.x
        initial_y = self.game_object.y
        initial_z = self.game_object.z
        self.command_manager.redo(self.game_object)  # Should do nothing
        self.assertEqual(self.game_object.x, initial_x)
        self.assertEqual(self.game_object.y, initial_y)
        self.assertEqual(self.game_object.z, initial_z)
        self.assertEqual(len(self.command_manager._history), 0)
        self.assertEqual(len(self.command_manager._redo_stack), 0)

    def test_execute_clears_redo_stack(self):
        move_command1 = MoveCommand(10, 0, 0)
        move_command2 = MoveCommand(0, 5, 0)

        self.command_manager.execute_command(move_command1, self.game_object)  # x=10
        self.command_manager.undo(self.game_object)  # x=0, redo_stack has move_command1
        self.assertEqual(len(self.command_manager._redo_stack), 1)

        self.command_manager.execute_command(
            move_command2, self.game_object
        )  # x=0, y=5
        self.assertEqual(self.game_object.y, 5)
        self.assertEqual(
            len(self.command_manager._history), 1
        )  # move_command2 is in history
        self.assertEqual(self.command_manager._history[0], move_command2)
        self.assertEqual(
            len(self.command_manager._redo_stack), 0
        )  # redo_stack is cleared

    def test_multiple_undo_redo(self):
        cmd1 = MoveCommand(1, 1, 1)
        cmd2 = MoveCommand(2, 2, 2)
        cmd3 = MoveCommand(3, 3, 3)

        # Execute three commands
        self.command_manager.execute_command(cmd1, self.game_object)  # (1,1,1)
        self.command_manager.execute_command(cmd2, self.game_object)  # (3,3,3)
        self.command_manager.execute_command(cmd3, self.game_object)  # (6,6,6)
        self.assertEqual(self.game_object.x, 6)
        self.assertEqual(len(self.command_manager._history), 3)

        # Undo last two commands
        self.command_manager.undo(self.game_object)  # Undoes cmd3, back to (3,3,3)
        self.assertEqual(self.game_object.x, 3)
        self.assertEqual(len(self.command_manager._history), 2)
        self.assertEqual(len(self.command_manager._redo_stack), 1)

        self.command_manager.undo(self.game_object)  # Undoes cmd2, back to (1,1,1)
        self.assertEqual(self.game_object.x, 1)
        self.assertEqual(len(self.command_manager._history), 1)
        self.assertEqual(len(self.command_manager._redo_stack), 2)

        # Redo one command
        self.command_manager.redo(self.game_object)  # Redoes cmd2, to (3,3,3)
        self.assertEqual(self.game_object.x, 3)
        self.assertEqual(len(self.command_manager._history), 2)
        self.assertEqual(len(self.command_manager._redo_stack), 1)
        self.assertEqual(
            self.command_manager._history[-1], cmd2
        )  # cmd2 is back in history

        # Execute a new command, should clear redo stack
        cmd4 = MoveCommand(4, 4, 4)
        self.command_manager.execute_command(cmd4, self.game_object)  # (7,7,7)
        self.assertEqual(self.game_object.x, 7)
        self.assertEqual(len(self.command_manager._history), 3)  # cmd1, cmd2, cmd4
        self.assertEqual(len(self.command_manager._redo_stack), 0)


if __name__ == "__main__":
    unittest.main()
