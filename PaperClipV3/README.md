# PaperClipV3
PaperClipV3 is the third iteration of a Python-based clipboard monitoring tool.

This version introduces new functionality that allows the user to clear the clipboard contents directly from the GUI. When cleared, both the system clipboard and the GUI display reset. Any previously captured clipboard data that was written to the log file remains unchanged.
Executable Build Instructions

To package this script into a standalone executable, ensure that PyInstaller is installed in your Python environment. Then run:

pyinstaller --noconsole --onefile PaperClip3.py

This command generates a single .exe file while suppressing the console window for a cleaner user experience.

If you prefer to keep the console visible for debugging, remove the --noconsole option.
