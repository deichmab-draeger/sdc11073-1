from sdc11073.mdib import clientmdib
from sdc11073 import observableproperties as properties

class GClientMdibContainer(clientmdib.ClientMdibContainer):

    def initMdib(self):
        if self._isInitialized:
            raise RuntimeError('ClientMdibContainer is already initialized')
        # first start receiving notifications, then call getMdib.
        # Otherwise we might miss notifications.
        self._bind_to_observables()

        cl_getService = self._sdcClient.client('Get')
        self._logger.info('initializing mdib...')
        response = cl_getService.GetMdib()
        self._logger.info('creating description containers...')
        descriptorContainers = self._msg_reader.readMdDescription(response.payload.mdib.md_description, self)
        with self.descriptions._lock:  # pylint: disable=protected-access
            self.descriptions.clear()
        self.addDescriptionContainers(descriptorContainers)
        self._logger.info('creating state containers...')
        self.clearStates()
        stateContainers = self._msg_reader.readMdState(response.payload.mdib.md_state, self)
        self.addStateContainers(stateContainers)

        mdib_version = response.payload.mdib.a_mdib_version_group.a_mdib_version.value
        sequence_id = response.payload.mdib.a_mdib_version_group.a_sequence_id
        instance_id = response.payload.mdib.a_mdib_version_group.a_instance_id.value
        self.mdibVersion = mdib_version
        self.sequenceId = sequence_id
        self._logger.info('setting sequence Id to {}', sequence_id)

        # retrieve context states only if there were none in mdibNode
        if len(self.contextStates.objects) == 0:
            self._get_context_states()
        else:
            self._logger.info('found context states in GetMdib Result, will not call getContextStates')

        # process buffered notifications
        with self._bufferedNotificationsLock:
            for bufferedReport in self._bufferedNotifications:
                bufferedReport.handler(bufferedReport.report, is_buffered_report=True)
            del self._bufferedNotifications[:]
            self._isInitialized = True

        #self._sdcClient._register_mdib(self)  # pylint: disable=protected-access
        self._logger.info('initializing mdib done')

    def _get_context_states(self):
        pass

    def _bind_to_observables(self):
        # observe properties of sdcClient
        properties.bind(self._sdcClient, waveFormReport=self._on_any_report)

    def _on_any_report(self, report, is_buffered_report=False):
        if not is_buffered_report and self._bufferNotification(report, self._on_any_report):
            return
        pass