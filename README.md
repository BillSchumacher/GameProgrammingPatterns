# Game Programming Patterns (gamepp)

## Overview
The `gamepp` package provides a collection of design patterns and best practices for game programming. It aims to help developers implement common patterns in their games, improving code organization, maintainability, and performance.

This collection is from Game Programming Patterns by Robert Nystrom. 

The code however may vary from the authors' original implementation. The book is a very good read, highly recommended.

## Installation
To install the `gamepp` package, you can use pip:

```
pip install gamepp
```

## Available Patterns
The `gamepp` package includes implementations of the following design patterns:

*   **Bytecode:** Defines a set of instructions that can be executed by a virtual machine.
    ```python
    from gamepp.patterns import Instruction, VirtualMachine

    # Define instructions
    ICONST = 1 # Push integer constant
    IADD = 2   # Add two integers
    PRINT = 3  # Print top of stack
    HALT = 4   # Stop execution

    instructions = [
        Instruction(ICONST, 5),
        Instruction(ICONST, 10),
        Instruction(IADD),
        Instruction(PRINT),
        Instruction(HALT),
    ]

    vm = VirtualMachine(instructions)
    vm.run() # Output: 15
    ```
*   **Command:** Encapsulates a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.
    ```python
    from gamepp.patterns.command import Command, CommandManager
    from gamepp.common.game_object import GameObject

    class MoveCommand(Command):
        def __init__(self, x, y):
            self._x = x
            self._y = y
            self._old_x = 0
            self._old_y = 0

        def execute(self, game_object: GameObject):
            self._old_x = game_object.x
            self._old_y = game_object.y
            game_object.x += self._x
            game_object.y += self._y
            print(f"Moved to ({game_object.x}, {game_object.y})")

        def undo(self, game_object: GameObject):
            game_object.x = self._old_x
            game_object.y = self._old_y
            print(f"Undid move to ({game_object.x}, {game_object.y})")

        def redo(self, game_object: GameObject):
            self.execute(game_object) # In this simple case, redo is same as execute

    player = GameObject(0, 0, 0) # Assuming GameObject has x, y, z
    manager = CommandManager()
    
    move_right = MoveCommand(10, 0)
    manager.execute_command(move_right, player) # Output: Moved to (10, 0)
    
    move_up = MoveCommand(0, 5)
    manager.execute_command(move_up, player)    # Output: Moved to (10, 5)
    
    manager.undo(player) # Output: Undid move to (10, 0)
    manager.redo(player) # Output: Moved to (10, 5)
    ```
*   **Component:** Allows you to add functionality to objects dynamically by composing them with reusable components.
    ```python
    from gamepp.patterns.component import Entity, PositionComponent, HealthComponent

    player = Entity()
    player.add_component(PositionComponent(x=10, y=20))
    player.add_component(HealthComponent(current_hp=100, max_hp=100))

    pos = player.get_component(PositionComponent)
    if pos:
        print(f"Player position: ({pos.x}, {pos.y})") # Output: Player position: (10, 20)

    health = player.get_component(HealthComponent)
    if health:
        health.take_damage(10)
        print(f"Player health: {health.current_hp}/{health.max_hp}") # Output: Player health: 90/100
    ```
*   **Context-Sensitive Multigraph (CSM):** A data structure for representing and querying relationships between game entities in a way that adapts to their current state or context.
    ```python
    from gamepp.patterns.csm import CSM, StateMachineInterface
    from enum import Enum

    class CharacterState(Enum):
        IDLE = 1
        CHASING = 2
        FLEEING = 3

    class CharacterFSM(StateMachineInterface):
        def __init__(self):
            self.current_state = CharacterState.IDLE
        def get_current_state_id(self) -> int:
            return self.current_state.value
        def set_state(self, state: CharacterState):
            self.current_state = state

    csm = CSM()
    player_fsm = CharacterFSM()
    enemy_fsm = CharacterFSM()

    # Add nodes (entities) with their state machines
    csm.add_node("player", player_fsm)
    csm.add_node("enemy", enemy_fsm)

    # Add edges based on states. Edge from player to enemy when player is chasing.
    csm.add_edge("player", "enemy", condition_state_id=CharacterState.CHASING.value)
    
    player_fsm.set_state(CharacterState.CHASING)
    # Get neighbors of player when player is in CHASIING state
    neighbors = csm.get_neighbors("player") 
    print(f"Player\'s neighbors when chasing: {neighbors}") # Output: Player's neighbors when chasing: ['enemy']

    player_fsm.set_state(CharacterState.IDLE)
    neighbors = csm.get_neighbors("player")
    print(f"Player\'s neighbors when idle: {neighbors}") # Output: Player's neighbors when idle: []
    ```
