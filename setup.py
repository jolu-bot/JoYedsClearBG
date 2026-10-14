from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'JoYeds.icns',
    'includes': ['PIL', 'rembg', 'tkinter'],
    'packages': ['onnxruntime', 'numpy'],
    'plist': {
        'CFBundleName': 'JoYed\'S ClearBG',
        'CFBundleDisplayName': 'JoYed\'S ClearBG',
        'CFBundleGetInfoString': 'JoYed\'S ClearBG - Powered by JoYed\'S',
        'CFBundleIdentifier': 'com.joyeds.clearbg',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True
    },
}

setup(
    app=APP,
    name='JoYedS ClearBG',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
