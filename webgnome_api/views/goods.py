"""
Views for the GOODS interface.
"""
import multiprocessing
import os
import sys
import threading
import time
import shutil
import urllib.request
import logging
import datetime
import pickle
from uuid import uuid1
from multiprocessing import Process

import ujson
import numpy as np

import shapely.wkt as wkt
from shapely.geometry import Polygon

from cornice import Service

from pyramid.httpexceptions import (HTTPRequestTimeout,
                                    HTTPInsufficientStorage,
                                    HTTPBadRequest)

from ..common.system_resources import (get_free_space,
                                       write_bufread_to_file)

from ..common.common_object import (get_session_dir,)

from ..common.session_management import (get_session_objects,
                                         register_exportable_file)

from ..common.views import (switch_to_existing_session,
                            gen_unique_filename,
                            cors_exception,
                            cors_policy,
                            cors_response)

log = logging.getLogger(__name__)

import pandas as pds
try:
    from libgoods import maps, api
except ImportError:
    print("libgoods package not available -- its functionality will not be there")


from .. import supported_ocean_models, supported_met_models

goods_maps = Service(name='maps', path='/goods/maps*',
                     description="GOODS MAP API", cors_policy=cors_policy)

goods_currents = Service(name='currents', path='/goods/currents*',
                         description="GOODS CURRENTS API",
                         cors_policy=cors_policy)

goods_list_models = Service(name='list_models', path='/goods/list_models*',
                            description="GOODS METADATA API",
                            cors_policy=cors_policy)

goods_requests = Service(name='goods_requests', path='/goods_requests*',
                         description="GOODS REQUESTS API",
                         cors_policy=cors_policy)


@goods_list_models.get()
def get_model_metadata(request):
    '''
    gets set of metadata for all available models

    If map_bounds is set, only models that intersect those
    bounds will be returned.

    map_bounds is a polygon as a list of lon, lat pairs
    '''
    bounds = request.GET.get('map_bounds', None)
    model_id = request.GET.get('model_id', None)
    model_source = request.GET.get('model_source', None)
    request_type = request.GET.get('request_type')
    try:
        if any(cur in request_type for cur in ('surface currents', '3D currents')):
            supported_env_models = supported_ocean_models
        elif 'surface winds' in request_type:
            supported_env_models = supported_met_models
        else:
            supported_env_models = {}
    except TypeError:
        supported_env_models = {**supported_ocean_models, **supported_met_models}
    retval = None
    #model_list = list(supported_env_models.keys())
    if bounds:
        bounds = ujson.loads(bounds)
    if model_id:
        mdl = api.get_model_info(model_id,model_source)
        return mdl
    else:
        retval = api.list_models(
            model_ids_sources=supported_env_models,
            map_bounds=bounds,
            env_params=ujson.loads(request_type),
            as_pyson=True,
            )
    return retval


@goods_maps.post()
def get_goods_map(request):
    '''
    Uses the payload passed by the client to make a .bna download request
    from GOODS.
    This file is then used to create a map object, which is then returned
    to the client

    Example post:
    req_params = {'err_placeholder':'',
                  'NorthLat': 47.06693175688763,
                  'WestLon': -124.26942110656861,
                  'EastLon': -123.6972360021842,
                  'SouthLat': 46.78488364986247,
                  'xDateline': 0,
                  'resolution': 'i',
                  'submit': 'Get Map',
                  }
    '''

    params = request.POST

    # In the future, the webgnome API should be a closer match
    # to the libgoods api.
    max_upload_size = eval(request.registry.settings['max_upload_size'])
    bounds = ((float(params['WestLon']), float(params['SouthLat'])),
              (float(params['EastLon']), float(params['NorthLat'])))

    try:
        fn, contents = maps.get_map(
            bounds=bounds,
            resolution=params['resolution'],
            shoreline=params['shoreline'],
            cross_dateline=bool(int(params['xDateline'])),
            max_filesize=max_upload_size,
        )

    except api.FileTooBigError:
        raise cors_response(request,
                            HTTPBadRequest('file is too big!  Max size = {}'
                                           .format(max_upload_size)))

    size = len(contents)

    upload_dir = os.path.relpath(get_session_dir(request))

    if size >= get_free_space(upload_dir):
        raise cors_response(request,
                            HTTPInsufficientStorage('Not enough space '
                                                    'to save the file'))

    file_name, unique_name = gen_unique_filename(fn, upload_dir)

    file_path = os.path.join(upload_dir, unique_name)

    log.info('Registering filename ' + file_path)
    register_exportable_file(request, file_name, file_path)

    with open(file_path, 'w') as fp:
        fp.write(contents)

    log.info('Successfully uploaded file "{0}"'.format(file_path))

    return file_path, file_name


