import unittest
import logging
import os
import time
from sdc11073.transport.protobuf.consumer.consumer import SdcClient
from sdc11073.transport.protobuf.provider.provider import SdcDevice
from sdc11073.mdib.devicemdib import DeviceMdibContainer
from sdc11073.transport.soap.soapenvelope import DPWSThisModel, DPWSThisDevice
from sdc11073 import namespaces, pmtypes


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
        mdsDescriptor.Manufacturer.append(pmtypes.LocalizedText(u'Dräger'))
        mdsDescriptor.ModelName.append(pmtypes.LocalizedText(model.modelName[None]))
        mdsDescriptor.SerialNumber.append(pmtypes.ElementWithTextOnly('ABCD-1234'))
        mdsDescriptor.ModelNumber = '0.99'
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
        self.wsd = None
        self.sdcDevice = SomeDevice.fromMdibFile(self.wsd, None, '70041_MDIB_Final.xml', log_prefix='<Final> ')
        self.sdc_client = SdcClient()

        self.sdcDevice.startAll()
        time.sleep(1)

    def tearDown(self) -> None:
        self.sdcDevice.stopAll()

    def test_BasicConnect(self):
        cl_getService = self.sdc_client.client('Get')
        response = cl_getService.GetMdib()
        self.assertEqual(response.tag, str(namespaces.msgTag('GetMdibResponse')))

