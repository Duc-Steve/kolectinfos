from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    'bs4',                   # pour beautifulsoup4
    'blis',
    'catalogue',
    'certifi',
    'cffi',
    'charset_normalizer',
    'click',
    'cloudpathlib',
    'colorama',
    'confection',
    'cryptography',
    'cymem',
    'dns',
    'et_xmlfile',
    'fr_core_news_lg',
    'idna',
    'jinja2',
    'langcodes',
    'language_data',
    'markdown_it',           # importable comme ça même si le package est markdown-it-py
    'markupsafe',
    'mdurl',
    'murmurhash',
    'numpy',
    'openpyxl',
    'packaging',
    'pandas',
    'pdfminer',              # pour pdfminer.six
    'pdfplumber',
    'PIL',                   # pillow
    'pymongo',
    'pypdfium2',
    'PySide6',
    'dateutil',       # attention : module réel = dateutil
    'pytz',
    'requests',
    'rich',
    'scipy',
    'shiboken6',
    'smart_open',
    'soupsieve',
    'spacy',
    'srsly',
    'thinc',
    'threadpoolctl',
    'tqdm',
    'typer',
    'typing_inspection',
    'tzdata',
    'urllib3',
    'wasabi',
    'weasel',
    'wrapt',
]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('Assets/logoKolectinfos.png', 'Assets')],  # ✅ Correction de la virgule
    hiddenimports=hiddenimports,
    hookspath=['.'],
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
    name='Kolectinfos',
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
    icon='logoKolectinfos.ico',
)
