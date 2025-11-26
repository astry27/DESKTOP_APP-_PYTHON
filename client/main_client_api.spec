# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_client_api.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('components', 'components'),
        ('user_data', 'user_data')
    ],
    hiddenimports=[
        'api_client',
        'components.login_dialog',
        'components.pengumuman_component',
        'components.dokumen_component',
        'components.jemaat_component',
        'components.keuangan_component',
        'components.kegiatan_component',
        'components.profile_dialog',
        'components.activity_dialog',
        'components.dashboard_component',
        'components.placeholder_component',
        'client_http'
    ],
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
    name='main_client_api',
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
