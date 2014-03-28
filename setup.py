from distutils.core import setup
import py2exe

setup(name="BibEd",
      options={'py2exe': {'optimize': 2}},
      windows=[{'script':'bibEditor.py'}],
      zipfile=None,
      )
