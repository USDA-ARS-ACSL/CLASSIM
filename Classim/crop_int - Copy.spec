# -*- mode: python -*-
import sys
sys.setrecursionlimit(5000)
block_cipher = None

#options =[(--upx-dir 'C:\\Users\\dennis.timlin\\UPX\\upx-3.95-win32',NONE,'OPTION')]
a = Analysis(['crop_int.py'],
             pathex=['C:\\Users\\Maura.Tokay\\Documents\\VisualStudio\\Workspace\\crop_int\\crop_int'],
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
          name='crop_int',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='crop_int')
