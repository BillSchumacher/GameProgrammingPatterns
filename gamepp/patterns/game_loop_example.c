#include "game_loop.h"
#include <stdio.h>

GameLoop my_game_loop;
int processed_updates_c = 0;
double current_position_c = 0.0;
double previous_position_c = 0.0;
double speed_c = 10.0; // units per second

void my_input_c() {
    printf("C: Processing input...\n");
    if (processed_updates_c >= 5) { // Stop after 5 game updates
        GameLoop_stop(&my_game_loop);
    }
}

void my_update_c(double dt) {
    previous_position_c = current_position_c;
    current_position_c += speed_c * dt; // Simulate movement
    processed_updates_c++;
    printf("C: Updating game state with dt: %.4fs (Update #%d), Pos: %.2f\n", 
           dt, processed_updates_c, current_position_c);
}

void my_render_c(double alpha) {
    double interpolated_position = previous_position_c * (1.0 - alpha) + current_position_c * alpha;
    printf("C: Rendering game... Alpha: %.2f, Interpolated Pos: %.2f\n", 
           alpha, interpolated_position);
    printf("C: --------------------\n");
}

int main() {
    GameLoop_init(&my_game_loop, 1.0/60.0); // 60 updates per second

    GameLoop_set_process_input_handler(&my_game_loop, my_input_c);
    GameLoop_set_update_handler(&my_game_loop, my_update_c);
    GameLoop_set_render_handler(&my_game_loop, my_render_c);

    printf("C: Starting game loop...\n");
    GameLoop_start(&my_game_loop);
    printf("C: Game loop stopped.\n");

    return 0;
}
