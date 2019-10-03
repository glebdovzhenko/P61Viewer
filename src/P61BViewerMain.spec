# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['P61BViewerMain.py'],
             pathex=['/Users/glebdovzhenko/Dropbox/PycharmProjects/P61Viewer/src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='P61BViewerMain',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='P61BViewerMain')

app = BUNDLE(coll,
             name='P61BViewer.app',
             icon='../img/icon.icns',
             info_plist={
                  'NSHighResolutionCapable': 'True'
                },
             bundle_identifier=None)

