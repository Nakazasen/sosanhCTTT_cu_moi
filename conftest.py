import os
import sys

tcl_dir = os.path.join(sys.base_prefix, 'tcl', 'tcl8.6').replace('\\', '/')
tk_dir = os.path.join(sys.base_prefix, 'tcl', 'tk8.6').replace('\\', '/')
if os.path.exists(tcl_dir):
    os.environ['TCL_LIBRARY'] = tcl_dir
if os.path.exists(tk_dir):
    os.environ['TK_LIBRARY'] = tk_dir

