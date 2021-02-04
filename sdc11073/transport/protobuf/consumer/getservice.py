from org.somda.sdc.proto.model import sdc_services_pb2_grpc, sdc_messages_pb2

class GetService_Wrapper(sdc_services_pb2_grpc.GetServiceStub):
    def __init__(self, channel):
        super().__init__(channel)
        self._stub = sdc_services_pb2_grpc.GetServiceStub(channel)

    def GetMdib(self):
        request = sdc_messages_pb2.GetMdibRequest()
        response = self._stub.GetMdib(request)
        return response