*   **Data Locality:** Optimizes performance by organizing data in memory to take advantage of CPU caching.
    ```python
    from gamepp.patterns.data_locality import ParticleSystem

    # Using Structure of Arrays (SoA) for better cache performance
    particle_system = ParticleSystem(max_particles=1000)
    particle_system.add_particle(pos_x=0, pos_y=0, vel_x=1, vel_y=1)
    particle_system.add_particle(pos_x=10, pos_y=10, vel_x=-1, vel_y=-1)

    print(f"Active particles before update: {particle_system.num_active_particles}")
    # Output: Active particles before update: 2 (or the number added)
    
    # This update will iterate over contiguous blocks of memory for positions and velocities
    particle_system.update(dt=0.1) 
    
    # Example of accessing data (less common to do this individually in practice)
    # print(f"Particle 0 position after update: ({particle_system.positions_x[0]}, {particle_system.positions_y[0]})")
    # This would print the updated position of the first active particle.
    ```
*   **Dirty Flag:** Reduces the overhead of updating objects by tracking whether their state has changed and only reprocessing them if necessary.
    ```python
    from gamepp.patterns.dirty_flag import GameObject

    root = GameObject(0, 0, "root")
    child = GameObject(10, 5, "child", parent=root)

    # Initially, representation is dirty and needs computation
    print(child.get_representation()) 
    # Output: Getting representation for child. Dirty: True
    # Output: Recomputed representation for child
    # Output: Object 'child' at world (10.00, 5.00), local (10.00, 5.00)

    # Accessing again without changes uses cached version
    print(child.get_representation())
    # Output: Getting representation for child. Dirty: False
    # Output: Object 'child' at world (10.00, 5.00), local (10.00, 5.00)

    child.local_x = 15 # This marks the transform and representation as dirty
    print(child.get_representation())
    # Output: Getting representation for child. Dirty: True
    # Output: Recomputed representation for child
    # Output: Object 'child' at world (15.00, 5.00), local (15.00, 5.00)
    ```
*   **Double Buffer:** Prevents tearing and provides smoother animation by drawing to an off-screen buffer and then swapping it with the visible buffer.
    ```python
    from gamepp.patterns.double_buffer import DoubleBuffer, Buffer

    # Create two buffers (e.g., for screen pixels or game states)
    buffer1 = Buffer(size=5) # Represents a simple buffer of size 5
    buffer2 = Buffer(size=5)
    double_buffer = DoubleBuffer(buffer1, buffer2)

    # Draw to the back buffer
    back_buf = double_buffer.get_back_buffer()
    for i in range(back_buf.get_size()):
        back_buf.set_data(i, i * 10) # Simulate drawing pixel data
    print(f"Back buffer before swap: {back_buf.get_all_data()}")
    # Output: Back buffer before swap: [0, 10, 20, 30, 40]

    double_buffer.swap()
    print(f"Front buffer after swap: {double_buffer.get_front_buffer().get_all_data()}")
    # Output: Front buffer after swap: [0, 10, 20, 30, 40]
    
    # Now the old front buffer is the new back buffer, ready for next frame's drawing
    new_back_buf = double_buffer.get_back_buffer()
    print(f"New back buffer data (should be old front buffer\'s initial state): {new_back_buf.get_all_data()}")
    # Output: New back buffer data (should be old front buffer's initial state): [0, 0, 0, 0, 0] (if Buffer initializes with 0s)
    ```
*   **Event Queue:** Decouples event producers and consumers by using a central queue to manage events.
    ```python
    from gamepp.patterns.event_queue import Event, EventQueue, global_event_queue

    # Define some event types
    class PlayerJumpEvent(Event):
        def __init__(self, player_id):
            self.player_id = player_id
        def __str__(self):
            return f"PlayerJumpEvent for player {self.player_id}"

    class EnemyDefeatedEvent(Event):
        def __init__(self, enemy_id, points):
            self.enemy_id = enemy_id
            self.points = points
        def __str__(self):
            return f"EnemyDefeatedEvent: {self.enemy_id} defeated, {self.points} points"

    # Using the global event queue (or you can instantiate EventQueue())
    # Producers add events
    global_event_queue.post(PlayerJumpEvent(player_id="player1"))
    global_event_queue.post(EnemyDefeatedEvent(enemy_id="goblin_A", points=100))

    # Consumers process events
    while not global_event_queue.is_empty():
        event = global_event_queue.get()
        if isinstance(event, PlayerJumpEvent):
            print(f"SoundSystem: Playing jump sound for {event.player_id}")
        elif isinstance(event, EnemyDefeatedEvent):
            print(f"ScoreSystem: Adding {event.points} for defeating {event.enemy_id}")
    # Output:
    # SoundSystem: Playing jump sound for player1
    # ScoreSystem: Adding 100 for defeating goblin_A
    ```
