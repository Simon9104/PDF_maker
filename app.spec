# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['reportlab', 'reportlab.pdfbase._fontdata_enc_winansi',
                   'reportlab.pdfbase._fontdata_enc_macroman',
                   'reportlab.pdfbase._fontdata_widths_courier',
                   'reportlab.pdfbase._fontdata_widths_helvetica',
                   'reportlab.pdfbase._fontdata_widths_timesroman'],
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
    name='CustomerTableGenerator',
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
    icon=None,
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='CustomerTableGenerator.app',
        icon=None,
        bundle_identifier='com.pdfmaker.customertable',
        info_plist={
            'NSHighResolutionCapable': True,
            'CFBundleShortVersionString': '1.0.0',
        },
    )
