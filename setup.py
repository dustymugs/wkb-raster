"""
WKB-Raster
----------

Read WKB rasters to Numpy arrays.

Links
`````

* `Docs <https://github.com/nathancahill/wkb-raster>`_
* `Raster WKB RFC
  <http://trac.osgeo.org/postgis/browser/trunk/raster/doc/RFC2-WellKnownBinaryFormat>`_
* `GitHub <https://github.com/nathancahill/wkb-raster>`_

"""
from setuptools import setup

test_requires = [
    'nose2'
]

dev_requires = [
    'flake8',
    'nose2[coverage_plugin]>=0.6.5'
]

setup(
    name='WKB-Raster',
    version='0.7.0',
    url='',
    license='MIT',
    author='',
    author_email='',
    description='Read/Write WKB rasters',
    long_description=__doc__,
    packages=['wkb_raster'],
    install_requires=['numpy'],
    extras_require={
        'test': test_requires,
        'dev': test_requires + dev_requires
    }
)