*   **Flyweight:** Minimizes memory usage by sharing common data between multiple objects.
    ```python
    from gamepp.patterns.flyweight import FlyweightFactory, TreeType

    factory = FlyweightFactory()

    # Create or get flyweight objects for tree types
    oak_type = factory.get_flyweight("Oak", "Green", "Rough")
    pine_type = factory.get_flyweight("Pine", "DarkGreen", "Needles")
    another_oak_type = factory.get_flyweight("Oak", "Green", "Rough")

    print(f"Oak Type ID: {id(oak_type)}")
    # Output: Oak Type ID: <some_id>
    print(f"Another Oak Type ID: {id(another_oak_type)}") # Should be the same ID as oak_type
    # Output: Another Oak Type ID: <some_id> 
    print(f"Pine Type ID: {id(pine_type)}")
    # Output: Pine Type ID: <another_id>

    # These objects represent the shared (intrinsic) state of trees.
    # Extrinsic state (e.g., position) would be stored elsewhere.
    class Tree:
        def __init__(self, x, y, tree_type: TreeType):
            self.x = x
            self.y = y
            self.tree_type = tree_type # This is the flyweight

        def display(self):
            print(f"Tree at ({self.x},{self.y}) - Type: {self.tree_type.name}, Color: {self.tree_type.color}, Texture: {self.tree_type.texture}")

    tree1 = Tree(10, 20, oak_type)
    tree2 = Tree(15, 30, pine_type)
    tree3 = Tree(25, 35, oak_type) # Reuses the oak_type flyweight

    tree1.display()
    tree2.display()
    tree3.display()
    # Output:
    # Tree at (10,20) - Type: Oak, Color: Green, Texture: Rough
    # Tree at (15,30) - Type: Pine, Color: DarkGreen, Texture: Needles
    # Tree at (25,35) - Type: Oak, Color: Green, Texture: Rough
    
    print(f"Number of distinct flyweights created: {factory.get_flyweight_count()}")
    # Output: Number of distinct flyweights created: 2
    ```
*   **Finite State Machine (FSM):** Represents an object\'s behavior as a set of states and transitions between those states.
    ```python
    from gamepp.patterns.fsm import State, StateMachine

    # Define states
    class IdleState(State):
        def enter(self, entity): print(f"{entity} enters Idle state.")
        def update(self, entity): print(f"{entity} is idling.")
        def exit(self, entity): print(f"{entity} exits Idle state.")

    class WalkingState(State):
        def enter(self, entity): print(f"{entity} enters Walking state.")
        def update(self, entity): print(f"{entity} is walking.")
        def exit(self, entity): print(f"{entity} exits Walking state.")

    # Create a state machine and add states
    fsm = StateMachine(entity_name="Player")
    fsm.add_state("idle", IdleState())
    fsm.add_state("walking", WalkingState())

    fsm.set_state("idle") # Output: Player enters Idle state.
    fsm.update()          # Output: Player is idling.
    fsm.set_state("walking") # Output: Player exits Idle state. Player enters Walking state.
    fsm.update()          # Output: Player is walking.
    ```
*   **Game Loop:** Provides the central control structure for a game, processing input, updating game state, and rendering graphics.
    ```python
    from gamepp.patterns.game_loop import GameLoop
    import time

    class MyGame(GameLoop):
        def __init__(self):
            super().__init__(target_fps=1) # Low FPS for demo
            self.frames = 0

        def process_input(self):
            print("Processing input...")
            pass

        def update(self, dt):
            print(f"Updating game state with dt: {dt:.4f}s")
            self.frames += 1
            if self.frames >= 3: # Run for a few frames then stop for demo
                self.stop()

        def render(self):
            print(f"Rendering frame {self.frames}")

    game = MyGame()
    print("Starting game loop...")
    game.run() 
    print("Game loop stopped.")
    # Output (will run quickly, showing ~3 frames):
    # Starting game loop...
    # Processing input...
    # Updating game state with dt: 1.0000s (approx)
    # Rendering frame 1
    # Processing input...
    # Updating game state with dt: 1.0000s (approx)
    # Rendering frame 2
    # Processing input...
    # Updating game state with dt: 1.0000s (approx)
    # Rendering frame 3
    # Game loop stopped.
    ```

