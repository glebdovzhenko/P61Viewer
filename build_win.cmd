rmdir build
rmdir dist
del P61BViewerMain.spec
del apps\P61BViewer.exe
pyinstaller -i img\icon.ico src\P61BViewerMain.py --windowed --onefile
xcopy dist\P61BViewerMain.exe apps\\P61BViewer.exe