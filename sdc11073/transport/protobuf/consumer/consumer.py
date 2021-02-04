import logging

import grpc
from org.somda.sdc.proto.model import sdc_services_pb2_grpc, sdc_messages_pb2
from org.somda.sdc.proto.model.biceps import setvalue_pb2, abstractset_pb2
from .getservice import GetService_Wrapper
from .setservice import SetService_Wrapper
from .mdibreportingservice import MdibReportingService_Wrapper
from ....definitions_sdc import SDC_v1_Definitions
from ..msgreader import MessageReader
from .... import observableproperties as properties


class GSdcClient:

    # the following observables can be used to observe the incoming notifications by message type.
    # They contain only the body node of the notification, not the envelope
    waveFormReport = properties.ObservableProperty()
    episodicMetricReport = properties.ObservableProperty()
    episodicAlertReport = properties.ObservableProperty()
    episodicComponentReport = properties.ObservableProperty()
    episodicOperationalStateReport = properties.ObservableProperty()
    episodicContextReport = properties.ObservableProperty()
    descriptionModificationReport = properties.ObservableProperty()
    operationInvokedReport = properties.ObservableProperty()
    anyReport = properties.ObservableProperty()  # all reports can be observed here

    def __init__(self, ip):
        self.channel = grpc.insecure_channel(ip)
        self._clients = {
            "Get": GetService_Wrapper(self.channel),
            "Set": SetService_Wrapper(self.channel),
            "Event": MdibReportingService_Wrapper(self.channel)
        }
        self.sdc_definitions = SDC_v1_Definitions
        self.log_prefix = ''
        self._logger = logging.getLogger('sdc.client')
        self.msg_reader = MessageReader(self._logger)
        properties.bind(self.client("Event"), episodic_report=self._on_episodic_report)
        self.all_subscribed = False

    def client(self, name):
        return self._clients[name]

    def subscribe_all(self):
        service = self.client('Event')
        self.all_subscribed = True
        service.EpisodicReport()  # starts a background thread to receive stream data

    def _on_episodic_report(self, episodic_report):
        print('_on_episodic_report')
        report = episodic_report.report
        self.anyReport = report
        if report.HasField('waveform'):
            self.waveFormReport = report.waveform
        if report.HasField('alert'):
            self.episodicAlertReport = report.alert
        if report.HasField('component'):
            self.episodicComponentReport = report.component
        if report.HasField('context'):
            self.episodicContextReport = report.component
        if report.HasField('description'):
            self.descriptionModificationReport = report.description
        if report.HasField('metric'):
            self.episodicMetricReport = report.metric
        if report.HasField('operational_state'):
            self.episodicOperationalStateReport = report.operational_state


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        request = sdc_messages_pb2.SetValueRequest(payload=setvalue_pb2.SetValueMsg(
            requested_numeric_value='42',
            abstract_set=abstractset_pb2.AbstractSetMsg(operation_handle_ref='abc')))
        s_stub = sdc_services_pb2_grpc.SetServiceStub(channel)
        response2 = s_stub.SetValue(request)
    print("s_stub client received: " + response2.payload)


if __name__ == '__main__':
    logging.basicConfig()
    run()
