# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

vosk_binaries = collect_dynamic_libs('vosk')
vosk_hiddenimports = collect_submodules('vosk')


a = Analysis(
    ['client\\main.py'],
    pathex=[],
    binaries=vosk_binaries,
    datas=[
        ('client/ressources', 'client/ressources'),
        ('client/tiles', 'client/tiles'),
        ('client/voice/vosk-model-small-fr-0.22', 'client/voice/vosk-model-small-fr-0.22'),
    ],
    hiddenimports=vosk_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AvadaKedavoix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
