#!/usr/bin/env python

"""
    Setup file.
"""
import os
import glob
import shutil
import fnmatch
import htmlmin
from jsmin import jsmin
import ujson
import json

from setuptools import setup, find_packages
from distutils.command.clean import clean
from distutils.command.build_py import build_py as _build_py
from setuptools.command.develop import develop
from setuptools.command.install import install

from git import Repo

# could run setup from anywhere
here = os.path.abspath(os.path.dirname(__file__))

repo = Repo('.')

try:
    branch_name = repo.active_branch.name
except TypeError:
    branch_name = 'no-branch'

last_update = repo.iter_commits().__next__().committed_datetime.isoformat(),

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


class cleanall(clean):
    description = 'cleans files generated by develop mode'

    def run(self):
        # call base class clean
        clean.run(self)

        self.clean_compiled_python_files()
        self.clean_compiled_location_files()

        rm_dir = ['pyGnome.egg-info', 'build']
        for dir_ in rm_dir:
            print("Deleting auto-generated directory: {0}".format(dir_))
            try:
                shutil.rmtree(dir_)
            except OSError as err:
                if err.errno != 2:  # ignore the not-found error
                    raise

    def clean_compiled_python_files(self):
        # clean any byte-compiled python files
        paths = [os.path.join(here, 'webgnome_api'),
                 os.path.join(here, 'location_files')]
        exts = ['*.pyc']

        self.clean_files(paths, exts)

    def clean_compiled_location_files(self):
        # clean any byte-compiled python files
        paths = [os.path.join(here, 'location_files')]
        exts = ['compiled.json']

        self.clean_files(paths, exts)

    def clean_files(self, paths, exts):
        for path in paths:
            # first, any local files directly under the path
            for ext in exts:
                for f in glob.glob(os.path.join(path, ext)):
                    self.delete_file(f)

            # next, walk any sub-directories
            for root, dirs, _files in os.walk(path, topdown=False):
                for d in dirs:
                    for ext in exts:
                        for f in glob.glob(os.path.join(root, d, ext)):
                            self.delete_file(f)

    def delete_file(self, filepath):
        print("Deleting auto-generated file: {0}".format(filepath))
        try:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)
        except OSError as err:
            print(("Failed to remove {0}. Error: {1}"
                  .format(filepath, err)))
            # raise


class compileJSON(_build_py):
    def run(self):
        paths = [os.path.join(here, 'location_files')]
        file_patterns = ['*wizard.json']

        with open(os.path.join(here, 'location_files/style.css'), "r") as css_file:
            for path in paths:
                for pattern in file_patterns:
                    file_list = [os.path.join(dirpath, f)
                                 for dirpath, _dirnames, files in os.walk(path)
                                 for f in fnmatch.filter(files, pattern)]

                    for f in file_list:
                        try:
                            self.parse(f, css_file)
                        except OSError as err:
                            print(("Failed to find {}. Error {}"
                                   .format(f, err)))

            print(("Compiled {0} location(s)".format(len(file_list))))

    def parse(self, path, css):
        if not hasattr(self, 'paths'):
            self.paths = set()

        with open(path, "r") as wizard_json:
            data = wizard_json.read()
            data_obj = ujson.loads(data)

            print(('Compiling location wizard "{}"'.format(data_obj["name"])))

            for step in data_obj["steps"]:
                dirpath = os.path.dirname(path)
                if dirpath not in self.paths:
                    if step["type"] == "custom":
                        self.fill_html_body(data_obj, dirpath, css)
                        self.fill_js_functions(data_obj, dirpath)
                        self.paths.add(dirpath)
                    else:
                        self.write_compiled_json(data_obj, dirpath)

    def fill_js_functions(self, obj, path):
        steps = obj["steps"]
        js_file_list = self.findJS(path)

        for file_path in js_file_list:
            file_parts = file_path.split(os.path.sep)

            # name of the folder 2 levels above our .js file
            filename = file_parts[-3]

            js_file_name = self.grab_filename(file_path)

            for step in steps:
                if step["type"] == "custom" and step["name"] == filename:
                    print(("    Processing {}{}{}.js"
                          .format(os.path.sep.join(file_parts[-5:-1]),
                                  os.path.sep,
                                  js_file_name)))
                    step["functions"][js_file_name] = self.jsMinify(file_path)

        self.write_compiled_json(obj, path)

    def findJS(self, path):
        return [os.path.join(dirpath, f)
                for dirpath, _dirnames, files in os.walk(path)
                for f in fnmatch.filter(files, "*.js")]

    def fill_html_body(self, obj, path, css):
        steps = obj["steps"]
        html_file_list = self.findHTML(path)

        for file_path in html_file_list:
            file_parts = file_path.split(os.path.sep)
            filename = self.grab_filename(file_path)

            for step in steps:
                if step["type"] == "custom" and step["name"] == filename:
                    print(("    Processing {}{}{}.html"
                          .format(os.path.sep.join(file_parts[-5:-1]),
                                  os.path.sep,
                                  filename)))
                    step["body"] = self.htmlMinify(file_path, css)

        self.write_compiled_json(obj, path)

    def findHTML(self, path):
        return [os.path.join(dirpath, f)
                for dirpath, _dirnames, files in os.walk(path)
                for f in fnmatch.filter(files, "*.html")]

    def grab_filename(self, path):
        return os.path.basename(path).split(".")[0]

    def htmlMinify(self, path, css):
        with open(path, "r") as myfile:
            css.seek(0)

            css_content = css.read()
            html_content = myfile.read()

            data = "<style>" + css_content + "</style>" + html_content

            return htmlmin.minify(data)

    def jsMinify(self, path):
        with open(path, "r") as myfile:
            return jsmin(myfile.read())

    def write_compiled_json(self, obj, path):
        with open(path + "/compiled.json", 'w+') as f:
            json.dump(obj, f, indent=4)


class DevelopAll(develop, compileJSON):
    description = ('Installs some additional things that the canned command '
                   'does not')

    def run(self):
        if not self.uninstall:
            compileJSON.run(self)

        develop.run(self)


class InstallAll(install, compileJSON):
    description = ('Installs some additional things that the canned command '
                   'does not')

    def run(self):
        compileJSON.run(self)
        install.run(self)


setup(name='webgnome_api',
      version=0.1,
      description=('webgnome_api\n'
                   'Branch: {}\n'
                   'LastUpdate: {}'
                   .format(branch_name, last_update)),
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
      cmdclass={'cleanall': cleanall,
                'develop': DevelopAll,
                'install': InstallAll,
                'compilejson': compileJSON
                },
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='webgnome_api',
      entry_points=('[paste.app_factory]\n'
                    '  main = webgnome_api:main\n'
                    '[paste.server_factory]\n'
                    '  srv = webgnome_api:server_factory\n'),
      )
