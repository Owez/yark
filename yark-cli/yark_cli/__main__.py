"""Main runner for those using `python3 -m yark_lib` instead of the proper `yark_lib` script poetry provides"""

import sys
from PyInstaller.lib.modulegraph.modulegraph import entry

entry(sys.argv[1:])