def create_goods_request(request):
    '''
    Uses the payload passed by the client to send information to
    libGOODS. This file returned from libgoods is then used to create a
    CurrentMover object, which is then returned to the client
    '''
    '''
    class FetchConfig:
        """Configuration data class for fetching."""

        model_name: str
        output_pth: Path
        start: pd.Timestamp
        end: pd.Timestamp
        bbox: Tuple[float, float, float, float]
        source: str
        standard_names: List[str] = field(default_factory=lambda: STANDARD_NAMES)
        surface_only: bool = False
    '''

    log_prefix = 'req{0}: get_currents()'.format(id(request))
    log.info('>>' + log_prefix)

    params = request.POST
    upload_dir = os.path.relpath(get_session_dir(request))
    max_upload_size = eval(request.registry.settings['max_upload_size'])
    bounds = (float(params['WestLon']), float(params['SouthLat']),
              float(params['EastLon']), float(params['NorthLat']))
    surface_only = params.get('surface_only', True) not in ('false', 'False', None)
    cross_dateline = params['cross_dateline'] in ('Yes',)
    request_type = params['request_type']
    tshift = params['tshift']

    include_winds = params.get('include_winds', True) not in ('false', 'False', None)
    if include_winds:
        request_type = [request_type, 'surface winds']

    #generate a unique model output name
    start = params['start_time']
    end = params['end_time']
    fname = params['model_name'] + '_' + start.split('T')[0] + '_' + end.split('T')[0] + '.nc'
    file_name, unique_name = gen_unique_filename(fname, upload_dir)
    output_path = os.path.join(upload_dir, unique_name)
    with open(output_path,'w') as fn:
        pass
    source=params.get('source')

    session_objs = get_session_objects(request)
    request_id = str(uuid1())

    goods_req = GOODSRequest(start_time=datetime.datetime.now(),
                                  request_id=request_id,
                                  filename=unique_name,
                                  outpath=output_path,
                                  request_type=request_type,
                                  request_args={
                                      'model_id':params['model_name'],
                                      'model_source':source,
                                      'start':start,
                                      'end':end,
                                      'bounds':bounds,
                                      'surface_only':surface_only,
                                      'cross_dateline':cross_dateline,
                                      'environmental_parameters':request_type,
                                  },
                                  tshift=tshift,
                                  _debug = False)

    session_objs[request_id] = goods_req
    goods_req.start()

    return goods_req


@goods_requests.post()
def goods_request(request):
    '''
    This route is used to create, cancel or reconfirm requests
    returns the updated request object
    '''

    log_prefix = 'req{0}: interact_request() {1}'.format(id(request), request.POST.get('command', 'NO COMMAND'))
    log.info('>>' + log_prefix)

    params = request.POST
    command = params.get('command', 'None')

    req_id = session_objs = req_obj = None
    if command != 'create':
        req_id = params.get('request_id',None)
        session_objs = get_session_objects(request)
        req_obj = session_objs.get(req_id, None)

    if command == 'create':
        new_req = create_goods_request(request)
        return new_req.to_response()

    elif command == 'cancel':
        req_obj.cancel_request()
        return req_obj.to_response()

    elif command == 'reconfirm':
        req_obj.reconfirm()
        return req_obj.to_response()

    elif command == '_debugPause':
        req_obj._debugPause()
        return req_obj.to_response()

    elif command == 'outpath':
        if req_obj.state != 'finished':
            raise ValueError('Request {0} is not finished'.format(req_obj.request_id))
        else:
            return req_obj.outpath

    elif command == 'cleanup':
        #if for some reason the client wants to wipe one or all requests
        if req_id == 'all':
            for obj in session_objs.values():
                if isinstance(obj, GOODSRequest):
                    log.info('Batch-remove GOODS request {0}'.format(obj.request_id))
                    session_objs[obj.request_id].dead()
                    del session_objs[obj.request_id]
        else:
            obj = session_objs.get(req_id, None)
            if not obj:
                return
            log.info('Removing GOODS request {0}'.format(obj.request_id))
            del session_objs[obj.request_id]

    else:
        raise ValueError('Unrecognized command ({0}) to goods_request interface'.format(command))


