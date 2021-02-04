import time
from sdc11073.mdib import clientmdib
from sdc11073 import observableproperties as properties
from org.somda.sdc.proto.model import sdc_messages_pb2

LOG_WF_AGE_INTERVAL = 30  # how often a log message is written with mean and standard-deviation of waveforms age
AGE_CALC_SAMPLES_COUNT = 100  # amount of data for wf mean age and standard-deviation calculation

A_NO_LOG = 0
A_OUT_OF_RANGE = 1
A_STILL_OUT_OF_RANGE = 2
A_BACK_IN_RANGE = 3


class GClientMdibContainer(clientmdib.ClientMdibContainer):

    def initMdib(self):
        if self._isInitialized:
            raise RuntimeError('ClientMdibContainer is already initialized')
        # first start receiving notifications, then call getMdib.
        # Otherwise we might miss notifications.
        self._bind_to_observables()

        cl_get_service = self._sdcClient.client('Get')
        self._logger.info('initializing mdib...')
        request = sdc_messages_pb2.GetMdibRequest()
        response = cl_get_service.GetMdib(request)
        self._logger.info('creating description containers...')
        descriptor_containers = self._msg_reader.readMdDescription(response.payload.mdib.md_description, self)
        with self.descriptions._lock:  # pylint: disable=protected-access
            self.descriptions.clear()
        self.addDescriptionContainers(descriptor_containers)
        self._logger.info('creating state containers...')
        self.clearStates()
        # state_containers = self._msg_reader.readMdState(response.payload.mdib.md_state, self)
        state_containers = self._msg_reader.read_states(response.payload.mdib.md_state.state, self)
        self.addStateContainers(state_containers)

        mdib_version = response.payload.mdib.a_mdib_version_group.a_mdib_version.value
        sequence_id = response.payload.mdib.a_mdib_version_group.a_sequence_id
        # instance_id = response.payload.mdib.a_mdib_version_group.a_instance_id.value
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
        self._logger.info('initializing mdib done')

    def _get_context_states(self):
        pass

    def _bind_to_observables(self):
        # observe properties of sdcClient
        properties.bind(self._sdcClient, anyReport=self._on_any_report)

    def _on_any_report(self, report, is_buffered_report=False):
        if not is_buffered_report and self._bufferNotification(report, self._on_any_report):
            print('_on_any_report: buffered')
            return
        print('_on_any_report: check version')
        print('_on_any_report: process')
        handler = None
        mdib_version_group = None
        actual_report = None
        if report.HasField('waveform'):
            actual_report = report.waveform
            mdib_version_group = actual_report.abstract_report.a_mdib_version_group
            handler = self._on_waveform_report
        elif report.HasField('metric'):
            actual_report = report.metric
            mdib_version_group = actual_report.abstract_metric_report.abstract_report.a_mdib_version_group
            handler = self._on_episodic_metric_report
        elif report.HasField('alert'):
            actual_report = report.alert
            mdib_version_group = actual_report.abstract_alert_report.abstract_report.a_mdib_version_group
            handler = self._on_episodic_alert_report
        elif report.HasField('component'):
            actual_report = report.component
            mdib_version_group = actual_report.abstract_component_report.abstract_report.a_mdib_version_group
            handler = self._on_episodic_component_report
        elif report.HasField('context'):
            actual_report = report.context
            mdib_version_group = actual_report.abstract_context_report.abstract_report.a_mdib_version_group
            handler = self._on_episodic_context_report
        elif report.HasField('description'):
            actual_report = report.description
            mdib_version_group = actual_report.abstract_report.a_mdib_version_group
            handler = self._on_description_modification_report
        elif report.HasField('operational_state'):
            actual_report = report.operational_state
            mdib_version_group = actual_report.abstract_report.a_mdib_version_group
        if handler:
            new_mdib_version = 0
            if mdib_version_group.HasField('a_mdib_version'):
                new_mdib_version = mdib_version_group.a_mdib_version.value
            if not self._canAcceptMdibVersion('_on_any_report', new_mdib_version):
                return
            return handler(actual_report, new_mdib_version, mdib_version_group.a_sequence_id, is_buffered_report)

    def _on_episodic_metric_report(self, report, new_mdib_version, sequence_id, is_buffered_report):
        print('_on_episodic_metric_report: process')
        now = time.time()
        metrics_by_handle = {}
        max_age = 0
        min_age = 0
        state_containers = []
        for report_part in report.abstract_metric_report.report_part:
            state_containers.extend(self._msg_reader.read_states(report_part.metric_state, self))
        try:
            with self.mdibLock:
                self.mdibVersion = new_mdib_version
                if sequence_id != self.sequenceId:
                    self.sequenceId = sequence_id
                for sc in state_containers:
                    if sc.descriptorContainer is not None and \
                            sc.descriptorContainer.DescriptorVersion != sc.DescriptorVersion:
                        self._logger.warn(
                            '_onEpisodicMetricReport: metric "{}": descriptor version expect "{}", found "{}"',
                            sc.descriptorHandle, sc.DescriptorVersion, sc.descriptorContainer.DescriptorVersion)
                        sc.descriptorContainer = None
                    try:
                        old_state_container = self.states.descriptorHandle.getOne(sc.descriptorHandle, allowNone=True)
                    except RuntimeError as ex:
                        self._logger.error('_onEpisodicMetricReport, getOne on states: {}', ex)
                        continue
                    desc_h = sc.descriptorHandle
                    metrics_by_handle[desc_h] = sc  # metric
                    if old_state_container is not None:
                        if self._hasNewStateUsableStateVersion(old_state_container, sc, 'EpisodicMetricReport',
                                                               is_buffered_report):
                            old_state_container.update_from_other_container(sc)
                            self.states.updateObject(old_state_container)
                    else:
                        self.states.addObject(sc)

                    if sc.metricValue is not None:
                        observation_time = sc.metricValue.DeterminationTime
                        if observation_time is None:
                            self._logger.warn(
                                '_onEpisodicMetricReport: metric {} version {} has no DeterminationTime',
                                desc_h, sc.StateVersion)
                        else:
                            age = now - observation_time
                            min_age = min(min_age, age)
                            max_age = max(max_age, age)
            shall_log = self.metric_time_warner.getOutOfDeterminationTimeLogState(
                min_age, max_age, self.DETERMINATIONTIME_WARN_LIMIT)
            if shall_log == A_OUT_OF_RANGE:
                self._logger.warn(
                    '_onEpisodicMetricReport mdibVersion {}: age of metrics outside limit of {} sec.: '
                    'max, min = {:03f}, {:03f}',
                    new_mdib_version, self.DETERMINATIONTIME_WARN_LIMIT, max_age, min_age)
            elif shall_log == A_STILL_OUT_OF_RANGE:
                self._logger.warn(
                    '_onEpisodicMetricReport mdibVersion {}: age of metrics still outside limit of {} sec.: '
                    'max, min = {:03f}, {:03f}',
                    new_mdib_version, self.DETERMINATIONTIME_WARN_LIMIT, max_age, min_age)
            elif shall_log == A_BACK_IN_RANGE:
                self._logger.info(
                    '_onEpisodicMetricReport mdibVersion {}: age of metrics back in limit of {} sec.: '
                    'max, min = {:03f}, {:03f}',
                    new_mdib_version, self.DETERMINATIONTIME_WARN_LIMIT, max_age, min_age)
        finally:
            self.metricsByHandle = metrics_by_handle  # used by waitMetricMatches method

    def _on_episodic_alert_report(self, report, new_mdib_version, sequence_id, is_buffered_report):
        print('_on_episodic_alert_report: process')
        alert_by_handle = {}
        try:
            state_containers = []
            for report_part in report.abstract_alert_report.report_part:
                state_containers.extend(self._msg_reader.read_states(report_part.alert_state, self))
            with self.mdibLock:
                self.mdibVersion = new_mdib_version
                if sequence_id != self.sequenceId:
                    self.sequenceId = sequence_id
                for sc in state_containers:
                    if sc.descriptorContainer is not None and \
                            sc.descriptorContainer.DescriptorVersion != sc.DescriptorVersion:
                        self._logger.warn(
                            '_on_episodic_alert_report: alert "{}": descriptor version expect "{}", found "{}"',
                            sc.descriptorHandle, sc.DescriptorVersion, sc.descriptorContainer.DescriptorVersion)
                        sc.descriptorContainer = None
                    try:
                        old_state_container = self.states.descriptorHandle.getOne(sc.descriptorHandle, allowNone=True)
                    except RuntimeError as ex:
                        self._logger.error('_onEpisodicAlertReport, getOne on states: {}', ex)
                        continue
                    # desc_h = sc.descriptorHandle

                    if old_state_container is not None:
                        if self._hasNewStateUsableStateVersion(old_state_container, sc, 'EpisodicAlertReport',
                                                               is_buffered_report):
                            old_state_container.update_from_other_container(sc)
                            self.states.updateObject(old_state_container)
                            alert_by_handle[old_state_container.descriptorHandle] = old_state_container
                    else:
                        self.states.addObject(sc)
                        alert_by_handle[sc.descriptorHandle] = sc
        finally:
            self.alertByHandle = alert_by_handle  # update observable

    def _on_waveform_report(self, report, new_mdib_version, sequence_id, is_buffered_report):
        print('_on_waveform_report: process')
        waveform_by_handle = {}
        waveform_age = {}  # collect age of all waveforms in this report,
        # and make one report if age is above warn limit (instead of multiple)
        try:
            all_states = self._msg_reader.read_states(report.state, self)

            with self.mdibLock:
                self.mdibVersion = new_mdib_version
                if sequence_id != self.sequenceId:
                    self.sequenceId = sequence_id
                for new_sac in all_states:
                    d_handle = new_sac.descriptorHandle
                    descriptor_container = new_sac.descriptorContainer
                    if descriptor_container is None:
                        self._logger.warn('_onWaveformReport: No Descriptor found for handle "{}"', d_handle)

                    old_state_container = self.states.descriptorHandle.getOne(d_handle, allowNone=True)
                    if old_state_container is None:
                        self.states.addObject(new_sac)
                        current_sc = new_sac
                    else:
                        if self._hasNewStateUsableStateVersion(old_state_container, new_sac,
                                                               'WaveformReport', is_buffered_report):
                            # update old state container from new one
                            old_state_container.update_from_other_container(new_sac)
                            self.states.updateObject(old_state_container)
                        current_sc = old_state_container  # we will need it later
                    waveform_by_handle[d_handle] = current_sc
                    # add to Waveform Buffer
                    rt_buffer = self.rtBuffers.get(d_handle)
                    if rt_buffer is None:
                        if descriptor_container is not None:
                            # read sample period
                            try:
                                sample_period = descriptor_container.SamplePeriod or 0
                            except AttributeError:
                                sample_period = 0  # default
                        rt_buffer = clientmdib.ClientRtBuffer(sample_period=sample_period,
                                                              max_samples=self._maxRealtimeSamples)
                        self.rtBuffers[d_handle] = rt_buffer
                    # last_sc = rt_buffer.last_sc
                    rt_sample_containers = rt_buffer.mkRtSampleContainers(new_sac)
                    rt_buffer.addRtSampleContainers(rt_sample_containers)

                    # check age
                    if len(rt_sample_containers) > 0:
                        waveform_age[d_handle] = rt_sample_containers[-1].age

                    # check descriptor version
                    if descriptor_container.DescriptorVersion != new_sac.DescriptorVersion:
                        self._logger.error('_onWaveformReport: descriptor {}: expect version "{}", found "{}"',
                                           d_handle, new_sac.DescriptorVersion, descriptor_container.DescriptorVersion)

            if len(waveform_age) > 0:
                min_age = min(waveform_age.values())
                max_age = max(waveform_age.values())
                shall_log = self.waveform_time_warner.getOutOfDeterminationTimeLogState(
                    min_age, max_age, self.DETERMINATIONTIME_WARN_LIMIT)
                if shall_log != A_NO_LOG:
                    tmp = ', '.join('"{}":{:.3f}sec.'.format(k, v) for k, v in waveform_age.items())
                    if shall_log == A_OUT_OF_RANGE:
                        self._logger.warn(
                            '_onWaveformReport mdibVersion {}: age of samples outside limit of {} sec.: age={}!',
                            new_mdib_version, self.DETERMINATIONTIME_WARN_LIMIT, tmp)
                    elif shall_log == A_STILL_OUT_OF_RANGE:
                        self._logger.warn(
                            '_onWaveformReport mdibVersion {}: age of samples still outside limit of {} sec.: age={}!',
                            new_mdib_version, self.DETERMINATIONTIME_WARN_LIMIT, tmp)
                    elif shall_log == A_BACK_IN_RANGE:
                        self._logger.info(
                            '_onWaveformReport mdibVersion {}: age of samples back in limit of {} sec.: age={}',
                            new_mdib_version, self.DETERMINATIONTIME_WARN_LIMIT, tmp)
            if LOG_WF_AGE_INTERVAL:
                now = time.time()
                if now - self._last_wf_age_log >= LOG_WF_AGE_INTERVAL:
                    age_data = self.get_wf_age_stdev()
                    self._logger.info('waveform mean age={:.1f}ms., std-dev={:.2f}ms. min={:.1f}ms., max={}',
                                      age_data.mean_age*1000., age_data.stdev*1000.,
                                      age_data.min_age*1000., age_data.max_age*1000.)
                    self._last_wf_age_log = now
        finally:
            self.waveformByHandle = waveform_by_handle

    def _on_episodic_component_report(self, report, new_mdib_version, sequence_id, is_buffered_report):
        print('_on_episodic_component_report: process')
        component_by_handle = {}
        state_containers = []
        for report_part in report.abstract_component_report.report_part:
            state_containers.extend(self._msg_reader.read_states(report_part.component_state, self))
        try:
            with self.mdibLock:
                self.mdibVersion = new_mdib_version
                if sequence_id != self.sequenceId:
                    self.sequenceId = sequence_id
                for sc in state_containers:
                    desc_h = sc.descriptorHandle
                    try:
                        old_state_container = self.states.descriptorHandle.getOne(desc_h, allowNone=True)
                    except RuntimeError  as ex:
                        self._logger.error('_on_episodic_component_report, getOne on states: {}', ex)
                        continue

                    if old_state_container is None:
                        self.states.addObject(sc)
                        self._logger.info(
                            '_onEpisodicComponentReport: new component state handle = {} DescriptorVersion={}',
                            desc_h, sc.DescriptorVersion)
                        component_by_handle[sc.descriptorHandle] = sc
                    else:
                        if self._hasNewStateUsableStateVersion(old_state_container, sc, 'EpisodicComponentReport',
                                                               is_buffered_report):
                            self._logger.info(
                                '_onEpisodicComponentReport: updated component state, handle="{}" DescriptorVersion={}',
                                desc_h, sc.DescriptorVersion)
                            old_state_container.update_from_other_container(sc)
                            self.states.updateObject(old_state_container)
                            component_by_handle[old_state_container.descriptorHandle] = old_state_container
        finally:
            self.componentByHandle = component_by_handle

    def _on_episodic_context_report(self, report, new_mdib_version, sequence_id, is_buffered_report):
        print('_on_episodic_context_report: process')
        context_by_handle = {}
        state_containers = []
        for report_part in report.abstract_context_report.report_part:
            state_containers.extend(self._msg_reader.read_states(report_part.context_state, self))
        try:
            with self.mdibLock:
                self.mdibVersion = new_mdib_version
                if sequence_id != self.sequenceId:
                    self.sequenceId = sequence_id
                for sc in state_containers:
                    try:
                        old_state_container = self.contextStates.handle.getOne(sc.Handle, allowNone=True)
                    except RuntimeError  as ex:
                        self._logger.error('_onEpisodicContextReport, getOne on contextStates: {}', ex)
                        continue

                    if old_state_container is None:
                        self.contextStates.addObject(sc)
                        self._logger.info(
                            '_on_episodic_context_report: new context state handle = {} Descriptor Handle={} Assoc={}, Validators={}',
                            sc.Handle, sc.descriptorHandle, sc.ContextAssociation, sc.Validator)
                        context_by_handle[sc.Handle] = sc
                    else:
                        if self._hasNewStateUsableStateVersion(old_state_container, sc, 'EpisodicContextReport', is_buffered_report):
                            self._logger.info(
                                '_on_episodic_context_report: updated context state handle = {} Descriptor Handle={} Assoc={}, Validators={}',
                                sc.Handle, sc.descriptorHandle, sc.ContextAssociation, sc.Validator)
                            old_state_container.update_from_other_container(sc)
                            self.contextStates.updateObject(old_state_container)
                            context_by_handle[old_state_container.Handle] = old_state_container
        finally:
            self.contextByHandle = context_by_handle

    def _on_description_modification_report(self, report, new_mdib_version, sequence_id, is_buffered_report):
        print('_on_description_modification_report: process')
        new_descriptor_by_handle = {}
        updated_descriptor_by_handle = {}
        with self.mdibLock:
            self.mdibVersion = new_mdib_version
            if sequence_id != self.sequenceId:
                self.sequenceId = sequence_id
            for report_part in report.report_part:
                descriptor_containers = self._msg_reader.read_descriptors(report_part.descriptorx_xx,
                                                                          report_part.a_parent_descriptor, self)
                if report_part.a_modification_type.enum_value == 0:  # CRT
                    for dc in descriptor_containers:
                        self.descriptions.addObject(dc)
                        self._logger.debug('_onDescriptionModificationReport: created description "{}" (parent="{}")',
                                           dc.handle, dc.parentHandle)
                        new_descriptor_by_handle[dc.handle] = dc
                    state_containers = self._msg_reader.read_states(report_part.state, self)
                    for sc in state_containers:
                        # determine multikey
                        if sc.isContextState:
                            multikey = self.contextStates
                        else:
                            multikey = self.states
                        multikey.addObject(sc)
                elif report_part.a_modification_type.enum_value == 1:  # UPD
                    for dc in descriptor_containers:
                        self._logger.info('_onDescriptionModificationReport: update descriptor "{}" (parent="{}")',
                                          dc.handle, dc.parentHandle)
                        container = self.descriptions.handle.getOne(dc.handle, allowNone=True)
                        if container is None:
                            pass
                        else:
                            container.update_from_other_container(dc)
                        updated_descriptor_by_handle[dc.handle] = dc
                    state_containers = self._msg_reader.read_states(report_part.state, self)
                    for sc in state_containers:
                        # determine multikey
                        if sc.isContextState:
                            multikey = self.contextStates
                            old_state_container = multikey.handle.getOne(sc.Handle, allowNone=True)
                        else:
                            multikey = self.states
                            old_state_container = multikey.descriptorHandle.getOne(sc.descriptorHandle, allowNone=True)
                        if old_state_container is not None:
                            old_state_container.update_from_other_container(sc)
                            multikey.updateObject(old_state_container)
                else:  # DEL
                    for dc in descriptor_containers:
                        self._logger.debug('_onDescriptionModificationReport: remove descriptor "{}" (parent="{}")',
                                           dc.handle, dc.parentHandle)
                        self.rmDescriptorHandleAll(
                            dc.handle)  # handling of self.deletedDescriptorByHandle inside called method

                # write observables for every report part separately
                if new_descriptor_by_handle:
                    self.newDescriptorByHandle = new_descriptor_by_handle
                if updated_descriptor_by_handle:
                    self.updatedDescriptorByHandle = updated_descriptor_by_handle
