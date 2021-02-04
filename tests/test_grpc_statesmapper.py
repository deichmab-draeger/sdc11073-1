import unittest
import logging
from decimal import Decimal
import time
from sdc11073 import pmtypes
from sdc11073.namespaces import nsmap, domTag

from sdc11073.mdib import statecontainers as sc
from sdc11073.mdib.descriptorcontainers import AbstractDescriptorContainer
from sdc11073.transport.protobuf.mapping import statesmapper as sm

def _start_logger():
    logger = logging.getLogger('pysdc.grpc.map')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    # create formatter
    #formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter("%(name)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return ch

def _stop_logger(handler):
    logger = logging.getLogger('pysdc.grpc.map')
    logger.setLevel(logging.WARNING)
    logger.removeHandler(handler)

class TestDescriptorsMapper(unittest.TestCase):
    def setUp(self) -> None:
        self._log_handler = _start_logger()
        self.descr = AbstractDescriptorContainer(nsmap, 'my_handle', 'parent_handle')
        self.descr.DescriptorVersion = 42

    def tearDown(self) -> None:
        _stop_logger(self._log_handler)

    def check_convert(self,obj):
        obj_p = sm.generic_state_to_p(obj, None)
        print('\n################################# generic_from_p##################')
        obj2 = sm.generic_state_from_p(obj_p, nsmap, self.descr)
        self.assertEqual(obj.__class__, obj2.__class__)
        self.assertIsNone(obj.diff(obj2))
        self.assertEqual(obj.DescriptorVersion, self.descr.DescriptorVersion)

    def test_set_value_operation_state(self):
        st_max = sc.SetValueOperationStateContainer(nsmap, self.descr)
        st_max.AllowedRange = [pmtypes.Range(0, 100.0)]
        st_min = sc.SetValueOperationStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_set_string_operation_state(self):
        st_max = sc.SetStringOperationStateContainer(nsmap, self.descr)
        st_max.AllowedValues = ['a', 'b']
        st_min = sc.SetStringOperationStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_operation_states(self):
        for state_cls in [sc.ActivateOperationStateContainer,
                           sc.SetContextStateOperationStateContainer,
                           sc.SetMetricStateOperationStateContainer,
                           sc.SetComponentStateOperationStateContainer,
                           sc.SetAlertStateOperationStateContainer]:
            obj = state_cls(nsmap, self.descr)
            self.check_convert(obj)

    def test_numeric_metric_state(self):
        st_max = sc.NumericMetricStateContainer(nsmap, self.descr)
        st_max.mkMetricValue()
        st_max.BodySite = [pmtypes.CodedValue('abc'), pmtypes.CodedValue('def')]
        st_max.PhysicalConnector = pmtypes.PhysicalConnectorInfo(
            [pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)
        st_max.ActivationState = pmtypes.ComponentActivation.NOT_READY
        st_max.ActiveDeterminationPeriod = 5.5
        st_max.LifeTimePeriod = 9.0
        st_min = sc.NumericMetricStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_string_metric_state(self):
        st_max = sc.StringMetricStateContainer(nsmap, self.descr)
        st_max.mkMetricValue()
        st_min = sc.StringMetricStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_enum_string_metric_state(self):
        st_max = sc.EnumStringMetricStateContainer(nsmap, self.descr)
        st_max.mkMetricValue()
        st_min = sc.EnumStringMetricStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_realtime_sample_array_metric_state(self):
        st_max = sc.RealTimeSampleArrayMetricStateContainer(nsmap, self.descr)
        st_max.mkMetricValue()
        st_max.PhysiologicalRange = [pmtypes.Range(1, 2), pmtypes.Range(3, 4)]
        st_min = sc.RealTimeSampleArrayMetricStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_distribution_sample_array_metric_state(self):
        st_max = sc.DistributionSampleArrayMetricStateContainer(nsmap, self.descr)
        st_max.mkMetricValue()
        st_max.PhysiologicalRange = [pmtypes.Range(1, 2), pmtypes.Range(3, 4)]
        st_min = sc.DistributionSampleArrayMetricStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_mds_state(self):
        st_max = sc.MdsStateContainer(nsmap, self.descr)
        # AbstractStateContainer
        st_max.StateVersion = 5
        # AbstractDeviceComponentStateContainer
        # st_max.CalibrationInfo = cp.NotImplementedProperty('CalibrationInfo', None)  # optional, CalibrationInfo type
        # st_max.NextCalibration = cp.NotImplementedProperty('NextCalibration', None)  # optional, CalibrationInfo type
        st_max.PhysicalConnector = pmtypes.PhysicalConnectorInfo(
            [pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)

        st_max.ActivationState = pmtypes.ComponentActivation.FAILURE
        st_max.OperatingHours = 42
        st_max.OperatingCycles = 101
        # MdsStateContainer
        st_max.OperatingMode = pmtypes.MdsOperatingMode.DEMO
        st_max.Lang = 'xx'
        st_min = sc.MdsStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_sco_state(self):
        st_max = sc.ScoStateContainer(nsmap, self.descr)
        # AbstractStateContainer
        st_max.StateVersion = 5
        # AbstractDeviceComponentStateContainer
        st_max.PhysicalConnector = pmtypes.PhysicalConnectorInfo(
            [pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)

        st_max.ActivationState = pmtypes.ComponentActivation.FAILURE
        st_max.OperatingHours = 42
        st_max.OperatingCycles = 101
        # ScoStateContainer
        st_max.OperationGroup = [pmtypes.OperationGroup(pmtypes.CodedValue('abc'))]
        st_max.InvocationRequested = ['handle1', 'handle2']
        st_max.InvocationRequired =  ['handle3', 'handle3']
        st_min = sc.ScoStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_vmd_state(self):
        st_max = sc.VmdStateContainer(nsmap, self.descr)
        # AbstractStateContainer
        st_max.StateVersion = 5
        # AbstractDeviceComponentStateContainer
        st_max.PhysicalConnector = pmtypes.PhysicalConnectorInfo(
            [pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)

        st_max.ActivationState = pmtypes.ComponentActivation.FAILURE
        st_max.OperatingHours = 42
        st_max.OperatingCycles = 101
        st_min = sc.VmdStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_channel_state(self):
        st_max = sc.ChannelStateContainer(nsmap, self.descr)
        # AbstractStateContainer
        st_max.StateVersion = 5
        # AbstractDeviceComponentStateContainer
        st_max.PhysicalConnector = pmtypes.PhysicalConnectorInfo(
            [pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)

        st_max.ActivationState = pmtypes.ComponentActivation.FAILURE
        st_max.OperatingHours = 42
        st_max.OperatingCycles = 101
        st_min = sc.ChannelStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_clock_state(self):
        st_max = sc.ClockStateContainer(nsmap, self.descr)
        # AbstractStateContainer
        st_max.StateVersion = 5
        # AbstractDeviceComponentStateContainer
        st_max.PhysicalConnector = pmtypes.PhysicalConnectorInfo(
            [pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)

        st_max.ActivationState = pmtypes.ComponentActivation.FAILURE
        st_max.OperatingHours = 42
        st_max.OperatingCycles = 101
        st_min = sc.ClockStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_system_context_state(self):
        st_max = sc.SystemContextStateContainer(nsmap, self.descr)
        # AbstractStateContainer
        st_max.StateVersion = 5
        # AbstractDeviceComponentStateContainer
        st_max.PhysicalConnector = pmtypes.PhysicalConnectorInfo(
            [pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)

        st_max.ActivationState = pmtypes.ComponentActivation.FAILURE
        st_max.OperatingHours = 42
        st_max.OperatingCycles = 101
        st_min = sc.SystemContextStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_battery_state(self):
        st_max = sc.BatteryStateContainer(nsmap, self.descr)
        # AbstractStateContainer
        st_max.StateVersion = 5
        # AbstractDeviceComponentStateContainer
        st_max.PhysicalConnector = pmtypes.PhysicalConnectorInfo(
            [pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)

        st_max.ActivationState = pmtypes.ComponentActivation.FAILURE
        st_max.OperatingHours = 42
        st_max.OperatingCycles = 101
        # BatteryState
        st_max.CapacityRemaining = pmtypes.Measurement(42, pmtypes.CodedValue('abc'))
        st_max.Voltage = pmtypes.Measurement(12, pmtypes.CodedValue('def'))
        st_max.Current = pmtypes.Measurement(2, pmtypes.CodedValue('xyz'))
        st_max.Temperature = pmtypes.Measurement(70, pmtypes.CodedValue('xyz'))
        st_max.RemainingBatteryTime = pmtypes.Measurement(3, pmtypes.CodedValue('xyz'))
        st_max.ChargeStatus = st_max.T_ChargeStatus.CHARGING
        st_max.ChargeCycles = 123
        st_min = sc.BatteryStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_alert_system_state(self):
        st_max = sc.AlertSystemStateContainer(nsmap, self.descr)
        # AbstractState
        st_max.StateVersion = 5
        # AbstractAlertState
        st_max.ActivationState = pmtypes.AlertActivation.PAUSED
        # AlertSystemState
        st_max.SystemSignalActivation
        st_max.LastSelfCheck = int(time.time())
        st_max.SelfCheckCount = 3
        st_max.PresentPhysiologicalAlarmConditions = ['a', 'b']
        st_max.PresentTechnicalAlarmConditions = ['c', 'd']
        st_min = sc.AlertSystemStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_alert_signal_state(self):
        self.descr.SignalDelegationSupported = True
        st_max = sc.AlertSignalStateContainer(nsmap, self.descr)
        # AbstractState
        st_max.StateVersion = 5
        # AbstractAlertState
        st_max.ActivationState = pmtypes.AlertActivation.PAUSED
        # AlertSignalState
        st_max.ActualSignalGenerationDelay = 0.2
        st_max.Presence = pmtypes.AlertSignalPresence.ACK
        st_max.Location = pmtypes.AlertSignalPrimaryLocation.REMOTE
        st_max.Slot = 3

        st_min = sc.AlertSystemStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_alert_condition_state(self):
        st_max = sc.AlertConditionStateContainer(nsmap, self.descr)
        # AbstractState
        st_max.StateVersion = 5
        # AbstractAlertState
        st_max.ActivationState = pmtypes.AlertActivation.PAUSED
        # AlertConditionState
        st_max.ActualConditionGenerationDelay = 0.2
        st_max.ActualPriority = pmtypes.AlertConditionPriority.HIGH
        st_max.Rank = 2
        st_max.DeterminationTime = 1234567
        st_max.Presence = True

        st_min = sc.AlertConditionStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_limit_alert_condition_state(self):
        st_max = sc.LimitAlertConditionStateContainer(nsmap, self.descr)
        # AbstractState
        st_max.StateVersion = 5
        # AbstractAlertState
        st_max.ActivationState = pmtypes.AlertActivation.PAUSED
        # AlertConditionState
        st_max.ActualConditionGenerationDelay = 0.2
        st_max.ActualPriority = pmtypes.AlertConditionPriority.HIGH
        st_max.Rank = 2
        st_max.DeterminationTime = 1234567
        st_max.Presence = True
        # LimitAlertConditionState
        st_max.Limits = pmtypes.Range(0, 100, 0.5)
        st_max.MonitoredAlertLimits = pmtypes.AlertConditionMonitoredLimits.HIGH_OFF
        st_max.AutoLimitActivationState = pmtypes.AlertActivation.PAUSED
        st_min = sc.LimitAlertConditionStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_location_context_state(self):
        st_max = sc.LocationContextStateContainer(nsmap, self.descr)
        # AbstractState
        st_max.StateVersion = 5
        # AbstractContextState
        st_max.Validator = [pmtypes.InstanceIdentifier('abc')]
        st_max.Identification = [pmtypes.InstanceIdentifier('def')]
        st_max.ContextAssociation = pmtypes.ContextAssociation.PRE_ASSOCIATION
        st_max.BindingMdibVersion = 12
        st_max.UnbindingMdibVersion = 15
        st_max.BindingStartTime = 12345
        st_max.BindingEndTime = 12346
        # LocationContextState
        st_max.LocationDetail.Poc = 'Poc'
        st_max.LocationDetail.Room = 'Room'
        st_max.LocationDetail.Bed = 'Bed'
        st_max.LocationDetail.Facility = 'Facility'
        st_max.LocationDetail.Building = 'Building'
        st_max.LocationDetail.Floor = 'Floor'
        st_min = sc.LocationContextStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)

    def test_patient_context_state(self):
        st_max = sc.PatientContextStateContainer(nsmap, self.descr)
        # AbstractState
        st_max.StateVersion = 5
        # AbstractContextState
        st_max.Validator = [pmtypes.InstanceIdentifier('abc')]
        st_max.Identification = [pmtypes.InstanceIdentifier('def')]
        st_max.ContextAssociation = pmtypes.ContextAssociation.PRE_ASSOCIATION
        st_max.BindingMdibVersion = 12
        st_max.UnbindingMdibVersion = 15
        st_max.BindingStartTime = 12345
        st_max.BindingEndTime = 12346
        st_max.CoreData.PoC = 'Poc'
        # PatientContextState
        st_max.CoreData.Givenname = 'gg'
        st_max.CoreData.Middlename = ['mm']
        st_max.CoreData.Familyname = 'ff'
        st_max.CoreData.Birthname = 'bb'
        st_max.CoreData.Title = 'tt'
        st_max.CoreData.Sex = 'F'
        st_min = sc.PatientContextStateContainer(nsmap, self.descr)
        for obj in (st_max, st_min):
            self.check_convert(obj)
