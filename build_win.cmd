rmdir build
rmdir dist
del P61ViewerMain.spec
del apps\P61Viewer.exe
pyinstaller src\P61ViewerMain.py --onedir --hidden-import=pyopengl --hidden-import=scipy.special.cython_special --noconfirm --windowed