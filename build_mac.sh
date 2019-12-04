#!/usr/bin/env bash
rm -rf apps/P61Viewer.app build dist
pyinstaller src/P61ViewerMain_mac.spec --windowed -y --onefile
cp -r dist/P61Viewer.app apps/P61Viewer.app