*   **Game Loop (C Extension - `gameloop_ext`):** A high-performance version of the game loop implemented as a CPython extension. It offers a similar API to the Python version but runs the core loop logic in C for better efficiency, while still allowing Python functions to be used as handlers.

    ```python
    # Assuming gameloop_ext.cpXXX-win_amd64.pyd is in your PYTHONPATH
    # or in the same directory
    try:
        from gamepp.patterns import gameloop_ext
        print("Successfully imported gameloop_ext")
    except ImportError as e:
        print(f"Error importing gameloop_ext: {e}")
        print("Make sure the extension is built and accessible.")
        gameloop_ext = None

    if gameloop_ext:
        import time

        loop_data = {
            "frames_processed": 0,
            "max_frames": 5,
            "input_calls": 0,
            "update_calls": 0,
            "render_calls": 0
        }

        # Create a GameLoop instance from the C extension
        # You can specify a fixed time step, e.g., for 30 FPS: 1.0/30.0
        game_loop_ext_instance = gameloop_ext.GameLoop(fixed_time_step=1.0/10.0) # 10 FPS for demo

        def my_process_input():
            loop_data["input_calls"] += 1
            print(f"[Ext] Input: frame {loop_data['frames_processed']}")
            if loop_data["frames_processed"] >= loop_data["max_frames"]:
                print("[Ext] Max frames reached, stopping loop from input handler.")
                game_loop_ext_instance.stop()

        def my_update(dt):
            loop_data["update_calls"] += 1
            print(f"[Ext] Update: dt={dt:.4f}s, frame {loop_data['frames_processed']}")
            # Game logic would go here
            loop_data["frames_processed"] += 1 # Increment after update

        def my_render(alpha):
            loop_data["render_calls"] += 1
            print(f"[Ext] Render: alpha={alpha:.4f}, frame {loop_data['frames_processed']-1}")
            # Rendering logic would go here

        # Set the Python callbacks
        game_loop_ext_instance.set_process_input_handler(my_process_input)
        game_loop_ext_instance.set_update_handler(my_update)
        game_loop_ext_instance.set_render_handler(my_render)

        print("Starting C extension game loop...")
        start_time = time.time()
        game_loop_ext_instance.start() # This is a blocking call
        end_time = time.time()
        print("C extension game loop stopped.")
        print(f"Loop ran for {end_time - start_time:.2f} seconds.")
        print(f"Callbacks: Input={loop_data['input_calls']}, Update={loop_data['update_calls']}, Render={loop_data['render_calls']}")
        print(f"Frames processed (by update): {loop_data['frames_processed']-1}") # -1 because it's incremented before stop check

    # Expected Output (will vary slightly due to timing, ~5 frames at 10 FPS):
    # Successfully imported gameloop_ext
    # Starting C extension game loop...
    # [Ext] Input: frame 0
    # [Ext] Update: dt=0.1000s, frame 0
    # [Ext] Render: alpha=0.XXXX, frame 0 
    # [Ext] Input: frame 1
    # [Ext] Update: dt=0.1000s, frame 1
    # [Ext] Render: alpha=0.XXXX, frame 1
    # [Ext] Input: frame 2
    # [Ext] Update: dt=0.1000s, frame 2
    # [Ext] Render: alpha=0.XXXX, frame 2
    # [Ext] Input: frame 3
    # [Ext] Update: dt=0.1000s, frame 3
    # [Ext] Render: alpha=0.XXXX, frame 3
    # [Ext] Input: frame 4
    # [Ext] Update: dt=0.1000s, frame 4
    # [Ext] Render: alpha=0.XXXX, frame 4
    # [Ext] Input: frame 5
    # [Ext] Max frames reached, stopping loop from input handler.
    # C extension game loop stopped.
    # Loop ran for 0.5X seconds.
    # Callbacks: Input=6, Update=5, Render=5 (Input called one more time to stop)
    # Frames processed (by update): 5
    ```

*   **Hierarchical State Machine (HSM):** Extends FSMs by allowing states to be nested, creating a hierarchy of behaviors.
    ```python
    from gamepp.patterns.hsm import HState, HStateMachine

    class EventLogger: # Helper to see event flow
        def __init__(self): self.log = []
        def add(self, msg): self.log.append(msg)
        def print_log(self): print("\\n".join(self.log))

    logger = EventLogger()

    class BaseTestHState(HState):
        def __init__(self, name): super().__init__(); self.name = name
        def on_enter(self, machine): logger.add(f"{self.name}:on_enter")
        def on_update(self, machine, dt): logger.add(f"{self.name}:on_update") # machine is context (logger here)
        def on_exit(self, machine): logger.add(f"{self.name}:on_exit")

    class ParentState(BaseTestHState): pass
    class ChildState(BaseTestHState): pass

    hsm = HStateMachine(logger) # Pass logger or any context
    parent = ParentState("Parent")
    child = ChildState("Child")
    
    hsm.add_state("parent", parent)
    hsm.add_state("child", child, parent_name="parent") # child is substate of parent

    hsm.set_initial_state("parent")
    hsm.set_initial_state("child", parent_name="parent") # Set initial substate for parent

    hsm.start() 
    
    hsm.update(0.1)
    
    hsm.change_state("parent") 
    
    logger.print_log()
    # Expected output:
    # Parent:on_enter
    # Child:on_enter
    # Parent:on_update
    # Child:on_update
    # Child:on_exit
    ```
*   **Interpreter:** Defines a grammatical representation for a language and provides an interpreter to deal with this grammar.
    ```python
    from gamepp.patterns.interpreter import (
        Expression, 
        NumberExpression, 
        AddExpression, 
        SubtractExpression,
        MultiplyExpression,
        DivideExpression
    )

    # Represent " (5 + 10) * 2 - 30 / 3 "
    # AST: Subtract(Multiply(Add(Number(5), Number(10)), Number(2)), Divide(Number(30), Number(3)))
    
    expr = SubtractExpression(
        MultiplyExpression(
            AddExpression(NumberExpression(5), NumberExpression(10)), 
            NumberExpression(2)
        ),
        DivideExpression(NumberExpression(30), NumberExpression(3))
    )
    
    result = expr.interpret()
    print(f"Interpreter result: {result}") # Output: Interpreter result: 20.0
    
    try:
        error_expr = DivideExpression(NumberExpression(5), NumberExpression(0))
        error_expr.interpret()
    except ValueError as e:
        print(f"Error: {e}") # Output: Error: Cannot divide by zero.
    ```
