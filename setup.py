#+ This file is used  to build Cython's file 
#+ -----------------------------------------

from  setuptools import  setup , Extension 
from  Cython.Build import cythonize
glb  = __import__("glob") 


dirent_structure :dict[str:str]  = {
        "package_source_dir": "src/"
        }

pyheat2d_srcs =  glb.glob(f"{dirent_structure.__getitem__('package_source_dir')}*.py") 

extensions_build = cythonize([
    Extension(
        "*",
        sources=["src/*.pyx"],
        #--- For later  --- 
        #include_dirs=["include"],
        #library_dir=["lib"],
        #library=["lib"]
        )
    ])


setup(
        name="Pyheat2D",   # Package name 
        version="0.0.1a",  # current_version
        ext_modules=extensions_build,
        author="Elhadj Mama Gaye",
        maintainer="Umar Ba",
        maintainer_email="jUmarB@protonmail.com",
        



        platforms=["GNU/linux" ,"MacOSX"]
        )
