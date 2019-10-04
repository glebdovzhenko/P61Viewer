#!/usr/bin/env bash
rm -rf apps/P61BViewer.app build dist
pyinstaller src/P61BViewerMain_mac.spec --windowed -y
cp -r dist/P61BViewer.app apps/P61BViewer.app