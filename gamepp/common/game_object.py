class GameObject:
    """
    Represents a basic game object in the game world.
    """

    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return f"GameObject at ({self.x}, {self.y}, {self.z})"
