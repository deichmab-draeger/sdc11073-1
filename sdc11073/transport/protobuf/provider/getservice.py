import grpc

from sdc import sdc_services_pb2_grpc
from sdc.sdc_messages_pb2 import GetMdibResponse

from sdc.biceps.mdib_pb2 import MdibMsg
from sdc.biceps.mddescription_pb2 import MdDescriptionMsg+


class GetService(sdc_services_pb2_grpc.GetServiceServicer):

    def __init__(self, mdib):
        super().__init__()
        self._mdib = mdib

    def GetMdib(self, request, context):
        """Missing associated documentation comment in .proto file."""

        response = GetMdibResponse()
        return response
        # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        # context.set_details('GetMdib Method not implemented!')
        # #raise NotImplementedError('GetMdib Method not implemented!')

