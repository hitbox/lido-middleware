import sys

from . import cli
from . import main

options = cli.parse_args()
result = main.run(options)
sys.exit(result)
