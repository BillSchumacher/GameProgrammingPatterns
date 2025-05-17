# Compile the C game loop example
Write-Host "Compiling game_loop_example.c and game_loop.c..."
gcc -Wall -I./gamepp/patterns -o ./gamepp/patterns/game_loop_example.exe ./gamepp/patterns/game_loop_example.c ./gamepp/patterns/game_loop.c

# Check if compilation was successful
if ($LASTEXITCODE -ne 0) {
    Write-Error "Compilation failed!"
    exit $LASTEXITCODE
}

Write-Host "Compilation successful."
Write-Host ""

# Run the compiled example
Write-Host "Running game_loop_example.exe..."
Start-Process -FilePath ./gamepp/patterns/game_loop_example.exe -Wait -NoNewWindow

Write-Host "Example finished."
