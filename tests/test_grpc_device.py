import unittest
import logging
from .test_grpc_client_device import SomeDevice
from org.somda.sdc.proto.model import sdc_messages_pb2
from sdc11073.transport.protobuf.msgreader import MessageReader
from sdc11073.mdib import mdibbase
from sdc11073.definitions_sdc import SDC_v1_Definitions

class Test_SomeDevice_GRPC(unittest.TestCase):
    def setUp(self) -> None:
        self.wsd = None
        self.sdcDevice = SomeDevice.fromMdibFile(self.wsd, None, '70041_MDIB_Final.xml', log_prefix='<Final> ')

        self.sdcDevice.startAll()
        # time.sleep(1)

    def tearDown(self) -> None:
        self.sdcDevice.stopAll()

    def test_get_mdib(self):
        getService = self.sdcDevice.get_service
        response = getService.GetMdib(None, None)
        self.assertIsInstance(response, sdc_messages_pb2.GetMdibResponse)

    def test_get_mdib_basic_content_check(self):
        getService = self.sdcDevice.get_service
        response = getService.GetMdib(None, None)
        self.assertIsInstance(response, sdc_messages_pb2.GetMdibResponse)
        descr_root = response.payload.mdib.md_description
        self.assertEqual(len(descr_root.mds), 1)
        self.assertEqual(len(descr_root.mds[0].vmd), 4)

    def test_get_mdib_msgreader(self):
        getService = self.sdcDevice.get_service
        response = getService.GetMdib(None, None)
        self.assertIsInstance(response, sdc_messages_pb2.GetMdibResponse)
        reader = MessageReader(logger =logging.getLogger('unittest'))
        cl_mdib = mdibbase.MdibContainer(SDC_v1_Definitions)
        descriptors = reader.readMdDescription(response, cl_mdib)
        handles = [d.Handle for d in descriptors]

        missing_handles = [ h for h in self.sdcDevice._mdib.descriptions.handle.keys() if h not in handles]
        missing_descriptors = [self.sdcDevice._mdib.descriptions.handle.getOne(h) for h in missing_handles]
        self.assertEqual(len(descriptors), len(self.sdcDevice._mdib.descriptions.objects))
        not_equal_descriptors = []
        for d in descriptors:
            d_ref = self.sdcDevice._mdib.descriptions.handle.getOne(d.Handle)
            d_ref.ext_Extension = None
            diff = d_ref.diff(d)
            if diff:
                not_equal_descriptors.append((d_ref, d, diff))
        self.assertEqual(len(not_equal_descriptors), 0)