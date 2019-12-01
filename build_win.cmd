rmdir build
rmdir dist
del P61ViewerMain.spec
del apps\P61Viewer.exe
pyinstaller src\P61ViewerMain.py --windowed --onefile --paths C:\Users\glebdovzhenko\Anaconda3\envs\P61Viewer6\Lib\site-packages\scipy\.libs
echo f|xcopy dist\P61ViewerMain.exe apps\P61Viewer.exe
apps\P61Viewer.exe