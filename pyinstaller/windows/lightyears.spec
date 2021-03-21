# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os

a = Analysis(['start.py'],
             binaries=[],
             pathex=[os.environ["ROOT"]],
             datas=[("../../data", "data")],
             hiddenimports=["pygame", "lib20k"],
             hookspath=[],
             runtime_hooks=[],
             excludes=["pytest", "numpy"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='20kly',
          icon='32.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=True,
          version="version.txt",
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)
