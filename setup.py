from distutils.core import setup
import py2exe

setup(name="BibEd",
      windows=[{'script':'bibEditor.py'}]
      )
