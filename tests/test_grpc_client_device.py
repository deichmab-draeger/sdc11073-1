import unittest
import logging
import os
import time
from sdc11073.transport.protobuf.consumer.consumer import GSdcClient
from sdc11073.transport.protobuf.provider.provider import GSdcDevice
from sdc11073.transport.protobuf.discovery import GDiscovery
from sdc11073.mdib.devicemdib import DeviceMdibContainer
from sdc11073.transport.soap.soapenvelope import DPWSThisModel, DPWSThisDevice
from sdc11073 import namespaces, pmtypes
from sdc11073.transport.protobuf.clientmdib import GClientMdibContainer
from sdc11073.sdcdevice import waveforms
from sdc11073.location import SdcLocation
from org.somda.sdc.proto.model import sdc_messages_pb2


def _start_logger():
    logger = logging.getLogger('pysdc.grpc')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    logging.getLogger('pysdc.grpc.map').setLevel(logging.WARN)

    return ch


def _stop_logger(handler):
    logger = logging.getLogger('pysdc.grpc')
    logger.setLevel(logging.WARNING)
    logger.removeHandler(handler)


class SomeDevice(GSdcDevice):
    """A device used for unit tests

    """
    def __init__(self, wsdiscovery, my_uuid, mdib_xml_string,
                 validate=True, sslContext=None, logLevel=logging.INFO, log_prefix='',
                 chunked_messages=False):
        model = DPWSThisModel(manufacturer='Draeger CoC Systems',
                              manufacturerUrl='www.draeger.com',
                              modelName='SomeDevice',
                              modelNumber='1.0',
                              modelUrl='www.draeger.com/whatever/you/want/model',
                              presentationUrl='www.draeger.com/whatever/you/want/presentation')
        device = DPWSThisDevice(friendlyName='Py SomeDevice',
                                firmwareVersion='0.99',
                                serialNumber='12345')
#        log_prefix = '' if not ident else '<{}>:'.format(ident)
        device_mdib_container = DeviceMdibContainer.fromString(mdib_xml_string, log_prefix=log_prefix)
        # set Metadata
        mds_descriptor = device_mdib_container.descriptions.NODETYPE.getOne(namespaces.domTag('MdsDescriptor'))
        mds_descriptor.MetaData.Manufacturer = [pmtypes.LocalizedText(u'Dräger')]
        mds_descriptor.MetaData.ModelName = [pmtypes.LocalizedText(model.modelName[None])]
        mds_descriptor.MetaData.SerialNumber = ['ABCD-1234']
        mds_descriptor.MetaData.ModelNumber = '0.99'
        super(SomeDevice, self).__init__(wsdiscovery, my_uuid, model, device, device_mdib_container, validate,
                                         # registerDefaultOperations=True,
                                         sslContext=sslContext, logLevel=logLevel, log_prefix=log_prefix,
                                         chunked_messages=chunked_messages)
        # self._handler.mkDefaultRoleHandlers()

    @classmethod
    def fromMdibFile(cls, wsdiscovery, my_uuid, mdib_xml_path,
                     validate=True, sslContext=None, logLevel=logging.INFO, log_prefix='', chunked_messages=False):
        """
        An alternative constructor for the class
        """
        if not os.path.isabs(mdib_xml_path):
            here = os.path.dirname(__file__)
            mdib_xml_path = os.path.join(here, mdib_xml_path)

        with open(mdib_xml_path, 'rb') as f:
            mdib_xml_string = f.read()
        return cls(wsdiscovery, my_uuid, mdib_xml_string, validate, sslContext, logLevel, log_prefix=log_prefix,
                   chunked_messages=chunked_messages)


