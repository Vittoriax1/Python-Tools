This is a Python script that creates a GUI to allow the user to monitor what is stored in their clipboard, with a timestamp of when the data is copied, and saves all of the information to a log file.

In order to run this on a Windows system as an executable, please ensure that PyInstaller is already installed in your Python environment. Then, run the following command:

pyinstaller --noconsole --onefile paperclip2.py

This command will create a single executable file and will also hide the black console window.  If you need the console window visible, do not include the "--noconsole" portion of the above command. 

This is the second iteration of the PaperClip script. I've added logging capabilities, as well as a GUI.
