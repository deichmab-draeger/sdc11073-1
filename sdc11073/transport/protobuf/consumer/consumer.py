import logging

import grpc
from org.somda.sdc.proto.model import sdc_services_pb2, sdc_services_pb2_grpc, sdc_messages_pb2
from org.somda.sdc.proto.model.biceps import setvalue_pb2, abstractset_pb2
from .getservice import GetService_Wrapper
from .setservice import SetService_Wrapper


class SdcClient():

    def __init__(self, ip='localhost:50051'):
        self.channel = grpc.insecure_channel(ip)
        self._clients = {
        "Get": GetService_Wrapper(self.channel),
        "Set": SetService_Wrapper(self.channel)
        }
    def client(self, name):
        return self._clients[name]



def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        # request = sdc_messages_pb2.GetMdibRequest()
        # g_stub = sdc_services_pb2_grpc.GetServiceStub(channel)
        # response1 = g_stub.GetMdib(request)

        #request = sdc_messages_pb2.SetValueRequest(payload=setvalue_pb2.SetValueMsg(operation_handle_ref = 'abc', requested_numeric_value='42'))
        request = sdc_messages_pb2.SetValueRequest(payload=setvalue_pb2.SetValueMsg(requested_numeric_value='42',
                                                                                    abstract_set=abstractset_pb2.AbstractSetMsg(operation_handle_ref='abc')))
        s_stub = sdc_services_pb2_grpc.SetServiceStub(channel)
        response2 = s_stub.SetValue(request)
    print("s_stub client received: " + response2.payload)


if __name__ == '__main__':
    logging.basicConfig()
    run()
