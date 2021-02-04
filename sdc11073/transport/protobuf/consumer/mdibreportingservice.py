import logging
import threading
from org.somda.sdc.proto.model import sdc_services_pb2_grpc, sdc_messages_pb2
from sdc11073.definitions_sdc import SDC_v1_Definitions
from sdc11073 import  observableproperties


class MdibReportingService_Wrapper(sdc_services_pb2_grpc.MdibReportingServiceStub):
    episodic_report = observableproperties.ObservableProperty()
    def __init__(self, channel):
        self._stub = sdc_services_pb2_grpc.MdibReportingServiceStub(channel)
        self._logger = logging.getLogger('pysdc.grpc.cl.rep_srv')
        self._report_reader = None

    def EpisodicReport(self):
        self._logger.info('EpisodicReport')
        self._report_reader = threading.Thread(target=self._read_episodic_reports, name='read_episodic_reports')
        self._report_reader.daemon = True
        self._report_reader.start()

    def _read_episodic_reports(self):
        request = sdc_messages_pb2.EpisodicReportRequest()
        f = request.filter.action_filter.action
        actions = [SDC_v1_Definitions.Actions.Waveform,
                   SDC_v1_Definitions.Actions.DescriptionModificationReport,
                   SDC_v1_Definitions.Actions.EpisodicMetricReport,
                   SDC_v1_Definitions.Actions.EpisodicAlertReport,
                   SDC_v1_Definitions.Actions.EpisodicContextReport,
                   SDC_v1_Definitions.Actions.EpisodicComponentReport,
                   SDC_v1_Definitions.Actions.EpisodicOperationalStateReport,
                   SDC_v1_Definitions.Actions.OperationInvokedReport]
        f.extend(actions)
        for response in self._stub.EpisodicReport(request):
            print(f'Response received')
            self.episodic_report = response
        print(f'end of EpisodicReports')
