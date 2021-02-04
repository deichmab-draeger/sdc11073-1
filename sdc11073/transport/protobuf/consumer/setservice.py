from org.somda.sdc.proto.model import sdc_services_pb2_grpc, sdc_messages_pb2
from org.somda.sdc.proto.model.biceps import setvalue_pb2, abstractset_pb2
from org.somda.sdc.proto.model.biceps import setmetricstate_pb2
from ..mapping.statesmapper import generic_state_to_p

class SetService_Wrapper(sdc_services_pb2_grpc.SetServiceStub):
    """Consumer-side implementation of SetService"""
    def __init__(self, channel):
        super().__init__(channel)
        self._operationsManager = None
        self._mdib_wref = None
        self._stub = sdc_services_pb2_grpc.SetServiceStub(channel)

    def SetValue(self, operation_handle, value):
        request = sdc_messages_pb2.SetValueRequest(
            payload=setvalue_pb2.SetValueMsg(
                requested_numeric_value=value,
                abstract_set=abstractset_pb2.AbstractSetMsg(operation_handle_ref=operation_handle)))
        response = self._stub.SetValue(request)
        return response

    def setMetricState(self, operation_handle, proposed_metric_states):
        request = sdc_messages_pb2.SetMetricStateRequest()
        request.payload.abstract_set.operation_handle_ref = operation_handle
        for proposed in proposed_metric_states:
            p = request.payload.proposed_metric_state.add()
            generic_state_to_p(proposed, p)
        response = self._stub.SetMetricState(request)
        return response

    def register_mdib(self, mdib):
        ''' Client sometimes must know the mdib data (e.g. Set service, activate method).'''
        if mdib is not None and self._mdib_wref is not None:
            raise RuntimeError('Client "{}" has already an registered mdib'.format(self.porttype))
        self._mdib_wref = None if mdib is None else weakref.ref(mdib)

    def setOperationsManager(self, operationsManager):
        self._operationsManager = operationsManager

    def _callOperation(self, soapEnvelope, request_manipulator=None):
        return self._operationsManager.callOperation(self, soapEnvelope, request_manipulator)

