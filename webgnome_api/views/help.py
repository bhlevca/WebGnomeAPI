"""
Views for help documentation
"""

from cornice import Service
from os import walk
from os.path import sep, join, isfile, isdir
from pyramid.httpexceptions import HTTPNotFound
from docutils.core import publish_parts
import urllib, time, json, redis

from webgnome_api.common.views import cors_exception, cors_policy

help = Service(name='help', path='/help/*dir',
                       description="Help Documentation and Feedback API", cors_policy=cors_policy)


@help.get()
def get_help(request):
    '''Get the requested help file if it exists'''
    help_dir = get_help_dir_from_config(request)
    requested_dir = urllib.unquote(sep.join(request.matchdict.get('dir'))).encode('utf8')

    requested_file = join(help_dir, requested_dir)
    if isfile(requested_file + '.rst'):
        # a single help file was requested
        file = open(requested_file + '.rst', 'r')
        html = publish_parts(file.read(), writer_name='html')['html_body']
        file.close()
        return {'path': requested_file, 'html': html}
    elif isdir(requested_file):
        # a directory was requested
        # aggrigate the files contained with in the given directory and sub dirs.
        for path, dirnames, filenames in walk(requested_file):
            html = ''
            for fname in filenames:
                file = open(join(path, fname), 'r')
                html += publish_parts(file.read(), writer_name='html')['html_body']
                file.close()
            return {'path': requested_file, 'html': html}

    else:
        raise cors_exception(request, HTTPNotFound)

@help.put()
@help.post()
def create_help_feedback(request):
    '''Creates a feedback entry for the given help section'''
    try:
        json_request = json.loads(request.body)
    except:
        raise cors_exception(request, HTTPBadRequest)

    json_request['ts'] = int(time.time())
    client = redis.Redis('localhost')

    if 'index' not in json_request:
        index = client.incr('index')
        json_request['index'] = index

    client.set('feedback' + str(json_request['index']), json_request)
    return json_request

def get_help_dir_from_config(request):
    help_dir = request.registry.settings['help_dir']
    if help_dir[0] == sep:
        full_path = help_dir
    else:
        here = request.registry.settings['install_path']
        full_path = join(here, help_dir)
    return full_path