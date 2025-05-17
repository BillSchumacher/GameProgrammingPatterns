#include "game_loop.h"
#include <stdio.h> // For printf, if needed for debugging or examples

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h> // For QueryPerformanceCounter, QueryPerformanceFrequency, Sleep
#else
#include <time.h>    // For clock_gettime, nanosleep (POSIX)
#include <unistd.h>  // For usleep (older POSIX, potentially)
#endif

// Helper function to get current time in seconds (platform-specific)
double get_current_time_seconds_os(GameLoop* loop) {
#ifdef _WIN32
    LARGE_INTEGER current_time_li;
    QueryPerformanceCounter(&current_time_li);
    return (double)current_time_li.QuadPart / loop->perf_frequency;
#else
    struct timespec current_time_ts;
    clock_gettime(CLOCK_MONOTONIC, &current_time_ts);
    return (double)current_time_ts.tv_sec + (double)current_time_ts.tv_nsec / 1e9;
#endif
}

// Helper function for sleeping (platform-specific)
void platform_sleep_seconds_os(double seconds) {
    if (seconds <= 0) return;
#ifdef _WIN32
    Sleep((DWORD)(seconds * 1000)); // Sleep takes milliseconds
#else
    struct timespec sleep_duration_ts;
    sleep_duration_ts.tv_sec = (time_t)seconds;
    sleep_duration_ts.tv_nsec = (long)((seconds - sleep_duration_ts.tv_sec) * 1e9);
    // Use nanosleep for precise sleeping, fall back to usleep or other methods if needed.
    // For simplicity, directly using nanosleep here.
    nanosleep(&sleep_duration_ts, NULL);
#endif
}

void GameLoop_init(GameLoop* loop, double fixed_time_step) {
    loop->is_running = false;
    loop->last_time = 0.0;
    // Initialize handlers to NULL or no-op functions if preferred
    loop->process_input = NULL; 
    loop->update = NULL;
    loop->render = NULL;
    loop->fixed_time_step = fixed_time_step;
    loop->lag = 0.0;
    loop->user_data = NULL; // Initialize user_data
    loop->process_input_user_data_func = NULL;
    loop->update_user_data_func = NULL;
    loop->render_user_data_func = NULL;

#ifdef _WIN32
    LARGE_INTEGER freq;
    if (!QueryPerformanceFrequency(&freq)) {
        // Handle error: High-resolution timer not supported
        // This is a critical error for the game loop's timing mechanism.
        // For a real application, you might fall back to a less precise timer
        // or terminate with an error message.
        printf("Error: High-resolution timer not supported.\n");
        // Setting a default or indicating an error state might be necessary.
        loop->perf_frequency = 1; // Avoid division by zero, but timing will be incorrect.
    } else {
        loop->perf_frequency = freq.QuadPart;
    }
#endif
    // For other platforms like Linux/macOS using clock_gettime, 
    // no specific frequency initialization is typically needed in the loop struct itself.
}

void GameLoop_start(GameLoop* loop) {
    if (loop->is_running) {
        return;
    }

    loop->is_running = true;
    loop->last_time = get_current_time_seconds_os(loop);
    loop->lag = 0.0; // Reset lag when starting

    while (loop->is_running) {
        double current_time = get_current_time_seconds_os(loop);
        double elapsed_time = current_time - loop->last_time;
        loop->last_time = current_time;
        loop->lag += elapsed_time;

        if (loop->process_input) {
            // This branch is for the old way, if someone still uses it.
            ((ProcessInputHandler)loop->process_input)();
        } else if (loop->user_data && loop->process_input_user_data_func) {
            loop->process_input_user_data_func(loop->user_data);
        }

        // Update game logic in fixed time steps
        while (loop->lag >= loop->fixed_time_step) {
            if (loop->update) {
                // This branch is for the old way.
                ((UpdateHandler)loop->update)(loop->fixed_time_step);
            } else if (loop->user_data && loop->update_user_data_func) {
                 loop->update_user_data_func(loop->fixed_time_step, loop->user_data);
            }
            loop->lag -= loop->fixed_time_step;
        }

        if (loop->render) {
            // Alpha is useful for interpolating rendering between fixed updates
            double alpha = loop->lag / loop->fixed_time_step;
            // This branch is for the old way.
            ((RenderHandler)loop->render)(alpha);
        } else if (loop->user_data && loop->render_user_data_func) {
            double alpha = loop->lag / loop->fixed_time_step;
            loop->render_user_data_func(alpha, loop->user_data);
        }

        // Optional: Add a small sleep to prevent hogging CPU
        if (elapsed_time < loop->fixed_time_step) { 
            double sleep_time = loop->fixed_time_step - loop->lag;
            if (loop->lag >= loop->fixed_time_step) { // If lag is still high, maybe just a minimal sleep
                 sleep_time = 0.001; // Minimal sleep to yield CPU
            }
            if (sleep_time > 0) {
                platform_sleep_seconds_os(sleep_time);
            }
        }
    }
}

void GameLoop_stop(GameLoop* loop) {
    loop->is_running = false;
}

void GameLoop_set_process_input_handler(GameLoop* loop, ProcessInputHandler handler) {
    loop->process_input = (void*)handler; // Cast to void* for storage
    loop->process_input_user_data_func = NULL; // Clear the other type of handler
}

void GameLoop_set_update_handler(GameLoop* loop, UpdateHandler handler) {
    loop->update = (void*)handler; // Cast to void* for storage
    loop->update_user_data_func = NULL; // Clear the other type of handler
}

void GameLoop_set_render_handler(GameLoop* loop, RenderHandler handler) {
    loop->render = (void*)handler; // Cast to void* for storage
    loop->render_user_data_func = NULL; // Clear the other type of handler
}

// Implementations for new handler setters with user_data
void GameLoop_set_process_input_handler_with_user_data(GameLoop* loop, ProcessInputHandlerWithUserData handler) {
    loop->process_input_user_data_func = handler;
    loop->process_input = NULL; // Clear the other type of handler
}

void GameLoop_set_update_handler_with_user_data(GameLoop* loop, UpdateHandlerWithUserData handler) {
    loop->update_user_data_func = handler;
    loop->update = NULL; // Clear the other type of handler
}

void GameLoop_set_render_handler_with_user_data(GameLoop* loop, RenderHandlerWithUserData handler) {
    loop->render_user_data_func = handler;
    loop->render = NULL; // Clear the other type of handler
}

void GameLoop_set_user_data(GameLoop* loop, void* user_data) {
    loop->user_data = user_data;
}

bool GameLoop_is_running(const GameLoop* loop) {
    return loop->is_running;
}
