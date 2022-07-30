block_cipher = None
from kivy.tools.packaging.pyinstaller_hooks import get_deps_all, hookspath, runtime_hooks, get_deps_minimal



a = Analysis(['Picturess.py'],
             pathex=['../testpackaging'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             hookspath=hookspath(),
             runtime_hooks=runtime_hooks(),
             **get_deps_all())


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Picturess',
          debug=False,
          strip=False,
          upx=True,
          console=False )


coll = COLLECT(exe, Tree('.'),
               #Tree('/Library/Frameworks/SDL2.framework/Versions/A/Frameworks/FreeType.framework'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               codesign_identity='Picturess_Josue',
               name='Picturess')

app = BUNDLE(coll,
             name='Picturess.app',
             icon='logo.ico',
         bundle_identifier=None)