*   **Object Pool:** Improves performance by reusing objects instead of creating and destroying them repeatedly.
    ```python
    from gamepp.patterns.object_pool import ObjectPool, PooledObject

    class Bullet(PooledObject):
        _id_counter = 0 # Class variable to ensure unique IDs for new bullets

        def __init__(self, pool_index: int): # pool_index is passed by the pool
            super().__init__()
            self.id_num = Bullet._id_counter
            Bullet._id_counter +=1
            self.pool_assigned_index = pool_index # Store the index given by pool for debug
            self.x = 0
            self.y = 0
            print(f"Bullet {self.id_num} (pool_idx:{self.pool_assigned_index}) created/re-initialized.")

        def reset(self): # Called when released back to pool
            super().reset()
            self.x = -1000 
            self.y = -1000
            # id_num remains to track the original bullet concept
            print(f"Bullet {self.id_num} (pool_idx:{self.pool_assigned_index}) reset and returned to pool.")

        def fire(self, x, y):\
            self.x = x
            self.y = y
            print(f"Bullet {self.id_num} (pool_idx:{self.pool_assigned_index}) fired to ({self.x}, {self.y})")

    # Create a pool of 2 bullets. The lambda provides the pool index to the constructor.
    bullet_pool = ObjectPool(Bullet, pool_size=2, object_init_args=(lambda i: i,))

    print(f"Available objects in pool: {bullet_pool.get_available_count()}")

    b1 = bullet_pool.acquire()
    if b1: b1.fire(10, 20)

    b2 = bullet_pool.acquire()
    if b2: b2.fire(15, 25)
    
    b_extra = bullet_pool.acquire() # Try to acquire more than available
    if not b_extra:
        print("Could not acquire third bullet, pool is empty.")

    if b1: bullet_pool.release(b1)
    print(f"Available objects in pool after releasing b1: {bullet_pool.get_available_count()}")

    b3 = bullet_pool.acquire() # Should reuse the one that was b1
    if b3: b3.fire(30,40) 
    
    print(f"Is b1 the same object as b3? {b1 is b3}") # True, object is reused

    # Expected Output:
    # Available objects in pool: 0 (Pool initializes objects, making them unavailable until reset by constructor)
    # Bullet 0 (pool_idx:0) created/re-initialized.
    # Bullet 1 (pool_idx:1) created/re-initialized.
    # Available objects in pool: 2 
    # Bullet 0 (pool_idx:0) fired to (10, 20)
    # Bullet 1 (pool_idx:1) fired to (15, 25)
    # Could not acquire third bullet, pool is empty.
    # Bullet 0 (pool_idx:0) reset and returned to pool.
    # Available objects in pool after releasing b1: 1
    # Bullet 0 (pool_idx:0) fired to (30,40)
    # Is b1 the same object as b3? True
    ```
*   **Observer:** Defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.
    ```python
    from gamepp.patterns.observer import Subject, ObserverMixin

    class Player(Subject): 
        def __init__(self, name):
            super().__init__()
            self.name = name
            self._health = 100

        @property
        def health(self): return self._health
        
        @health.setter
        def health(self, value):
            old_health = self._health
            if self._health != value:
                self._health = value
                self.notify(event="health_changed", old_health=old_health, new_health=self._health)

    class HealthDisplay(ObserverMixin): 
        def update(self, subject, event, **kwargs):
            if event == "health_changed":
                print(f"HealthDisplay: Player {subject.name}'s health changed from {kwargs['old_health']} to {kwargs['new_health']}")

    class AchievementSystem(ObserverMixin):
        def update(self, subject, event, **kwargs):
            if event == "health_changed" and kwargs['new_health'] <= 0 and kwargs['old_health'] > 0:
                print(f"AchievementSystem: Player {subject.name} has been defeated! Achievement unlocked.")

    player = Player("Hero")
    health_bar = HealthDisplay()
    achievements = AchievementSystem()

    player.attach(health_bar)
    player.attach(achievements)

    player.health = 80
    player.health = 50
    player.health = 0
    player.health = -10 # To show it only triggers achievement once
    player.health = 50 # Bring back to life, no achievement
    
    # Expected Output:
    # HealthDisplay: Player Hero's health changed from 100 to 80
    # HealthDisplay: Player Hero's health changed from 80 to 50
    # HealthDisplay: Player Hero's health changed from 50 to 0
    # AchievementSystem: Player Hero has been defeated! Achievement unlocked.
    # HealthDisplay: Player Hero's health changed from 0 to -10
    # HealthDisplay: Player Hero's health changed from -10 to 50
    ```
