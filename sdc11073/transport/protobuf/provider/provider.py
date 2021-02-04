from concurrent import futures
import traceback
import logging
import threading
import time
import grpc
from org.somda.sdc.proto.model import sdc_services_pb2_grpc
from .getservice import GetService
from .setservice import SetService
from .mdibreportingservice import MdibReportingService
from . import subscriptionmgr
from .localizationservice import LocalizationService
from ..msgreader import MessageReader
from .archiveservice import ArchiveService
from ....sdcdevice import intervaltimer
from ....sdcdevice import sco
from sdc11073 import namespaces, pmtypes
from sdc11073.location import SdcLocation
from sdc11073 import loghelper


class GSdcDevice(object):
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
        self._log_prefix = ''
        self._sslContext=None
        self._mdib = deviceMdibContainer
        self._subscriptions_manager = self._mkSubscriptionManager(max_subscription_duration)
        self._location = None
        self._server = None
        self._server_thread = None
        self._rtSampleSendThread = None
        self.collectRtSamplesPeriod = 0.1  # in seconds
        self.get_service = GetService(self._mdib)
        self.set_service = SetService(self._mdib)
        self.mdib_reporting_service = MdibReportingService(self._subscriptions_manager)
        self.localization_service = LocalizationService(self._mdib)
        self.archive_service = ArchiveService(self._mdib)
        self._port_number = None  # ip listen port
        self.epr = 'test_epr'
        self._logger = loghelper.getLoggerAdapter('sdc.device', log_prefix) # logging.getLogger('sdc.device')
        self.msg_reader = MessageReader(self._logger)
        self.product_roles = roleProvider or self._mk_default_role_handlers()

        deviceMdibContainer.setSdcDevice(self)
        self.scoOperationsRegistry = self._mkScoOperationsRegistry(handle='_sco')


    def startAll(self, startRealtimeSampleLoop=True, shared_http_server=None):
        if self.product_roles is not None:
            self.product_roles.initOperations(self._mdib, self.scoOperationsRegistry)
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
        self._subscriptions_manager.stop()

    def start_realtimesample_loop(self):
        if not self._rtSampleSendThread:
            self._runRtSampleThread = True
            self._rtSampleSendThread = threading.Thread(target=self._rtSampleSendLoop, name='DevRtSampleSendLoop')
            self._rtSampleSendThread.daemon = True
            self._rtSampleSendThread.start()

    def stop_realtimesample_loop(self):
        if self._rtSampleSendThread:
            self._runRtSampleThread = False
            self._rtSampleSendThread.join()
            self._rtSampleSendThread = None

    @property
    def mdib(self):
        return self._mdib

    def _serve(self):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        sdc_services_pb2_grpc.add_GetServiceServicer_to_server(self.get_service, self._server)
        sdc_services_pb2_grpc.add_SetServiceServicer_to_server(self.set_service, self._server)
        sdc_services_pb2_grpc.add_MdibReportingServiceServicer_to_server(self.mdib_reporting_service, self._server)
        sdc_services_pb2_grpc.add_LocalizationServiceServicer_to_server(self.localization_service, self._server)
        sdc_services_pb2_grpc.add_ArchiveServiceServicer_to_server(self.archive_service, self._server)
        self._port_number = self._server.add_insecure_port('[::]:50051')
        self._server.start()
        print('server started')
        self._server.wait_for_termination()
        print('server terminated')


    def sendMetricStateUpdates(self, mdibVersion, stateUpdates):
        self._logger.debug('sending metric state updates {}', stateUpdates)
        self._subscriptions_manager.sendEpisodicMetricReport(stateUpdates, self._mdib.nsmapper, mdibVersion,
                                                            self.mdib.sequenceId)

    def sendAlertStateUpdates(self, mdibVersion, stateUpdates):
        self._logger.debug('sending alert updates {}', stateUpdates)
        self._subscriptions_manager.sendEpisodicAlertReport(stateUpdates, self._mdib.nsmapper, mdibVersion,
                                                           self.mdib.sequenceId)

    def sendComponentStateUpdates(self, mdibVersion, stateUpdates):
        self._logger.debug('sending component state updates {}', stateUpdates)
        self._subscriptions_manager.sendEpisodicComponentStateReport(stateUpdates, self._mdib.nsmapper, mdibVersion,
                                                                    self.mdib.sequenceId)

    def sendContextStateUpdates(self, mdibVersion, stateUpdates):
        self._logger.debug('sending context updates {}', stateUpdates)
        self._subscriptions_manager.sendEpisodicContextReport(stateUpdates, self._mdib.nsmapper, mdibVersion,
                                                             self.mdib.sequenceId)

    def sendOperationalStateUpdates(self, mdibVersion, stateUpdates):
        self._logger.debug('sending operational state updates {}', stateUpdates)
        self._subscriptions_manager.sendEpisodicOperationalStateReport(stateUpdates, self._mdib.nsmapper, mdibVersion,
                                                                      self.mdib.sequenceId)

    def sendRealtimeSamplesStateUpdates(self, mdibVersion, stateUpdates):
        self._logger.debug('sending real time sample state updates {}', stateUpdates)
        self._subscriptions_manager.sendRealtimeSamplesReport(stateUpdates, self._mdib.nsmapper, mdibVersion, self.mdib.sequenceId)

    def sendDescriptorUpdates(self, mdibVersion, updated, created, deleted, updated_states):
        self._logger.debug('sending descriptor updates updated={} created={} deleted={}', updated, created, deleted)
        self._subscriptions_manager.sendDescriptorUpdates(updated, created, deleted, updated_states,
                                                         self._mdib.nsmapper,
                                                         mdibVersion,
                                                         self.mdib.sequenceId)

    def _waveform_updates_transaction(self, changedSamples):
        '''
        @param changedSamples: a dictionary with key = handle, value= devicemdib.RtSampleArray instance
        '''
        with self._mdib.mdibUpdateTransaction() as tr:
            for descriptorHandle, changedSample in changedSamples.items():
                determinationTime = changedSample.determinationTime
                samples = [s[0] for s in changedSample.samples]  # only the values without the 'start of cycle' flags
                activationState = changedSample.activationState
                st = tr.getRealTimeSampleArrayMetricState(descriptorHandle)
                if st.metricValue is None:
                    st.mkMetricValue()
                st.metricValue.Samples = samples
                st.metricValue.DeterminationTime = determinationTime  # set Attribute
                st.metricValue.Annotations = changedSample.annotations
                st.metricValue.ApplyAnnotations = changedSample.applyAnnotations
                st.ActivationState = activationState

    def _rtSampleSendLoop(self):
        time.sleep(0.1)  # start delayed in order to have a fully initialized device when waveforms start
        timer = intervaltimer.IntervalTimer(periodInSeconds=self.collectRtSamplesPeriod)
        try:
            while self._runRtSampleThread:
                behind_schedule_seconds = timer.waitForNextIntervalBegin()
                changed_samples = self._mdib.getUpdatedDeviceRtSamples()
                if len(changed_samples) > 0:
                    print(f'_rtSampleSendLoop with {len(changed_samples)} waveforms')
                    #self._logWaveformTiming(behind_schedule_seconds)
                    self._waveform_updates_transaction(changed_samples)
                else:
                    print('_rtSampleSendLoop no data')
            print('_rtSampleSendLoop end')
        except Exception as ex:
            print(traceback.format_exc())

    def publish(self):
        """
        publish device on the network (sends HELLO message)
        :return:
        """
        scopes = self._mkScopes()
        xAddrs = self._getXAddrs()
        self._wsdiscovery.publishService(self.epr, self._mdib.sdc_definitions.MedicalDeviceTypesFilter, scopes, xAddrs)

    def _mkScopes(self):
        scopes = []
        locations = self._mdib.contextStates.NODETYPE.get(namespaces.domTag('LocationContextState'))
        if not locations:
            return scopes
        assoc_loc = [l for l in locations if l.ContextAssociation == pmtypes.ContextAssociation.ASSOCIATED]
        for loc in assoc_loc:
            det = loc.LocationDetail
            dr_loc = SdcLocation(fac=det.Facility, poc=det.PoC, bed=det.Bed, bld=det.Building,
                                 flr=det.Floor, rm=det.Room)
            scopes.append(wsdiscovery.Scope(dr_loc.scopeStringSdc))

        for nodetype, scheme in (
                ('OperatorContextDescriptor', 'sdc.ctxt.opr'),
                ('EnsembleContextDescriptor', 'sdc.ctxt.ens'),
                ('WorkflowContextDescriptor', 'sdc.ctxt.wfl'),
                ('MeansContextDescriptor', 'sdc.ctxt.mns'),
        ):
            descriptors = self._mdib.descriptions.NODETYPE.get(namespaces.domTag(nodetype), [])
            for descriptor in descriptors:
                states = self._mdib.contextStates.descriptorHandle.get(descriptor.Handle, [])
                assoc_st = [s for s in states if s.ContextAssociation == pmtypes.ContextAssociation.ASSOCIATED]
                for st in assoc_st:
                    for ident in st.Identification:
                        scopes.append(wsdiscovery.Scope('{}:/{}/{}'.format(scheme, urllib.parse.quote_plus(ident.Root),
                                                                           urllib.parse.quote_plus(ident.Extension))))

        scopes.extend(self._getDeviceComponentBasedScopes())
        scopes.append(wsdiscovery.Scope('sdc.mds.pkp:1.2.840.10004.20701.1.1'))  # key purpose Service provider
        return scopes

    def _getDeviceComponentBasedScopes(self):
        '''
        SDC: For every instance derived from pm:AbstractComplexDeviceComponentDescriptor in the MDIB an
        SDC SERVICE PROVIDER SHOULD include a URIencoded pm:AbstractComplexDeviceComponentDescriptor/pm:Type
        as dpws:Scope of the MDPWS discovery messages. The URI encoding conforms to the given Extended Backus-Naur Form.
        E.G.  sdc.cdc.type:///69650, sdc.cdc.type:/urn:oid:1.3.6.1.4.1.3592.2.1.1.0//DN_VMD
        After discussion with David: use only MDSDescriptor, VmdDescriptor makes no sense.
        :return: a set of scopes
        '''
        scopes = set()
        for t in (namespaces.domTag('MdsDescriptor'),):
            descriptors = self._mdib.descriptions.NODETYPE.get(t)
            for d in descriptors:
                if d.Type is not None:
                    cs = '' if d.Type.CodingSystem == pmtypes.DefaultCodingSystem else d.Type.CodingSystem
                    csv = d.Type.CodingSystemVersion or ''
                    sc = wsdiscovery.Scope('sdc.cdc.type:/{}/{}/{}'.format(cs, csv, d.Type.Code))
                    scopes.add(sc)
        return scopes

    def _getXAddrs(self):
        return [f'localhost:{self._port_number}'] # for now...
        #xaddrs = self._server

    def _mkSubscriptionManager(self, max_subscription_duration):
        return subscriptionmgr.SubscriptionsManager(self._mdib.sdc_definitions,
                                                    max_subscription_duration,
                                                    log_prefix=self._log_prefix)

    def _mkScoOperationsRegistry(self, handle):
        return sco.ScoOperationsRegistry(self._subscriptions_manager, self._mdib, handle, log_prefix=self._log_prefix)

    def _mk_default_role_handlers(self):
        from sdc11073 import roles
        return roles.product.MinimalProduct(self._log_prefix)
