from os.path import dirname, basename, isfile
import glob

from ..common.helpers import PyClassFromName

modules = glob.glob(dirname(__file__)+"/*.py")

__all__ = [basename(f)[:-3] for f in modules
           if (isfile(f) and
               not basename(f).startswith('_'))]

from . import *


# roll up all the implemented PyGnome classes that are used by our views.
# This will be a list of object types that we can register.
implemented_types = []
for m_name in __all__:
    mod = locals()[m_name]
    if hasattr(mod, 'implemented_types'):
        for t in mod.implemented_types:
            try:
                py_class = PyClassFromName(t)
                implemented_types.append(py_class)
            except ImportError:
                print ('Warning: could not import implemented_type: {}'
                       .format(t))