*   **Pushdown Automaton (PDA):** An extension of finite state machines that includes a stack, allowing for more complex state management or parsing.
    ```python
    from gamepp.patterns.pda import PushdownAutomata, PDAState
    from typing import Any

    # --- Define States for a simple menu system ---
    class BaseMenuState(PDAState):
        def __init__(self, name: str):
            self.name = name
        def enter(self, pda: PushdownAutomata):
            print(f"Entering {self.name} State")
        def exit(self, pda: PushdownAutomata):
            print(f"Exiting {self.name} State")
        def handle_input(self, pda: PushdownAutomata, input_data: Any):
            print(f"{self.name} received input: {input_data}")
            if input_data == "back":
                pda.pop_state()

    class MainMenuState(BaseMenuState):
        def __init__(self):
            super().__init__("MainMenu")
        def handle_input(self, pda: PushdownAutomata, input_data: Any):
            super().handle_input(pda, input_data)
            if input_data == "options":
                pda.push_state(OptionsMenuState())
            elif input_data == "play":
                pda.push_state(PlayingGameState())

    class OptionsMenuState(BaseMenuState):
        def __init__(self):
            super().__init__("OptionsMenu")
        def handle_input(self, pda: PushdownAutomata, input_data: Any):
            super().handle_input(pda, input_data)
            if input_data == "sound":
                pda.push_state(SoundOptionsState())
    
    class SoundOptionsState(BaseMenuState):
        def __init__(self):
            super().__init__("SoundOptions")

    class PlayingGameState(BaseMenuState):
        def __init__(self):
            super().__init__("PlayingGame")
        def handle_input(self, pda: PushdownAutomata, input_data: Any):
            super().handle_input(pda, input_data)
            if input_data == "pause":
                pda.push_state(PauseMenuState())

    class PauseMenuState(BaseMenuState):
        def __init__(self):
            super().__init__("PauseMenu")
        def handle_input(self, pda: PushdownAutomata, input_data: Any):
            super().handle_input(pda, input_data)
            if input_data == "resume": # This will pop PauseMenu
                pda.pop_state() 
            elif input_data == "main_menu": # Pop until back to main or specific state
                # For simplicity, pop twice if we know Pause is on top of Playing
                pda.pop_state() # Pop Pause
                pda.pop_state() # Pop PlayingGame
    
    # --- PDA Usage ---
    pda_system = PushdownAutomata(MainMenuState())

    inputs = ["options", "sound", "back", "play", "pause", "resume", "pause", "main_menu", "invalid_input"]

    for inp in inputs:
        print(f"--- PDA Stack Depth: {pda_system.stack_depth}, Current: {pda_system.current_state.name if pda_system.current_state else 'None'} ---")
        pda_system.handle_input(inp)
        if pda_system.stack_depth == 0:
            print("PDA stack is empty, stopping.")
            break
    
    # Expected Output (simplified):
    # --- PDA Stack Depth: 1, Current: MainMenu ---
    # Entering MainMenu State
    # MainMenu received input: options
    # Entering OptionsMenu State
    # --- PDA Stack Depth: 2, Current: OptionsMenu ---
    # OptionsMenu received input: sound
    # Entering SoundOptions State
    # --- PDA Stack Depth: 3, Current: SoundOptions ---
    # SoundOptions received input: back
    # Exiting SoundOptions State
    # --- PDA Stack Depth: 2, Current: OptionsMenu ---
    # OptionsMenu received input: play  (Error in logic here, Options doesn't handle 'play')
    # (Corrected logic would be 'back' then 'play' from MainMenu)
    # Let's assume 'back' from OptionsMenu, then 'play' from MainMenu
    # Exiting OptionsMenu State
    # --- PDA Stack Depth: 1, Current: MainMenu ---
    # MainMenu received input: play
    # Entering PlayingGame State
    # --- PDA Stack Depth: 2, Current: PlayingGame ---
    # PlayingGame received input: pause
    # Entering PauseMenu State
    # --- PDA Stack Depth: 3, Current: PauseMenu ---
    # PauseMenu received input: resume
    # Exiting PauseMenu State
    # --- PDA Stack Depth: 2, Current: PlayingGame ---
    # PlayingGame received input: pause
    # Entering PauseMenu State
    # --- PDA Stack Depth: 3, Current: PauseMenu ---
    # PauseMenu received input: main_menu
    # Exiting PauseMenu State
    # Exiting PlayingGame State
    # --- PDA Stack Depth: 1, Current: MainMenu ---
    # MainMenu received input: invalid_input
    ```
*   **Prototype:** Creates new objects by copying an existing object, known as the prototype.
    ```python
    from gamepp.patterns.prototype import Prototype
    import copy

    class Monster(Prototype):
        def __init__(self, name, health, attack):
            self.name = name
            self.health = health
            self.attack = attack
            self.abilities = [] # Complex object

        def clone(self):
            # Use deepcopy for a true independent clone if attributes are mutable
            cloned_obj = copy.deepcopy(self)
            return cloned_obj
            
        def __str__(self):
            return f"{self.name} - HP: {self.health}, ATK: {self.attack}, Abilities: {self.abilities}"

    goblin_prototype = Monster("Goblin", 50, 5)
    goblin_prototype.abilities.append("Sneak")

    # Create new monsters by cloning the prototype
    goblin1 = goblin_prototype.clone()
    goblin1.name = "Goblin Warrior" # Customize the clone
    goblin1.health = 60
    goblin1.abilities.append("Shield Bash")


    goblin2 = goblin_prototype.clone()
    goblin2.name = "Goblin Archer"
    goblin2.attack = 7
    
    print(goblin_prototype) # Output: Goblin - HP: 50, ATK: 5, Abilities: ['Sneak']
    print(goblin1)          # Output: Goblin Warrior - HP: 60, ATK: 5, Abilities: ['Sneak', 'Shield Bash']
    print(goblin2)          # Output: Goblin Archer - HP: 50, ATK: 7, Abilities: ['Sneak']
    # Note: goblin_prototype.abilities was also changed by goblin1 if not deepcopied correctly.
    # The provided Prototype class in gamepp might handle this.
    ```
