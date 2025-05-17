#!/bin/bash

# Compile the C game loop example
echo "Compiling game_loop_example.c and game_loop.c..."
gcc -Wall -I./gamepp/patterns -o ./gamepp/patterns/game_loop_example ./gamepp/patterns/game_loop_example.c ./gamepp/patterns/game_loop.c

# Check if compilation was successful
if [ $? -ne 0 ]; then
    echo "Error: Compilation failed!" >&2
    exit 1
fi

echo "Compilation successful."
echo ""

# Run the compiled example
echo "Running game_loop_example..."
./gamepp/patterns/game_loop_example

echo "Example finished."
