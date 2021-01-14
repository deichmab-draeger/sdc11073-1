import unittest
import logging
from tests.test_grpc_client_device import SomeDevice
from org.somda.sdc.proto.model import sdc_messages_pb2
from sdc11073.transport.protobuf.msgreader import MessageReader
from sdc11073.mdib import mdibbase
from sdc11073.definitions_sdc import SDC_v1_Definitions

class Test_SomeDevice_GRPC(unittest.TestCase):
    def setUp(self) -> None:
        self.wsd = None
        self.sdc_device = SomeDevice.fromMdibFile(self.wsd, None, '70041_MDIB_Final.xml', log_prefix='<Final> ')
        self.sdc_device._mdib.mdibVersion = 42 # start with some non-default value
        self.sdc_device.startAll()
        # time.sleep(1)

    def tearDown(self) -> None:
        self.sdc_device.stopAll()

    def _missing_descriptors(self, device_mdib, client_mdib):
        dev_handles = device_mdib.descriptions.handle.keys()
        cl_handles = client_mdib.descriptions.handle.keys()
        return [h for h in dev_handles if h not in cl_handles]

    def _missing_states(self, device_mdib, client_mdib):
        dev_handles = device_mdib.states.descriptorHandle.keys()
        cl_handles = client_mdib.states.descriptorHandle.keys()
        return [h for h in dev_handles if h not in cl_handles]

    def test_get_mdib(self):
        getService = self.sdc_device.get_service
        response = getService.GetMdib(None, None)
        self.assertIsInstance(response, sdc_messages_pb2.GetMdibResponse)
        self.assertEqual(response.payload.mdib.a_mdib_version_group.a_mdib_version.value, self.sdc_device._mdib.mdibVersion)
        self.assertEqual(response.payload.mdib.a_mdib_version_group.a_sequence_id, self.sdc_device._mdib.sequenceId)

    def test_get_mdib_msgreader(self):
        getService = self.sdc_device.get_service
        request = sdc_messages_pb2.GetMdibRequest()
        response = getService.GetMdib(request, None)
        self.assertIsInstance(response, sdc_messages_pb2.GetMdibResponse)
        reader = MessageReader(logger =logging.getLogger('unittest'))
        cl_mdib = mdibbase.MdibContainer(SDC_v1_Definitions)
        descriptors = reader.readMdDescription(response.payload.mdib.md_description, cl_mdib)
        for d in descriptors:
            cl_mdib.descriptions.addObjectNoLock(d)
        missing_descr_handles = self._missing_descriptors(self.sdc_device._mdib, cl_mdib)
        self.assertEqual(len(missing_descr_handles), 0)
        states = reader.readMdState(response.payload.mdib.md_state, cl_mdib)
        for st in states:
            cl_mdib.states.addObjectNoLock(st)
        missing_state_handles = self._missing_states(self.sdc_device._mdib, cl_mdib)
        self.assertEqual(len(missing_state_handles), 0)

    def test_get_md_description_msgreader(self):
        getService = self.sdc_device.get_service
        request = sdc_messages_pb2.GetMdDescriptionRequest()
        response = getService.GetMdDescription(request, None)
        self.assertIsInstance(response, sdc_messages_pb2.GetMdDescriptionResponse)
        reader = MessageReader(logger=logging.getLogger('unittest'))
        cl_mdib = mdibbase.MdibContainer(SDC_v1_Definitions)
        descriptors = reader.readMdDescription(response.payload.md_description, cl_mdib)
        for d in descriptors:
            cl_mdib.descriptions.addObjectNoLock(d)
        missing_descr_handles = self._missing_descriptors(self.sdc_device._mdib, cl_mdib)
        self.assertEqual(len(missing_descr_handles), 0)

        not_equal_descriptors = []
        for d in descriptors:
            d_ref = self.sdc_device._mdib.descriptions.handle.getOne(d.Handle)
            d_ref.ext_Extension = None
            diff = d_ref.diff(d)
            if diff:
                not_equal_descriptors.append((d_ref, d, diff))
        self.assertEqual(len(not_equal_descriptors), 0)

    def test_get_md_state_msgreader(self):
        reader = MessageReader(logger=logging.getLogger('unittest'))
        cl_mdib = mdibbase.MdibContainer(SDC_v1_Definitions)
        getService = self.sdc_device.get_service
        # first get descriptors, otherwise states can't be instantiated
        response = getService.GetMdDescription(None, None)
        descriptors = reader.readMdDescription(response.payload.md_description, cl_mdib)
        for d in descriptors:
            cl_mdib.descriptions.addObjectNoLock(d)
        # get all states
        request = sdc_messages_pb2.GetMdStateRequest()
        response = getService.GetMdState(request, None)
        self.assertIsInstance(response, sdc_messages_pb2.GetMdStateResponse)
        states = reader.readMdState(response.payload.md_state, cl_mdib)
        for st in states:
            cl_mdib.states.addObjectNoLock(st)
        missing_state_handles = self._missing_states(self.sdc_device._mdib, cl_mdib)
        self.assertEqual(len(missing_state_handles), 0)

        #use handles parameter: try to read only two states, pick some random handles
        all_handles = list(cl_mdib.descriptions.handle.keys())
        handles = [all_handles[4], all_handles[40]]
        request.payload.handle_ref.extend(handles)
        response = getService.GetMdState(request, None)
        states = reader.readMdState(response.payload.md_state, cl_mdib)
        self.assertEqual(len(states), 2)
        self.assertEqual(states[0].descriptorHandle, handles[0])
        self.assertEqual(states[1].descriptorHandle, handles[1])


    def test_activate(self):
        reader = MessageReader(logger=logging.getLogger('unittest'))
        cl_mdib = mdibbase.MdibContainer(SDC_v1_Definitions)
        setService = self.sdc_device.set_service
        request = sdc_messages_pb2.ActivateRequest()
        response = setService.Activate(request, None)
        self.assertIsInstance(response, sdc_messages_pb2.ActivateResponse)
        pass
