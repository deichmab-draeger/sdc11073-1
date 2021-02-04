import logging
from org.somda.sdc.proto.model import sdc_services_pb2_grpc
from org.somda.sdc.proto.model.sdc_messages_pb2 import EpisodicReportStream
import grpc


class MdibReportingService(sdc_services_pb2_grpc.MdibReportingServiceServicer):

    def __init__(self, subscriptions_manager):
        super().__init__()
        self._subscriptions_manager = subscriptions_manager
        self._subscription = None
        self._logger = logging.getLogger('pysdc.grpc.dev.rep_srv')
        self._logger.info('MdibReportingService initialized')

    def EpisodicReport(self, request, context):
        actions = list(request.filter.action_filter.action)
        self._logger.info('EpisodicReport called')
        self._subscription = self._subscriptions_manager.onSubscribeRequest(actions)
        _run = True
        while(_run):
            report = self._subscription.reports.get()
            if report == 'stop':
                _run = False
            else:
                self._logger.info('yield EpisodicReport')
                yield report
                self._logger.info('yield EpisodicReport done')
