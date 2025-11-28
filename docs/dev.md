# For Dev

## [UV](https://docs.astral.sh/uv/) setup
this project use [uv](https://docs.astral.sh/uv/), so you need to install it first

for Mac, Linux
```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```
or
```shell
curl -LsSf https://astral.sh/uv/0.9.13/install.sh | sh
```

for Windows
```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Run
```
uv sync
source .venv/bin/activate
uv run main.py
```
you can setup a `.env` files to save your time

## Add Auth for your school
Coming Soon

## Deploy as a single executable.
we use `pyinstaller` to package this to a single executable.
```bash
uv run pyinstaller --name tenko --onefile --console main.py
```
inside tenko.spec
```
# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='tenko',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```
then run
```bash
uv run pyinstaller --log-level=DEBUG tenko.spec
```