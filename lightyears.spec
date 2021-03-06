# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os

a = Analysis(['lightyears'],
             pathex=[os.getcwd()],
             binaries=[],
             datas=[("data", "data"), ("audio", "audio"), ("manual", "manual"), 
                    ("LICENSE.txt", "."), ("THANKS.txt", "."), 
                    ("README.txt", "."), ("code", "code")],
             hiddenimports=["pygame"],
             hookspath=[],
             runtime_hooks=[],
             excludes=["pytest"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='lightyears',
          debug="noarchive",
          icon="data/32.ico",
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='lightyears')
