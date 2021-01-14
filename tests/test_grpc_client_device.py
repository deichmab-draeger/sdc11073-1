import unittest
import logging
import os
import time
from sdc11073.transport.protobuf.consumer.consumer import SdcClient
from sdc11073.transport.protobuf.provider.provider import SdcDevice
from sdc11073.transport.protobuf.discovery import GDiscovery
from sdc11073.mdib.devicemdib import DeviceMdibContainer
from sdc11073.transport.soap.soapenvelope import DPWSThisModel, DPWSThisDevice
from sdc11073 import namespaces, pmtypes
from sdc11073.transport.protobuf.clientmdib import GClientMdibContainer
from sdc11073.sdcdevice import waveforms

from org.somda.sdc.proto.model import sdc_messages_pb2

class SomeDevice(SdcDevice):
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
        deviceMdibContainer = DeviceMdibContainer.fromString(mdib_xml_string, log_prefix=log_prefix)
        # set Metadata
        mdsDescriptor = deviceMdibContainer.descriptions.NODETYPE.getOne(namespaces.domTag('MdsDescriptor'))
        mdsDescriptor.MetaData.Manufacturer = [pmtypes.LocalizedText(u'Dräger')]
        mdsDescriptor.MetaData.ModelName = [pmtypes.LocalizedText(model.modelName[None])]
        mdsDescriptor.MetaData.SerialNumber = ['ABCD-1234']
        mdsDescriptor.MetaData.ModelNumber = '0.99'
        # mdsDescriptor.updateNode()
        super(SomeDevice, self).__init__(wsdiscovery, my_uuid, model, device, deviceMdibContainer, validate,
                                         # registerDefaultOperations=True,
                                         sslContext=sslContext, logLevel=logLevel, log_prefix=log_prefix,
                                         chunked_messages=chunked_messages)
        #self._handler.mkDefaultRoleHandlers()

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


class Test_Client_SomeDevice_GRPC(unittest.TestCase):
    def setUp(self) -> None:
        self.wsd = GDiscovery()
        self.wsd.start()
        self.sdc_device = SomeDevice.fromMdibFile(self.wsd, None, '70041_MDIB_Final.xml', log_prefix='<Final> ')
        self.sdc_device.startAll(startRealtimeSampleLoop=True)
        self.sdc_device.publish()
        self.sdc_client = SdcClient('localhost:50051')

        time.sleep(1)

    def tearDown(self) -> None:
        self.sdc_device.stopAll()

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
        cl_getService = self.sdc_client.client('Get')
        response = cl_getService.GetMdib()
        self.assertIsInstance(response, sdc_messages_pb2.GetMdibResponse)

    def test_initmdibBasicConnect(self):
        self.provideRealtimeData(self.sdc_device)
        cl_mdib = GClientMdibContainer(self.sdc_client)
        cl_mdib.initMdib()
        self.assertEqual(cl_mdib.mdibVersion, self.sdc_device._mdib.mdibVersion)
        self.assertEqual(cl_mdib.sequenceId, self.sdc_device._mdib.sequenceId)

        self.assertEqual(len(cl_mdib.descriptions.objects), len(self.sdc_device._mdib.descriptions.objects))
        self.assertEqual(len(cl_mdib.states.objects), len(self.sdc_device._mdib.states.objects))
        time.sleep(100)