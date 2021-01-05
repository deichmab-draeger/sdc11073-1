from concurrent import futures
import logging
import grpc

from org.somda.sdc.proto.model import sdc_services_pb2_grpc
from org.somda.sdc.proto.model.biceps.setvalueresponse_pb2 import SetValueResponseMsg
from org.somda.sdc.proto.model.biceps.abstractsetresponse_pb2 import AbstractSetResponseMsg
from org.somda.sdc.proto.model.biceps.invocationinfo_pb2 import InvocationInfoMsg
from org.somda.sdc.proto.model.biceps.invocationstate_pb2 import InvocationStateMsg
from org.somda.sdc.proto.model.sdc_messages_pb2 import SetValueResponse


class SetService(sdc_services_pb2_grpc.SetServiceServicer):
    def __init__(self, mdib):
        super().__init__()
        self._mdib = mdib

    def SetValue(self, request, context):
        operation_handle = request.payload.abstract_set.operation_handle_ref
        value = request.payload.requested_numeric_value
        response = SetValueResponse(payload=SetValueResponseMsg(
             abstract_set_response=AbstractSetResponseMsg(
                invocation_info=InvocationInfoMsg(
                    invocation_state=InvocationStateMsg(enum_value=InvocationStateMsg.FIN),
                    transaction_id=43
                )
            )
        ))
        return response