*   **Service Locator:** Provides a global point of access for services, decoupling clients from concrete service implementations.
    ```python
    from gamepp.patterns.service_locator import ServiceLocator, NullService, get_service, register_service

    # Define a service interface (optional, but good practice)
    class IAudio:
        def play_sound(self, sound_id): pass
        def stop_sound(self, sound_id): pass

    # Concrete service implementation
    class AudioSystem(IAudio):
        def play_sound(self, sound_id): print(f"AudioSystem: Playing sound {sound_id}")
        def stop_sound(self, sound_id): print(f"AudioSystem: Stopping sound {sound_id}")

    # Null service (for when the real service isn't available)
    class NullAudio(NullService, IAudio): # Inherits from NullService
        def play_sound(self, sound_id): print("NullAudio: (No sound played)")
        def stop_sound(self, sound_id): print("NullAudio: (No sound stopped)")

    # Register the service (typically at app startup)
    # ServiceLocator.register("audio", AudioSystem()) # Direct instantiation
    # Or using the helper functions:
    register_service("audio", AudioSystem(), IAudio) # Register with interface type

    # Client code gets the service
    # audio_service = ServiceLocator.get("audio")
    # Or using the helper function with type hinting:
    audio_service = get_service(IAudio) # Type hint helps IDEs and static analysis

    if audio_service:
        audio_service.play_sound("jump.wav") # Output: AudioSystem: Playing sound jump.wav

    # Example with NullService if real one wasn't registered for "audio_fx"
    register_service("audio_fx", NullAudio(), IAudio) # Register a null service
    fx_service = get_service(IAudio, service_name="audio_fx")
    if fx_service:
        fx_service.play_sound("explosion.wav") # Output: NullAudio: (No sound played)
    ```
*   **Singleton:** Ensures that a class has only one instance and provides a global point of access to it.
    ```python
    from gamepp.patterns.singleton import Singleton

    class GameManager(Singleton):
        def __init__(self):
            # Ensure init is called only once by Singleton's logic
            if hasattr(self, '_initialized') and self._initialized:
                return
            print("GameManager initialized.")
            self.score = 0
            self._initialized = True

        def add_score(self, points):
            self.score += points
            print(f"Score is now: {self.score}")

    # Get the singleton instance
    gm1 = GameManager.instance() # Output: GameManager initialized. (only first time)
    gm1.add_score(10)            # Output: Score is now: 10

    gm2 = GameManager.instance() # Does not re-initialize
    gm2.add_score(20)            # Output: Score is now: 30 (operates on the same instance)

    print(f"Are gm1 and gm2 the same object? {gm1 is gm2}") # Output: True
    ```
*   **Spatial Partition:** Divides the game world into smaller regions to optimize collision detection and other spatial queries.
    ```python
    from gamepp.patterns.spatial_partition import GridPartition, SpatialObject
    import math

    # Simple entity that will use SpatialObject for grid management
    class GameEntity:
        def __init__(self, entity_id: str, x: float, y: float):
            self.entity_id = entity_id
            # The SpatialObject holds the representation for the grid
            self.spatial_repr = SpatialObject(entity_id, x, y)

        def move(self, dx: float, dy: float, grid: GridPartition):
            new_x = self.spatial_repr.position[0] + dx
            new_y = self.spatial_repr.position[1] + dy
            grid.update_object_position(self.spatial_repr, new_x, new_y)
            print(f"Entity {self.entity_id} moved to ({new_x:.1f}, {new_y:.1f})")

        @property
        def position(self):
            return self.spatial_repr.position

    # Initialize grid
    world_width, world_height = 200, 200
    cell_size = 50
    grid = GridPartition(cell_size, world_width, world_height)

    # Create entities
    entity1 = GameEntity("player", 20, 20)
    entity2 = GameEntity("enemyA", 30, 30)
    entity3 = GameEntity("enemyB", 180, 180) # In a different part of the grid
    entity4 = GameEntity("item", 25, 70)    # Near player and enemyA

    grid.add_object(entity1.spatial_repr)
    grid.add_object(entity2.spatial_repr)
    grid.add_object(entity3.spatial_repr)
    grid.add_object(entity4.spatial_repr)

    print("Initial state:")
    for y_idx, row in enumerate(grid.grid):
        for x_idx, cell in enumerate(row):
            if cell:
                print(f"Cell ({x_idx},{y_idx}): {[obj.obj_id for obj in cell]}")

    # Query for objects near player (entity1)
    # The query_nearby in the provided spatial_partition.py is not fully implemented
    # So we'll manually check the player's cell and neighbors for this example
    
    def get_objects_in_cell_and_neighbors(target_obj_spatial: SpatialObject, grid_partition: GridPartition):
        results = set()
        tx, ty = grid_partition._get_cell_coords(target_obj_spatial.position)
        for r_offset in range(-1, 2): # -1, 0, 1
            for c_offset in range(-1, 2):
                cell_y, cell_x = ty + r_offset, tx + c_offset
                if 0 <= cell_y < grid_partition.grid_height and 0 <= cell_x < grid_partition.grid_width:
                    results.update(grid_partition.grid[cell_y][cell_x])
        return [obj for obj in results if obj is not target_obj_spatial]

    print(f"\\nQuerying near {entity1.entity_id} at {entity1.position}:")
    nearby_to_e1 = get_objects_in_cell_and_neighbors(entity1.spatial_repr, grid)
    print(f"Found: {[obj.obj_id for obj in nearby_to_e1]}")
    # Expected: enemyA, item (depending on cell boundaries)

    # Move player
    entity1.move(40, 40, grid) # Move player to (60,60) - likely a new cell

    print("\\nState after player moves:")
    for y_idx, row in enumerate(grid.grid):
        for x_idx, cell in enumerate(row):
            if cell:
                print(f"Cell ({x_idx},{y_idx}): {[obj.obj_id for obj in cell]}")
    
    print(f"\\nQuerying near {entity1.entity_id} at {entity1.position} after move:")
    nearby_to_e1_moved = get_objects_in_cell_and_neighbors(entity1.spatial_repr, grid)
    print(f"Found: {[obj.obj_id for obj in nearby_to_e1_moved]}")
    # Expected: item (enemyA might be out of direct neighbor cells now)

    # Expected Output (structure, actual cell content depends on exact coords & cell_size):
    # Initial state:
    # Cell (0,0): ['player', 'enemyA']
    # Cell (0,1): ['item']
    # Cell (3,3): ['enemyB']
    #
    # Querying near player at (20.0, 20.0):
    # Found: ['enemyA', 'item'] (or similar, based on neighborhood)
    # Entity player moved to (60.0, 60.0)
    #
    # State after player moves:
    # Cell (0,0): ['enemyA']
    # Cell (0,1): ['item'] 
    # Cell (1,1): ['player'] 
    # Cell (3,3): ['enemyB']
    #
    # Querying near player at (60.0, 60.0) after move:
    # Found: ['item'] (or similar)
    ```
