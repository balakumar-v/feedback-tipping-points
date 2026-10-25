import os
import sys

from p3ope.cli import main

try:
    code = main()
except BrokenPipeError:      # e.g. `python -m p3ope summary | head`: exit quietly instead of a traceback
    os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    code = 0
sys.exit(code)
