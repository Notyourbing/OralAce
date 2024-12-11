# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_dynamic_libs

a = Analysis(
    ['main.py', 'Speech2Text.py', 'Text2Speech.py'],
    pathex=[],
    binaries=collect_dynamic_libs('pyaudio'),  # 添加pyaudio的动态链接库
    datas=[
        ('image/*','image'),
        # 添加portaudio相关文件
        (os.path.join(sys.prefix, 'Lib/site-packages/pyaudio'), 'pyaudio'),
    ],
    hiddenimports=['pyaudio'],  # 显式添加pyaudio
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon='image/icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)