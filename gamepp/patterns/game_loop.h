#ifndef GAME_LOOP_H
#define GAME_LOOP_H

#include <stdbool.h> // For bool type

// Define function pointer types for handlers
typedef void (*ProcessInputHandler)(void);
typedef void (*UpdateHandler)(double dt);
typedef void (*RenderHandler)(double alpha);

// Define function pointer types for handlers with user_data
typedef void (*ProcessInputHandlerWithUserData)(void* user_data);
typedef void (*UpdateHandlerWithUserData)(double dt, void* user_data);
typedef void (*RenderHandlerWithUserData)(double alpha, void* user_data);

// GameLoop structure
typedef struct {
    bool is_running;
    double last_time;       // Stores time in seconds, obtained from high-resolution timer
    ProcessInputHandler process_input;
    UpdateHandler update;
    RenderHandler render;
    double fixed_time_step;
    double lag;

#ifdef _WIN32
    long long perf_frequency; // For QueryPerformanceFrequency (Windows specific)
#endif
    // For other platforms, time functions might not need per-instance data,
    // or would be handled differently (e.g. clock_gettime doesn't need extra struct fields here)
    void* user_data; // Add user_data pointer for callbacks

    // Function pointers for handlers with user_data
    ProcessInputHandlerWithUserData process_input_user_data_func;
    UpdateHandlerWithUserData update_user_data_func;
    RenderHandlerWithUserData render_user_data_func;
} GameLoop;

// Function prototypes
void GameLoop_init(GameLoop* loop, double fixed_time_step);
void GameLoop_start(GameLoop* loop);
void GameLoop_stop(GameLoop* loop);

void GameLoop_set_process_input_handler(GameLoop* loop, ProcessInputHandler handler);
void GameLoop_set_update_handler(GameLoop* loop, UpdateHandler handler);
void GameLoop_set_render_handler(GameLoop* loop, RenderHandler handler);

// New functions to set handlers with user_data
void GameLoop_set_process_input_handler_with_user_data(GameLoop* loop, ProcessInputHandlerWithUserData handler);
void GameLoop_set_update_handler_with_user_data(GameLoop* loop, UpdateHandlerWithUserData handler);
void GameLoop_set_render_handler_with_user_data(GameLoop* loop, RenderHandlerWithUserData handler);
void GameLoop_set_user_data(GameLoop* loop, void* user_data);

bool GameLoop_is_running(const GameLoop* loop);

// Helper function to get current time in seconds.
// Implementation is in game_loop.c and handles platform specifics.
double get_current_time_seconds_os(GameLoop* loop);

// Helper function for sleeping for a duration in seconds.
// Implementation is in game_loop.c and handles platform specifics.
void platform_sleep_seconds_os(double seconds);

#endif // GAME_LOOP_H