@goods_requests.get()
def get_goods_requests(request):
    '''
    If the client needs to request all currently open GOODS requests this is the function
    that handles it.

    returns to the client a jsonified list of GOODSRequest objects
    '''

    log_prefix = 'req{0}: get_currents()'.format(id(request))
    log.info('>>' + log_prefix)
    session_objs = get_session_objects(request)

    params = request.GET
    if params.get('id', None) and params['id'] in session_objs:
        #if GET is provided a single request_id, it will return only that request
        return session_objs['request_id'].to_response()

    all_requests = [v for k, v in session_objs.items() if isinstance(v, GOODSRequest)]
    open_requests = [r for r in all_requests if r.state != 'dead']

    typ = request.GET.get('request_type', None)
    rv = None
    if typ:
        rv = [r.to_response() for r in open_requests if typ in r.request_type]
    else:
        rv = [r.to_response() for r in open_requests]

    for idx, r in enumerate(open_requests):
        log.info('>>>>>Req' + r.request_id + ' subset ' + str(r.subset_process.is_alive()))
    return rv




class GOODSRequest(object):
    '''
    Manages a GOODS data subset operation and progress tracking

    This object is intended to be created inside a request handler and put into
    the session objects dict. This provides management and persistence.

    This object has 6 primary states: 'preparing', 'subsetting', 'requesting', 'too_large', 'error', and 'dead'.
    It is initialized in the 'preparing' state, and goes to the 'subsetting' state after
    calling the relevant method.
    '''
    def __init__(self,
                 request_id=None,
                 start_time=None,
                 request_type=None,
                 request_args=None,
                 filename=None,
                 outpath=None,
                 tshift=0,
                 _debug=False,
                 _max_size=100000000, #100 MB
                 _reconfirm_timeout=300,
                 ):
        '''
        Object to represent an open asynchronous file retrieval.
        '''
        if start_time is None:
            start_time = datetime.datetime.now()
        self.start_time = start_time
        self.request_id = request_id
        self.request_type = request_type #'currents' or 'winds'
        self.request_args = request_args
        self.state = 'preparing'
        self.request_greenlet = None
        self.subset_size = None
        self.filename = filename
        self.outpath = outpath
        self.tshift = int(tshift)
        self._debug = _debug
        self._max_size = _max_size
        self._reconfirm_timeout = _reconfirm_timeout
        self.percent = 0
        self.message = None #set by worker thread
        self.request_process = None
        self.pause_event = threading.Event() #lock for main thread to clear on reconfirmation
        self.cancel_event = threading.Event() #event for main thread to set if cancellation desired
        self.cancel_event.clear()
        self.complete_event = threading.Event() #event for worker thread to set when request is complete
        self.complete_event.clear()

    def to_response(self):
        return {'start_time': self.start_time.isoformat(),
               'request_id': self.request_id, #GOODSRequest do not have an 'id' as a distinction from GnomeId
               'id': self.request_id, #'id' specifically needed by Backbone.Collection so merging works right
               'request_type': self.request_type,
               'filename': self.filename,
               'state': self.state,
               'size': self.subset_size,
               'percent': self.percent,
               'message': self.message,
               'outpath': self.outpath,
               'tshift': self.tshift}

    @property
    def subset_xr(self):
        if not self._subset_finished:
            raise ValueError('Subset operation not completed')
        else:
            return self._subset_xr

    @subset_xr.setter
    def subset_xr(self, subs):
        if not self._subset_finished:
            raise ValueError('Subset operation not completed')
        else:
            self._subset_xr = subs

    def start(self):
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(multiprocessing.SUBDEBUG)
        if self.state != 'preparing':
            msg = 'Subset operation {0} already started or completed'.format(self.request_id)
            log.error(msg)
            return msg
        self.state = 'subsetting'
        self._subset_finished = False

        message_queue = multiprocessing.Queue()
        message_queue.write = message_queue.put
        self.request_thread = threading.Thread(
            target=self._thread_request_func,
            args=(self.request_args, logger, message_queue),
            daemon=True
        )
        self.request_thread.start()

    def _thread_request_func(self, request_args, logger, mq):
        logger.info('START')
        self.subset_process = Process(target=subset_process_func, args=(request_args, mq), daemon=True)
        self.subset_process.start()
        msg = '0%'
        while '%' in msg:
            logger.debug('SUBSET PROGESS: ' + msg)
            msg = mq.get()
            if msg == 'success' or msg == 'error':
                break
            msg = msg + '%'
        status = msg
        result = mq.get(timeout=1)
        self.subset_process.join()

        if self.cancel_event.is_set():
            self.message = 'Cancelled'
            return
        if self.subset_process.exitcode:
            logger.info('SUBSET FAILED: exitcode' + str(self.subset_process.exitcode))
        if status:
            logger.info('SUBSET COMPLETE')
            logger.info(str(status))
            self._subset_xr = pickle.loads(result)
            logger.info(str(self._subset_xr))
        else:
            self.message = status
            self.error(result)

        self._subset_finished=True
        self.percent = 0
        self.subset_size = self._subset_xr.nbytes
        if self.subset_size > self._max_size:
            self.too_large()

        if self.cancel_event.is_set():
            self.message = 'Cancelled'
            return
        self.state = 'requesting'
        self.request_process = Process(target=api.get_model_output, args=(self._subset_xr, self.outpath))
        self.request_process.start()
        self.request_process.join()
        if self.request_process.exitcode:
            logger.info('REQUEST FAILED: exitcode ' + str(self.request_process.exitcode))
        logger.info('REQUEST COMPLETE')
        if self.cancel_event.is_set():
            self.message = 'Cancelled'
            return

        self._request_finished = True
        self.state = 'finished'
        self.percent = 100
        self.complete_event.set()

    def too_large(self):
        size = self._subset_xr.nbytes
        self.state = 'too_large'
        self.message = 'Subset size is very large ({0}). Reconfirm required.'.format(size)
        self.pause_event.clear()
        if not self.pause_event.wait(timeout=self._reconfirm_timeout):
            self.dead()
            return


    def error(self, msg, exc=None):
        self.state = 'error'
        self.message = msg
        self.exception = exc

    def reconfirm(self):
        if self.state == 'too_large':
            self.state = 'subsetting'
        self.pause_event.set() #releases the waiting request thread

    def dead(self):
        self.cancel_request()

    def _debugPause(self):
        breakpoint()

    def cancel_request(self):
        self.cancel_event.set()
        self.state = 'dead'
        if self.subset_process:
            self.subset_process.terminate()
        if self.request_process:
            self.request_process.terminate()
        monitor_thread = threading.Thread(target=self._deathwatch, daemon=True)
        monitor_thread.start()

    def _deathwatch(self):
        self.request_thread.join(timeout=self._reconfirm_timeout)
        if self.request_thread.is_alive():
            print('REQUEST CANCELLATION FAILED')

    def test_no_thread(self):
        from dask.diagnostics import ProgressBar, Profiler
        breakpoint()
        with Profiler() as pb:
            subs = api.get_model_file(**self.request_args)
            pb.visualize()

        with ProgressBar() as pb:
            api.get_model_output(subs, self.outpath)



