#!/usr/bin/env bash
pyinstaller src/P61BViewerMain.spec --windowed
rm -rf ViewerMac.app
cp -r dist/P61BViewer.app ViewerMac.app