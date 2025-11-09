# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Speech to Text Application
Builds both CLI and GUI executables with shared dependencies via MERGE

Usage:
    pyinstaller SpeechToText.spec --noconfirm
    py -3.13 -m uv run pyinstaller SpeechToText.spec --noconfirm
"""

import os
import sys
from pathlib import Path
from glob import glob

# Trouver le chemin vers whisper assets
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    # Environnement virtuel
    whisper_path = Path(sys.prefix) / 'Lib' / 'site-packages' / 'whisper'
else:
    # Installation système
    import whisper
    whisper_path = Path(whisper.__file__).parent

whisper_assets = whisper_path / 'assets'

# ============================================================================
# CLI EXECUTABLE (console application)
# ============================================================================

a_cli = Analysis(
    ['speech_to_text.py'],              # Script principal CLI
    pathex=[],                          # Chemins additionnels (vide = sys.path)
    binaries=[],                        # Binaires additionnels (.dll, .so)
    datas=[
        ('models', 'models'),           # Dossier models à inclure
        (str(whisper_assets), 'whisper/assets'),  # ✅ Assets whisper (mel_filters.npz, etc.)
    ],
    hiddenimports=['whisper'],          # Imports non détectés (forcer whisper)
    hookspath=[],                       # Hooks personnalisés
    hooksconfig={},                     # Configuration des hooks
    excludes=[                          # Modules à EXCLURE
        # Torch modules inutiles
        'torch.utils.tensorboard',      # 2. TensorBoard visualisation (dev tool)
        'torchvision.models',           # 3. Modèles vision pré-entraînés (CNN, ResNet, etc.)
        'torchaudio',                   # 4. Audio processing (whisper utilise ses propres fonctions)
        
        # Windows COM/IDE (inutiles)
        'Pythonwin',                    # 6. PythonWin IDE (~6 MB)
        'win32com',                     # 7. Windows COM automation
        'pythoncom',                    # 7. Python COM support
        
        # Build/dev tools (inutiles dans exe)
        'setuptools',                   # 8. Packaging tools
        'distutils',                    # 8. Distribution utilities
        'pip',                          # 8. Package installer
        '_distutils_hack',              # 8. Hack setuptools
        
        # Dev/test tools (inutiles)
        'matplotlib',                   # 9. Graphiques (pas utilisé)
        'IPython',                      # 10. Interactive Python
        'jupyter',                      # 10. Jupyter notebook
        'notebook',                     # 10. Jupyter notebook
        'pytest',                       # 10. Testing framework
    ],
    noarchive=False,                    # False = compression des .py
    optimize=1,                         # 0=aucune, 1=basic, 2=aggressive (bytecode optimisé)
)

pyz_cli = PYZ(a_cli.pure)

exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
    [],
    exclude_binaries=True,              # True = mode onedir (fichiers séparés)
    name='SpeechToText',                # Nom de l'exécutable
    debug=False,                        # False = mode production
    bootloader_ignore_signals=False,    # Gérer les signaux système (Ctrl+C)
    strip=False,                        # Garder symboles debug (Linux/Mac)
    upx=False,                           # Compression UPX (taille réduite)
    upx_exclude=[
        'vcruntime*.dll',
        'python*.dll',
        'VCRUNTIME*.dll',
    ],
    console=True,                       # ✅ Console visible (CLI)
    disable_windowed_traceback=False,   # Afficher les erreurs
    argv_emulation=False,               # macOS uniquement
    target_arch=None,                   # Auto-détection architecture
    codesign_identity=None,             # Signature code (macOS)
    entitlements_file=None,             # Entitlements (macOS)
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

# ============================================================================
# GUI EXECUTABLE (windowed application)
# ============================================================================

a_gui = Analysis(
    ['speech_to_text_gui.py'],          # Script principal GUI
    pathex=[],
    binaries=[],
    datas=[
        ('models', 'models'),           # Dossier models à inclure
        (str(whisper_assets), 'whisper/assets'),  # ✅ Assets whisper
    ],
    hiddenimports=['whisper'],          # Forcer l'inclusion de whisper
    hookspath=[],
    hooksconfig={},
    excludes=[                          # Modules à exclure
        # Torch modules inutiles
        'torch.utils.tensorboard',      # 2. TensorBoard visualisation
        'torchvision.models',           # 3. Modèles vision pré-entraînés
        'torchaudio',                   # 4. Audio processing
        
        # Windows COM/IDE (inutiles)
        'Pythonwin',                    # 6. PythonWin IDE (~6 MB)
        'win32com',                     # 7. Windows COM automation
        'pythoncom',                    # 7. Python COM support
        
        # Build/dev tools (inutiles dans exe)
        'setuptools',                   # 8. Packaging tools
        'distutils',                    # 8. Distribution utilities
        'pip',                          # 8. Package installer
        '_distutils_hack',              # 8. Hack setuptools
        
        # Dev/test tools (inutiles)
        'matplotlib',                   # 9. Graphiques (pas utilisé)
        'IPython',                      # 10. Interactive Python
        'jupyter',                      # 10. Jupyter notebook
        'notebook',                     # 10. Jupyter notebook
        'pytest',                       # 10. Testing framework
    ],
    noarchive=False,                    # Compression des .py
    optimize=1,                         # Optimisation bytecode Python (aggressive)
)

pyz_gui = PYZ(a_gui.pure)

exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    [],
    exclude_binaries=True,              # True = mode onedir
    name='SpeechToTextGUI',             # Nom de l'exécutable GUI
    debug=False,                        # Mode production
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                           # Compression UPX
    upx_exclude=[
        'vcruntime*.dll',
        'python*.dll',
        'VCRUNTIME*.dll',
    ],
    console=True,                       # ✅ GARDER console=True pour éviter les problèmes
    disable_windowed_traceback=False,   # Afficher les erreurs GUI
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

# ============================================================================
# COLLECT - Shared resources for both executables (multipackaging)
# ============================================================================
# Un seul COLLECT pour partager les DLLs communes (torch, whisper, etc.)
# Les deux .exe seront dans le même dossier dist/SpeechToText/
# avec un seul _internal/ partagé
coll = COLLECT(
    exe_cli,                            # Premier exécutable (CLI)
    a_cli.binaries,
    a_cli.zipfiles,
    a_cli.datas,
    exe_gui,                            # Deuxième exécutable (GUI)
    a_gui.binaries,
    a_gui.zipfiles,
    a_gui.datas,
    strip=False,
    upx=False,                           # Compression des DLLs
    upx_exclude=[                       # DLLs à ne pas compresser (problèmes connus)
        'vcruntime*.dll',
        'msvcp*.dll',
        'python*.dll',
        'VCRUNTIME*.dll',
    ],
    name='SpeechToText',                # Nom du dossier dist/SpeechToText/
)