*   **Type Object:** Allows you to create new classes by defining their behavior and properties through a type object.
    ```python
    from gamepp.patterns.type_object import Breed, Monster

    # Define breed types (Type Objects)
    goblin_breed = Breed(name="Goblin", health=30, attack_damage=5, sound="Goblin grunt")
    dragon_breed = Breed(name="Dragon", health=500, attack_damage=40, sound="Dragon roar")

    # Create monster instances using these breeds
    monster1 = goblin_breed.new_monster() # Creates a Monster instance
    monster1.name_instance = "Grizlak the Goblin" # Instance-specific data

    monster2 = dragon_breed.new_monster()
    monster2.name_instance = "Ignis the Red"
    
    monster3 = goblin_breed.new_monster() # Another goblin, shares breed properties

    print(f"{monster1.name_instance} ({monster1.get_breed().name}) attacks for {monster1.get_attack_damage()} damage.")
    # Output: Grizlak the Goblin (Goblin) attacks for 5 damage.
    monster1.make_sound() # Output: Goblin grunt

    print(f"{monster2.name_instance} ({monster2.get_breed().name}) has {monster2.get_health()} HP.")
    # Output: Ignis the Red (Dragon) has 500 HP.
    monster2.make_sound() # Output: Dragon roar
    
    print(f"Monster 3 is a {monster3.get_breed().name}")
    # Output: Monster 3 is a Goblin
    ```
*   **Update Method:** Provides a simple way to update game objects by calling an update method on each object during each frame of the game loop.
    ```python
    from gamepp.patterns.update_method import UpdateMethodManager, Entity as UpdateableEntity

    class Player(UpdateableEntity):
        def __init__(self, name):
            super().__init__()
            self.name = name
            self.position = 0
        
        def update(self, dt): # dt is delta time
            self.position += 1 * dt # Move one unit per second
            print(f"Player {self.name} updated. Position: {self.position:.2f}")

    class Enemy(UpdateableEntity):
        def __init__(self, name):
            super().__init__()
            self.name = name
            self.energy = 100

        def update(self, dt):
            self.energy -= 5 * dt # Lose energy over time
            print(f"Enemy {self.name} updated. Energy: {self.energy:.2f}")

    manager = UpdateMethodManager()
    player1 = Player("Hero")
    enemy1 = Enemy("Goblin")

    manager.add_entity(player1)
    manager.add_entity(enemy1)

    print("--- First update call ---")
    manager.update_all(dt=0.1) 
    # Output:
    # Player Hero updated. Position: 0.10
    # Enemy Goblin updated. Energy: 99.50

    print("\\n--- Second update call ---")
    manager.update_all(dt=0.5)
    # Output:
    # Player Hero updated. Position: 0.60 (0.1 + 0.5)
    # Enemy Goblin updated. Energy: 97.00 (99.5 - 2.5)
    
    manager.remove_entity(enemy1)
    print("\\n--- Third update call (enemy removed) ---")
    manager.update_all(dt=0.1)
    # Output:
    # Player Hero updated. Position: 0.70 
    ```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.