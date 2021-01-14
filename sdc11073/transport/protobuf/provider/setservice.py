import grpc

from org.somda.sdc.proto.model import sdc_services_pb2_grpc
from org.somda.sdc.proto.model.biceps.setvalueresponse_pb2 import SetValueResponseMsg
from org.somda.sdc.proto.model.biceps.abstractsetresponse_pb2 import AbstractSetResponseMsg
from org.somda.sdc.proto.model.biceps.invocationinfo_pb2 import InvocationInfoMsg
from org.somda.sdc.proto.model.biceps.invocationstate_pb2 import InvocationStateMsg
from org.somda.sdc.proto.model import sdc_messages_pb2 #import SetValueResponse, ActivateResponse


class SetService(sdc_services_pb2_grpc.SetServiceServicer):
    def __init__(self, mdib):
        super().__init__()
        self._mdib = mdib

    def Activate(self, request, context):
        response = sdc_messages_pb2.ActivateResponse()
        return response

    def SetMetricState(self, request, context):
        response = sdc_messages_pb2.SetMetricStateResponse()
        return response

    def SetMetricState(self, request, context):
        response = sdc_messages_pb2.SetMetricStateResponse()
        return response

    def SetComponentState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetContextState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetAlertState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetString(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetValue(self, request, context):
        operation_handle = request.payload.abstract_set.operation_handle_ref
        value = request.payload.requested_numeric_value
        response = sdc_messages_pb2.SetValueResponse(payload=SetValueResponseMsg(
             abstract_set_response=AbstractSetResponseMsg(
                invocation_info=InvocationInfoMsg(
                    invocation_state=InvocationStateMsg(enum_value=InvocationStateMsg.FIN),
                    transaction_id=43
                )
            )
        ))
        return response

    def OperationInvokedReport(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')