class TestClientSomeDeviceGRPC(unittest.TestCase):
    def setUp(self) -> None:
        self._log_handler = _start_logger()
        self.wsd = GDiscovery()
        self.wsd.start()
        self.sdc_device = SomeDevice.fromMdibFile(self.wsd, None, '70041_MDIB_Final.xml', log_prefix='<Final> ')
        self.sdc_device.mdib.mdibVersion = 42
        self.sdc_device.startAll(startRealtimeSampleLoop=False)
        self.sdc_device.publish()
        time.sleep(1)
        self.sdc_client = GSdcClient('localhost:50051')

    def tearDown(self) -> None:
        self.sdc_device.stopAll()
        _stop_logger(self._log_handler)

    @staticmethod
    def provideRealtimeData(sdcDevice):
        paw = waveforms.SawtoothGenerator(min_value=0, max_value=10, waveformperiod=1.1, sampleperiod=0.01)
        sdcDevice.mdib.registerWaveformGenerator('0x34F05500', paw)  # '0x34F05500 MBUSX_RESP_THERAPY2.00H_Paw'

        flow = waveforms.SinusGenerator(min_value=-8.0, max_value=10.0, waveformperiod=1.2, sampleperiod=0.01)
        sdcDevice.mdib.registerWaveformGenerator('0x34F05501', flow)  # '0x34F05501 MBUSX_RESP_THERAPY2.01H_Flow'

        co2 = waveforms.TriangleGenerator(min_value=0, max_value=20, waveformperiod=1.0, sampleperiod=0.01)
        sdcDevice.mdib.registerWaveformGenerator('0x34F05506', co2)  # '0x34F05506 MBUSX_RESP_THERAPY2.06H_CO2_Signal'

        # make SinusGenerator (0x34F05501) the annotator source
        annotation = pmtypes.Annotation(pmtypes.CodedValue('a', 'b'))  # what is CodedValue for startOfInspirationCycle?
        sdcDevice.mdib.registerAnnotationGenerator(annotation,
                                                   triggerHandle='0x34F05501',
                                                   annotatedHandles=('0x34F05500', '0x34F05501', '0x34F05506'))

    def test_BasicConnect(self):
        cl_get_service = self.sdc_client.client('Get')
        request = sdc_messages_pb2.GetMdibRequest()
        response = cl_get_service.GetMdib(request)
        self.assertIsInstance(response, sdc_messages_pb2.GetMdibResponse)

    def test_initmdibBasicConnect(self):
        self.provideRealtimeData(self.sdc_device)
        self.sdc_client.subscribe_all()
        cl_mdib = GClientMdibContainer(self.sdc_client)
        cl_mdib.initMdib()
        self.assertEqual(cl_mdib.mdibVersion, self.sdc_device._mdib.mdibVersion)
        self.assertEqual(cl_mdib.sequenceId, self.sdc_device._mdib.sequenceId)

        self.assertEqual(len(cl_mdib.descriptions.objects), len(self.sdc_device._mdib.descriptions.objects))
        self.assertEqual(len(cl_mdib.states.objects), len(self.sdc_device._mdib.states.objects))
        initial_mdib_version = cl_mdib.mdibVersion
        self.sdc_device.start_realtimesample_loop()
        time.sleep(1)
        self.assertGreater(cl_mdib.mdibVersion, initial_mdib_version)

    def test_subscriptions(self):
        self.provideRealtimeData(self.sdc_device)
        self.sdc_client.subscribe_all()
        cl_mdib = GClientMdibContainer(self.sdc_client)
        cl_mdib.initMdib()
        self.assertEqual(cl_mdib.mdibVersion, self.sdc_device._mdib.mdibVersion)
        self.assertEqual(cl_mdib.sequenceId, self.sdc_device._mdib.sequenceId)

        self.assertEqual(len(cl_mdib.descriptions.objects), len(self.sdc_device._mdib.descriptions.objects))
        self.assertEqual(len(cl_mdib.states.objects), len(self.sdc_device._mdib.states.objects))
        self.sdc_device.start_realtimesample_loop()
        time.sleep(1)
        metric_handle = '0x34F0434A'
        alert_cond_handle = '0xD3C00100'
        alert_sig_handle = '0xD3C00100.loc.Vis'
        alert_sys_handle = 'Asy.mds0'
        descriptor_handle = 'Asy.mds0'
        vmd_handle = "2.1.1"
        with self.sdc_device.mdib.mdibUpdateTransaction() as tr:
            metric_state = tr.getMetricState(metric_handle)
            if not metric_state.metricValue:
                metric_state.mkMetricValue()
            metric_state.metricValue.Value = 42
            alert_cond_state = tr.getAlertState(alert_cond_handle)
            alert_cond_state.ActualConditionGenerationDelay = 44
            alert_sig_state = tr.getAlertState(alert_sig_handle)
            alert_sig_state.Slot = 4
            alert_sys_state = tr.getAlertState(alert_sys_handle)
            alert_sys_state.SelfCheckCount = 555
            alert_sys_descr = tr.getDescriptor(descriptor_handle)
            alert_sys_descr.SelfCheckPeriod = 17
            vmd_state = tr.getComponentState(vmd_handle)
            vmd_state.OperatingHours = 3
        new_location = SdcLocation(fac='tklx', poc='CU2', bed='b42')
        self.sdc_device.mdib.setLocation(new_location)

        # wait for episodic report
        time.sleep(1)
        updated_metric_state = cl_mdib.states.descriptorHandle.getOne(metric_handle)
        self.assertEqual(updated_metric_state.metricValue.Value, 42)
        updated_alert_cond_state = cl_mdib.states.descriptorHandle.getOne(alert_cond_handle)
        self.assertEqual(updated_alert_cond_state.ActualConditionGenerationDelay, 44)
        updated_alert_sig_state = cl_mdib.states.descriptorHandle.getOne(alert_sig_handle)
        self.assertEqual(updated_alert_sig_state.Slot, 4)
        updated_alert_sys_state = cl_mdib.states.descriptorHandle.getOne(alert_sys_handle)
        self.assertEqual(updated_alert_sys_state.SelfCheckCount, 555)
        updated_alert_sys_descr = cl_mdib.descriptions.handle.getOne(descriptor_handle)
        self.assertEqual(updated_alert_sys_descr.SelfCheckPeriod, 17)
        updated_vmd_state = cl_mdib.states.descriptorHandle.getOne(vmd_handle)
        self.assertEqual(updated_vmd_state.OperatingHours, 3)
        updated_loc_context = cl_mdib.contextStates.descriptorHandle.getOne('LC.mds0') #objects[0]
        self.assertEqual(updated_loc_context.LocationDetail.Facility, 'tklx')
        self.assertEqual(updated_loc_context.LocationDetail.PoC, 'CU2')
        self.assertEqual(updated_loc_context.LocationDetail.Bed, 'b42')

    def test_metric_report_subscriptions(self):
        # self.provideRealtimeData(self.sdc_device)
        # time.sleep(1)
        self.sdc_client.subscribe_all()
        cl_mdib = GClientMdibContainer(self.sdc_client)
        # time.sleep(1)
        cl_mdib.initMdib()
        self.assertEqual(cl_mdib.mdibVersion, self.sdc_device._mdib.mdibVersion)
        self.assertEqual(cl_mdib.sequenceId, self.sdc_device._mdib.sequenceId)

        self.assertEqual(len(cl_mdib.descriptions.objects), len(self.sdc_device._mdib.descriptions.objects))
        self.assertEqual(len(cl_mdib.states.objects), len(self.sdc_device._mdib.states.objects))
        # self.sdc_device.start_realtimesample_loop()
        time.sleep(1)
        # self.assertGreater(cl_mdib.mdibVersion, initial_mdib_version)
        handle = '0x34F0434A'
        logging.getLogger('pysdc.grpc.map').setLevel(logging.DEBUG)
        with self.sdc_device.mdib.mdibUpdateTransaction() as tr:
            state = tr.getMetricState(handle)
            if not state.metricValue:
                state.mkMetricValue()
            state.metricValue.Value = 42
        # wait for episodic report
        time.sleep(1)
        updated_state = cl_mdib.states.descriptorHandle.getOne(handle)
        self.assertEqual(updated_state.metricValue.Value, 42)

    def test_setMetricState_SDC(self):
        SET_TIMEOUT = 10
        # first we need to add a setMetricState Operation
        scoDescriptors = self.sdc_device.mdib.descriptions.NODETYPE.get(namespaces.domTag('ScoDescriptor'))
        cls = self.sdc_device.mdib.getDescriptorContainerClass(namespaces.domTag('SetMetricStateOperationDescriptor'))
        myCode = pmtypes.CodedValue(99999)
        operation_descriptor_container = self.sdc_device.mdib._createDescriptorContainer(cls,
                                                                                         'HANDLE_FOR_MY_TEST',
                                                                                         scoDescriptors[0].handle,
                                                                                         myCode,
                                                                                         'Inf')
        operation_descriptor_container.OperationTarget = '0x34F001D5'
        operation_descriptor_container.Type = pmtypes.CodedValue(999998)
        # setMetricStateOperationDescriptorContainer.updateNode()
        self.sdc_device.mdib.descriptions.addObject(operation_descriptor_container)
        op = self.sdc_device.product_roles.metric_provider.makeOperationInstance(operation_descriptor_container)
        self.sdc_device.scoOperationsRegistry.registerOperation(op)
        self.sdc_device.mdib.mkStateContainersforAllDescriptors()
        setService = self.sdc_client.client('Set')
        cl_mdib = GClientMdibContainer(self.sdc_client)
        cl_mdib.initMdib()

        myOperationDescriptor = operation_descriptor_container
        operationHandle = myOperationDescriptor.handle
        proposed_metric_state = cl_mdib.mkProposedState('0x34F001D5')
        self.assertIsNone(proposed_metric_state.LifeTimePeriod) # just to be sure that we know the correct intitial value
        before_stateversion = proposed_metric_state.StateVersion
        newLifeTimePeriod = 42.5
        proposed_metric_state.LifeTimePeriod = newLifeTimePeriod
        future = setService.setMetricState(operationHandle, proposed_metric_states=[proposed_metric_state])
        result = future.result(timeout=SET_TIMEOUT)
        state = result.state
        self.assertEqual(state, pmtypes.InvocationState.FINISHED)
        self.assertTrue(result.error in ('', 'Unspec'))
        self.assertEqual(result.errorMsg, '')
        updatedMetricState = cl_mdib.states.descriptorHandle.getOne('0x34F001D5')
        self.assertEqual(updatedMetricState.StateVersion, before_stateversion +1)
        self.assertAlmostEqual(updatedMetricState.LifeTimePeriod, newLifeTimePeriod)
