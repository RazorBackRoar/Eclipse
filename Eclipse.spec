# Eclipse.spec
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['src/eclipse/main.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[
        # Include Jinja2 templates (required at runtime)
        ('src/eclipse/templates', 'eclipse/templates'),
    ],
    hiddenimports=[
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'jinja2',
        'jinja2.ext',
        'eclipse.exporters.claude_code',
        'eclipse.exporters.codex',
        'eclipse.exporters.cursor',
        'eclipse.exporters.windsurf',
        'eclipse.exporters.opencode',
        'eclipse.importers.scanner',
        'eclipse.importers.local_drop',
        'eclipse.importers.github_url',
        'eclipse.importers.save_to_library',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,            # onedir mode: binaries collected separately
    name='Eclipse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    console=False,                    # No terminal window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,             # Important for macOS: do not emulate argv
    target_arch='arm64',              # Native Apple Silicon
    codesign_identity=None,           # Shared build wrappers apply ad-hoc signing.
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Eclipse',
)

app = BUNDLE(
    coll,
    name='Eclipse.app',
    icon='assets/Eclipse.icns',
    bundle_identifier='com.razorbackroar.eclipse',
    info_plist={
        'CFBundleName': 'Eclipse',
        'CFBundleDisplayName': 'Eclipse',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleVersion': '2.0.0',
        'LSMinimumSystemVersion': '12.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Supports Dark Mode
        'CFBundleDocumentTypes': [],
        'NSHumanReadableCopyright': 'Copyright 2026 RazorBackRoar',
    },
)
