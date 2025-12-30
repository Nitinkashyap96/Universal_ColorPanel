# menu.py
# Universal Color Panel – Menu Loader
# Author: Nitin Kashyap

import nuke
import os
import sys
import datetime


version= "v1.0"
update_date= "31 December 2025"

nuke.pluginAddPath(r'./icon')
# ------------------------------------------------------------
# Add tool path (EDIT if needed)
# ------------------------------------------------------------

# TOOL_DIR = os.path.dirname(__file__)

# if TOOL_DIR not in sys.path:
#     sys.path.append(TOOL_DIR)

# ------------------------------------------------------------
# Import Panel
# ------------------------------------------------------------


import Universal_ColorPanel


menubar = nuke.menu("Nuke")
tools_menu = menubar.addMenu("Tools")

tools_menu.addCommand(
    "Universal Color Panel",
    "Universal_ColorPanel.show()",
    icon="ColorWheel.png"  # optional icon
)

# Optional shortcut
# tools_menu.addCommand(
#     "Universal Color Panel",
#     "universal_color_panel.show()",
#     "Ctrl+Alt+C"
# )



license ="Copyright (C) 2025 by Nitin Kashyap,All rights reserved."
nuke.tprint(f"Universal_ColorPanel {version},  build  {update_date}. \n{license}")