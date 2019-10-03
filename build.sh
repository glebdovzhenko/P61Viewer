#!/usr/bin/env bash
pyinstaller src/P61BViewerMain.spec --windowed
cp -r dist/P61BViewer.app ViewerMac.app