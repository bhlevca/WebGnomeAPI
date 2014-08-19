"""
    Setup file.
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

requires = ['cornice',
            'waitress',
            'WebTest',
            'webhelpers2>=2.0b5',
            'pyramid_redis_sessions>=1.0a1',
            'GDAL']


setup(name='webgnome_api',
      version=0.1,
      description='webgnome_api',
      long_description=README,
      classifiers=["Programming Language :: Python",
                   "Framework :: Pylons",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
                   ],
      keywords="adios gnome oilspill weathering trajectory modeling",
      author='ADIOS/GNOME team at NOAA ORR',
      author_email='orr.gnome@noaa.gov',
      url='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite='webgnome_api',
      entry_points=('[paste.app_factory]\n'
                    '  main = webgnome_api:main\n'),
)
