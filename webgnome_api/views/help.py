"""
Views for help documentation
"""

from cornice import Service
from os.path import sep, join, isfile
from pyramid.httpexceptions import HTTPNotFound
import urllib

from webgnome_api.common.views import cors_exception, cors_policy, cors_file

help = Service(name='help', path='/help/*dir',
                       description="Help Documentation and Feedback API", cors_policy=cors_policy)


@help.get()
def get_help(request):
    '''Get the requested help file if it exists'''
    help_dir = get_help_dir_from_config(request)
    requested_dir = urllib.unquote(sep.join(request.matchdict.get('dir'))).encode('utf8')

    if requested_dir[-5:] != '.html':
        requested_dir = requested_dir + '.html'

    requested_file = join(help_dir, requested_dir)
    
    if isfile(requested_file):
        return cors_file(request, requested_file)
    else:
        raise cors_exception(request, HTTPNotFound)

@help.post()
def create_help_feedback(request):
    '''Creates a feedback entry for the given help section'''



def get_help_dir_from_config(request):
    help_dir = request.registry.settings['help_dir']
    if help_dir[0] == sep:
        full_path = help_dir
    else:
        here = request.registry.settings['install_path']
        full_path = join(here, help_dir)
    return full_path