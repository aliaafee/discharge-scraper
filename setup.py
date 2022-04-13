from distutils.core import setup
import py2exe

packages=[
    'docx2txt'
]

setup(
    name="extract_log_book",
    windows = [
        {
            "script": 'extract_log_book.py'
        }
    ],
    options={'py2exe': {'bundle_files': 1, 'compressed': True, "packages": packages}},
    zipfile = None
)