from sdc import sdc_services_pb2_grpc, sdc_messages_pb2
from sdc.biceps import setvalue_pb2, abstractset_pb2

class SetService_Wrapper(sdc_services_pb2_grpc.SetServiceStub):
    def __init__(self, channel):
        self._stub = sdc_services_pb2_grpc.SetServiceStub(channel)

    def SetValue(self, operation_handle, value):
        request = sdc_messages_pb2.SetValueRequest(
            payload=setvalue_pb2.SetValueMsg(
                requested_numeric_value=value,
                abstract_set=abstractset_pb2.AbstractSetMsg(operation_handle_ref=operation_handle)))
        response = self._stub.SetValue(request)
        return response
