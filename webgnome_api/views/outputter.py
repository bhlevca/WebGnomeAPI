"""
Views for the Outputter objects.
"""
import os
import ujson
from webgnome_api.common.common_object import get_session_dir
from webgnome_api.common.views import (get_object,
                                       create_object,
                                       update_object,
                                       cors_policy)

from cornice import Service

outputter = Service(name='outputter', path='/outputter*obj_id',
                    description="Outputter API", cors_policy=cors_policy)

implemented_types = ('gnome.outputters.outputter.Outputter',
                     'gnome.outputters.renderer.Renderer',
                     'gnome.outputters.netcdf.NetCDFOutput',
                     'gnome.outputters.geo_json.TrajectoryGeoJsonOutput',
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
    request = process_outputter(request)
    print(request)
    return create_object(request, implemented_types)


@outputter.put()
def update_outputter(request):
    '''Updates a Gnome Outputter object.'''
    request = process_outputter(request)
    return update_object(request, implemented_types)


def setup_output(request, obj_type):
    session_dir = get_session_dir(request)
    outputter_path = session_dir + os.path.sep + 'output' + os.path.sep + obj_type + os.path.sep
    print(outputter_path)

    if not os.path.isdir(outputter_path):
        os.makedirs(outputter_path)

    return outputter_path


def check_path_equality(path1, path2):
    head1, tail1 = os.path.split(path1)
    head2, tail2 = os.path.split(path2)

    if head1 == head2:
        return True
    else:
        return False


def process_outputter(request):
    json_request = ujson.loads(request.body)
    obj_type = json_request['obj_type']
    output_dir = setup_output(request, obj_type)

    if obj_type == 'gnome.outputters.netcdf.NetCDFOutput':
        if not check_path_equality(output_dir, json_request['netcdf_filename']):
            json_request['netcdf_filename'] = output_dir + json_request['netcdf_filename']
    else:
        if not check_path_equality(output_dir, json_request['filename']):
            json_request['filename'] = output_dir + json_request['filename']

    request.body = ujson.dumps(json_request)

    return request
