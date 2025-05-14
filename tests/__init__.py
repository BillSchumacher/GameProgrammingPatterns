import os
import sys

# This adds the project root directory (which is the parent directory of 'gpp')
# to the Python path. This allows modules within the 'tests' directory to
# import modules from the 'gpp' package (e.g., from gpp.gpp import GameObject)
# as if the tests were being run from the project root.

# Path to the 'tests' directory, where this __init__.py file is located
_tests_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the 'gpp' directory (one level up from 'tests')
_gpp_dir = os.path.dirname(_tests_dir)

# Path to the project root directory (one level up from 'gpp')
_project_root = os.path.dirname(_gpp_dir)

# Add project root to the beginning of sys.path if it's not already there
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Clean up namespace to avoid polluting the 'tests' package namespace
del os, sys, _tests_dir, _gpp_dir, _project_root
