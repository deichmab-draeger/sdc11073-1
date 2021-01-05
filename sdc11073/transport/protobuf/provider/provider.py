from concurrent import futures
import logging
import threading
import time
import grpc
from org.somda.sdc.proto.model import sdc_services_pb2_grpc
from .getservice import GetService
from .setservice import SetService
from ....sdcdevice import intervaltimer

class SdcDevice(object):
    def __init__(self, ws_discovery, my_uuid, model, device, deviceMdibContainer, validate=True, roleProvider=None, sslContext=None,
                 logLevel=None, max_subscription_duration=7200, log_prefix='',
                 chunked_messages=False): #pylint:disable=too-many-arguments
        # ssl protocol handling itself is delegated to a handler.
        # Specific protocol versions or behaviours are implemented there.
        # if handler_cls is None:
        #     handler_cls = SdcHandler_Full
        # self._handler = handler_cls(my_uuid, ws_discovery, model, device, deviceMdibContainer, validate,
        #                         roleProvider, sslContext, logLevel, max_subscription_duration,
        #                         log_prefix=log_prefix, chunked_messages=chunked_messages)
        self._wsdiscovery = ws_discovery
        #self._logger = self._handler._logger
        self._mdib = deviceMdibContainer
        self._location = None
        self._server = None
        self._server_thread = None
        self._rtSampleSendThread = None
        self.collectRtSamplesPeriod = 0.1  # in seconds
        self.get_service = GetService(self._mdib)
        self.set_service = SetService(self._mdib)

    def startAll(self, startRealtimeSampleLoop=True, shared_http_server=None):
        # if self.product_roles is not None:
        #     self.product_roles.initOperations(self._mdib, self._scoOperationsRegistry)
        self._server_thread = threading.Thread(target=self._serve, name='grpc_server')
        self._server_thread.daemon = True
        self._server_thread.start()

        if startRealtimeSampleLoop:
            self._runRtSampleThread = True
            self._rtSampleSendThread = threading.Thread(target=self._rtSampleSendLoop, name='DevRtSampleSendLoop')
            self._rtSampleSendThread.daemon = True
            self._rtSampleSendThread.start()

    def stopAll(self, closeAllConnections=True, sendSubscriptionEnd=True):
        if self._rtSampleSendThread is not None:
            self._runRtSampleThread = False
            self._rtSampleSendThread.join()
            self._rtSampleSendThread = None

    def _serve(self):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        sdc_services_pb2_grpc.add_GetServiceServicer_to_server(self.get_service, self._server)
        sdc_services_pb2_grpc.add_SetServiceServicer_to_server(self.set_service, self._server)
        self._server.add_insecure_port('[::]:50051')
        self._server.start()
        print('server started')
        self._server.wait_for_termination()
        print('server terminated')

    def _rtSampleSendLoop(self):
        time.sleep(0.1)  # start delayed in order to have a fully initialized device when waveforms start
        timer = intervaltimer.IntervalTimer(periodInSeconds=self.collectRtSamplesPeriod)
        while self._runRtSampleThread:
            behind_schedule_seconds = timer.waitForNextIntervalBegin()
            changed_samples = self._mdib.getUpdatedDeviceRtSamples()
            if len(changed_samples) > 0:
                self._logWaveformTiming(behind_schedule_seconds)
                self.sendWaveformUpdates(changed_samples)

# if __name__ == '__main__':
#     logging.basicConfig()
#     serve()
