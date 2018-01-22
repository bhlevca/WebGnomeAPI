"""
Views for the Outputter objects.
"""
import os
import ujson

from pyramid.httpexceptions import HTTPBadRequest
from cornice import Service

from ..common.common_object import get_session_dir
from ..common.views import (get_object,
                            create_object,
                            update_object,
                            cors_policy,
                            cors_exception)

outputter = Service(name='outputter', path='/outputter*obj_id',
                    description="Outputter API", cors_policy=cors_policy)

implemented_types = ('gnome.outputters.outputter.Outputter',
                     'gnome.outputters.renderer.Renderer',
                     'gnome.outputters.netcdf.NetCDFOutput',
                     'gnome.outputters.geo_json.TrajectoryGeoJsonOutput',
                     'gnome.outputters.json.SpillJsonOutput',
                     'gnome.outputters.json.CurrentJsonOutput',
                     'gnome.outputters.weathering.WeatheringOutput',
                     'gnome.outputters.json.IceJsonOutput',
                     'gnome.outputters.image.IceImageOutput',
                     'gnome.outputters.kmz.KMZOutput',
                     'gnome.outputters.shape.ShapeOutput'
                     )


@outputter.get()
def get_outputter(request):
    '''Returns a Gnome Outputter object in JSON.'''
    return get_object(request, implemented_types)


@outputter.post()
def create_outputter(request):
    '''Creates a Gnome Outputter object.'''
    request = process_outputter(request, True)
    return create_object(request, implemented_types)


@outputter.put()
def update_outputter(request):
    '''Updates a Gnome Outputter object.'''
    request = process_outputter(request)
    return update_object(request, implemented_types)


def setup_output(request, obj_type, clean_dir):
    session_dir = get_session_dir(request)
    outputter_path = os.path.join(session_dir, 'output', obj_type, '')

    if not os.path.isdir(outputter_path):
        os.makedirs(outputter_path)

    if clean_dir:
        for f in os.listdir(outputter_path):
            file_path = os.path.join(outputter_path, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
    return outputter_path


def process_outputter(request, clean_dir=False):
    try:
        json_request = ujson.loads(request.body)
    except:
        raise cors_exception(request, HTTPBadRequest)

    obj_type = json_request['obj_type']
    output_dir = setup_output(request, obj_type, clean_dir)

    if obj_type == 'gnome.outputters.netcdf.NetCDFOutput':
        json_request['netcdf_filename'] = os.path.join(output_dir,
                                                       json_request['name'])
    else:
        json_request['filename'] = os.path.join(output_dir,
                                                json_request['name'])

    request.body = ujson.dumps(json_request)

    return request
