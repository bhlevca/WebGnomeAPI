"""
    Setup file.
"""
import os
import shutil
import fnmatch
import htmlmin
from jsmin import jsmin
import ujson
import json
import re

from setuptools import setup, find_packages
from distutils.command.clean import clean
from distutils.command.build_py import build_py as _build_py
from setuptools.command.develop import develop as base_develop

# could run setup from anywhere
here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


class cleandev(clean):
    description = 'cleans files generated by develop mode'

    def run(self):
        # call base class clean
        clean.run(self)

        # clean auto-generated files
        paths = [os.path.join(here, 'webgnome_api'),
                 ]
        file_patterns = ['*.pyc']

        for path in paths:
            for pattern in file_patterns:
                file_list = [os.path.join(dirpath, f)
                             for dirpath, dirnames, files in os.walk(path)
                             for f in fnmatch.filter(files, pattern)]

                for f in file_list:
                    try:
                        os.remove(f)
                        print "Deleted auto-generated file: {0}".format(f)
                    except OSError as err:
                        print ("Failed to remove {0}. Error: {1}"
                               .format(f, err))

        rm_dir = ['webgnome_api.egg-info']
        for dir_ in rm_dir:
            try:
                shutil.rmtree(dir_)
                print "Deleted auto-generated directory: {0}".format(dir_)
            except OSError as err:
                if err.errno != 2:
                    # we report everything except file not found.
                    print ("Failed to remove {0}. Error: {1}"
                           .format(dir_, err))


class compileJSON(_build_py):

    def run(self):
        paths = [os.path.join(here, 'location_files')]
        file_patterns = ['*wizard.json']

        with open(os.path.join(here, 'css/less/style.css'), "r") as css_file:
            for path in paths:
                for pattern in file_patterns:
                    file_list = [os.path.join(dirpath, f)
                                 for dirpath, dirnames, files in os.walk(path)
                                 for f in fnmatch.filter(files, pattern)]

                    for f in file_list:
                        try:
                            self.parse(self, f, css_file)
                        except OSError as err:
                            print ("Failed to find {0}. Error {1}".format(f, err))

    def parse(self, obj, path, css):
        with open(path, "r") as wizard_json:
            data = unicode(wizard_json.read(), "utf-8")
            data_obj = ujson.loads(data)
            for key in data_obj:
                if key == "steps":
                    for step in data_obj[key]:
                        dirpath = os.path.dirname(path)
                        if step["type"] == "custom":
                            self.fill_html_body(data_obj, dirpath, css)
                            self.fill_js_functions(data_obj, dirpath)
                        else:
                            self.write_compiled_json(data_obj, dirpath)

    def findHTML(self, obj, path):
        html_files = [os.path.join(dirpath, f) for dirpath, dirnames, files in os.walk(path) for f in fnmatch.filter(files, "*.html")]
        return sorted(set(html_files))

    def findJS(self, obj, path):
        js_files = [os.path.join(dirpath, f) for dirpath, dirnames, files in os.walk(path) for f in fnmatch.filter(files, "*.js")]
        return js_files

    def fill_js_functions(self, obj, path):
        steps = obj["steps"]
        js_file_list = self.findJS(obj, path)
        for file_path in js_file_list:
            filename = os.path.basename(os.path.dirname(file_path).split("/js")[0])
            js_file_name = self.grab_filename(file_path)
            for step in steps:
                if step["type"] == "custom" and step["name"] == filename:
                    step["functions"][js_file_name] = self.jsMinify(file_path)
        self.write_compiled_json(obj, path)

    def fill_html_body(self, obj, path, css):
        steps = obj["steps"]
        html_file_list = self.findHTML(obj, path)
        for file_path in html_file_list:
            filename = self.grab_filename(file_path)
            for step in steps:
                if step["type"] == "custom" and step["name"] == filename:
                    step["body"] = self.htmlMinify(file_path, css)
        self.write_compiled_json(obj, path)

    def grab_filename(self, path):
        return os.path.basename(path).split(".")[0]

    def htmlMinify(self, path, css):
        with open(path, "r") as myfile:
            css.seek(0)
            css_read = unicode(css.read(), "utf-8")
            data = u"<style>" + css_read + u"</style>" + unicode(myfile.read(), "utf-8")
            return self.remove_head_tags(htmlmin.minify(data))

    def remove_head_tags(self, string):
        html_re = re.compile(r'<body[^>]*\>(.*)\<\/body', re.S)
        parsed_str = html_re.search(string).group(1)
        return parsed_str

    def jsMinify(self, path):
        with open(path, "r") as myfile:
            data = unicode(myfile.read(), "utf-8")
            return jsmin(data)

    def write_compiled_json(self, obj, path):
        with open(path + "/compiled.json", 'w+') as f:
            json.dump(obj, f, indent=4)


class developall(base_develop, compileJSON):
    description = ''

    def run(self):
        base_develop.run(self)
        compileJSON.run(self)


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
      cmdclass={'cleandev': cleandev,
                'developall': developall,
                'compilejson': compileJSON
                },
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='webgnome_api',
      entry_points=('[paste.app_factory]\n'
                    '  main = webgnome_api:main\n'),
)
