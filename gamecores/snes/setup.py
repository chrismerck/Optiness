from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

snes = Extension (
    "snes",                         # name of extension
    ["snes.pyx"],                   # filename of our Cython source
    language="c++",                 # this causes Cython to create C++ source
    include_dirs=["/usr/include"],  # usual stuff
    libraries=["snes"],             # ditto
#    extra_link_args=[],             # if needed
    cmdclass = {'build_ext': build_ext}
)

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [snes]
)
