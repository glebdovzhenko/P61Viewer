rmdir build
rmdir dist
del P61ViewerMain.spec
del apps\P61Viewer.exe
pyinstaller -i img\icon.ico src\P61ViewerMain.py --windowed --onefile
xcopy dist\P61ViewerMain.exe apps\\P61Viewer.exe