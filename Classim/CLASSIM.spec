# -*- mode: python -*- 
import sys
sys.setrecursionlimit(5000)
block_cipher = None

options =[]
added_files= [
   ('.\\images\\*.png','images'),
   ('.\\images\\*.ico','images')
   ]
a = Analysis(['classim.py'],
             pathex=["/%userprofile%/AppData/Local/conda/conda/envs/Classim22/Library/bin"],
             binaries=[],
             datas=added_files,
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
          name='CLASSIM',
          version='classim.rc',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
		  icon='.\images\COMMON.ICO', 
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False, 
               name='CLASSIM')
