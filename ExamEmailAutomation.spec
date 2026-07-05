# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, copy_metadata
from pathlib import Path

block_cipher = None

# Collect template files as individual (src, dest) tuples
_template_dir = Path("src/exam_email_automation/templates")
_template_datas = [
    (str(p), str(p.relative_to(_template_dir.parent)))
    for p in _template_dir.rglob("*")
    if p.is_file()
]

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("config.yaml", "."),
        *[(str(p), str(p.relative_to(_template_dir.parent))) for p in Path("src/exam_email_automation/templates").rglob("*") if p.is_file()],
        ("resources/icon.ico", "resources"),
        ("resources/icon.png", "resources"),
    ],
    hiddenimports=[
        "win32com",
        "win32com.client",
        "pythoncom",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ExamEmailAutomation",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="resources/icon.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="ExamEmailAutomation",
)