from dask.callbacks import Callback
from timeit import default_timer
class Tracker(Callback):
    def __init__(self, model, dt=1, timeout=60):
        self.dt = 1
        self.timeout = timeout
        self.model = model
        self.timer_greenlet = None

    def _start(self, dsk):
        self.state = None
        self.start_time = default_timer()
        self.running = True
        self.timer_thread = threading.Thread(
            target=self._timer_func,
            name='TimerThread' + self.model.request_id,
            daemon=True,
            )
        self.timer_thread.start()

    def _pretask(self, key, dsk, state):
        self.state = state

    def _finish(self, dsk, state, errored):
        self._running = False
        self.timer.join()
        elapsed = default_timer() - self.start_time
        self.last_duration = elapsed
        if not errored:
            self.model.percent = 100
            self.model.elapsed = elapsed
        else:
            raise errored

    def _timer_func(self):
        while self.running:
            elapsed = default_timer() - self.start_time
            if elapsed > self.dt:
                self._update(elapsed)
            time.sleep(self.dt)

    def _update(self, elapsed):
        s = self.state
        if not s: #tracker was not attached to dask correctly
            self.model.percent = 0
            return
        ndone = len(s["finished"])
        ntasks = sum(len(s[k]) for k in ["ready", "waiting", "running"]) + ndone
        pct = int(ndone / ntasks if ntasks else 0)

        if ndone < ntasks:
            self.model.percent = pct
            self.model.elapsed = elapsed

def subset_process_func(request_args, mq):
    try:
        result = api.get_model_subset(**request_args)
        mq.put('success', timeout=1)
        mq.put(pickle.dumps(result), timeout=1)
    except Exception as e:
        mq.put('error', timeout=1)
        mq.put(str(e), timeout=1)
        raise e