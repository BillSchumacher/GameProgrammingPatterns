from abc import ABC, abstractmethod
from gamepp.common.game_object import GameObject


class Command(ABC):
    """
    The Command interface declares a method for executing a command.
    """

    @abstractmethod
    def execute(self, game_object: GameObject, *args, **kwargs) -> None:
        """
        Execute the command for the given game object.
        """
        pass

    @abstractmethod
    def undo(self, game_object: GameObject, *args, **kwargs) -> None:
        """
        Undo the command for the given game object.
        """
        pass

    @abstractmethod
    def redo(self, game_object: GameObject, *args, **kwargs) -> None:
        """
        Redo the command for the given game object.
        """
        pass


class CommandManager:
    """
    CommandManager is responsible for managing command history and executing commands.
    """

    def __init__(self):
        self._history = []
        self._redo_stack = []

    def execute_command(
        self, command: Command, game_object: GameObject, *args, **kwargs
    ) -> None:
        """
        Execute a command and store it in the history.
        """
        command.execute(game_object, *args, **kwargs)
        self._history.append(command)
        self._redo_stack.clear()  # Clear redo stack on new command execution

    def undo(self, game_object: GameObject) -> None:
        """
        Undo the last executed command.
        """
        if not self._history:
            return
        command = self._history.pop()
        command.undo(game_object)
        self._redo_stack.append(command)

    def redo(self, game_object: GameObject) -> None:
        """
        Redo the last undone command.
        """
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.redo(game_object)
        self._history.append(command)  # Add command back to history
