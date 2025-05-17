from setuptools import setup, Extension

setup(
    name="gameloop_ext",
    version="1.0",
    description="Python C extension for GameLoop",
    ext_modules=[
        Extension(
            "gameloop_ext",
            sources=["gamepp/patterns/gameloop_ext.c", "gamepp/patterns/game_loop.c"],
            include_dirs=["gamepp/patterns"],
            # Add relevant library_dirs and libraries if your C code has other dependencies
            # For Windows, you might need to specify libraries like 'user32', 'gdi32' etc.
            # depending on what your game loop or its handlers might do.
            # For POSIX, libraries like 'm' (for math.h functions if not auto-linked) or 'rt' (for clock_gettime).
            # libraries=['m'] # Example for POSIX if math functions are used and not auto-linked
        )
    ],
)
