import unittest
import logging
from decimal import Decimal
from sdc11073 import pmtypes
from sdc11073.namespaces import nsmap, domTag

from sdc11073.mdib import descriptorcontainers as dc
from sdc11073.transport.protobuf.mapping import descriptorsmapper as dm

def _start_logger():
    logger = logging.getLogger('pysdc.grpc')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

    def tearDown(self) -> None:
        _stop_logger(self._log_handler)

    def check_convert(self, obj):
        obj_p = dm.generic_descriptor_to_p(obj, None)
        print('\n################################# generic_from_p##################')
        obj2 = dm.generic_descriptor_from_p(obj_p, obj.parentHandle, nsmap)
        self.assertEqual(obj.__class__, obj2.__class__)
        self.assertIsNone(obj.diff(obj2))

    def test_mds_descriptor(self):
        mds_max = dc.MdsDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        mds_max.ProductionSpecification = [pmtypes.ProductionSpecification(pmtypes.CodedValue('abc', 'def'), 'prod_spec')]
        mds_max.Manufacturer = [pmtypes.LocalizedText('some_company')]
        mds_min = dc.MdsDescriptorContainer(nsmap, 'my_handle', None)
        for obj in (mds_max, mds_min):
            self.check_convert(obj)

    def test_vmd_descriptor(self):
        obj = dc.VmdDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self.check_convert(obj)

    def test_channel_descriptor(self):
        obj = dc.ChannelDescriptorContainer(nsmap, 'my_handle', None)
        self.check_convert(obj)

    def test_clock_descriptor(self):
        descr_max = dc.ClockDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.TimeProtocol = [pmtypes.CodedValue('abc', 'def'), pmtypes.CodedValue('123', '456')]
        descr_max.Resolution = 42.1
        descr_min = dc.ClockDescriptorContainer(nsmap, 'my_handle', None)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_battery_descriptor(self):
        descr_max = dc.BatteryDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.CapacityFullCharge = pmtypes.Measurement(Decimal('11'), pmtypes.CodedValue('ah'))
        descr_max.CapacitySpecified = pmtypes.Measurement(Decimal('12'), pmtypes.CodedValue('ah'))
        descr_max.VoltageSpecified = pmtypes.Measurement(Decimal('6'), pmtypes.CodedValue('v'))
        descr_min = dc.BatteryDescriptorContainer(nsmap, 'my_handle', None)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_sco_descriptor(self):
        obj = dc.ScoDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self.check_convert(obj)

    def test_numeric_metric_descriptor(self):
        # properties of AbstractMetricDescriptorContainer
        descr_max = dc.NumericMetricDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.Unit = pmtypes.CodedValue('ah')
        descr_max.BodySite = [pmtypes.CodedValue('ah')]
        descr_max.Relation = [pmtypes.Relation()]
        descr_max.MetricCategory = pmtypes.MetricCategory.PRESETTING #'Preset'
        descr_max.DerivationMethod = pmtypes.DerivationMethod.MANUAL #'Man'
        descr_max.MetricAvailability = 'Intr'
        descr_max.MaxMeasurementTime = 3
        descr_max.MaxDelayTime = 1
        descr_max.DeterminationPeriod = 1
        descr_max.LifeTimePeriod = 2
        descr_max.ActivationDuration = 3
        # properties of NumericMetricDescriptorContainer
        descr_max.TechnicalRange = [pmtypes.Range(0,20, 0.5)]
        descr_max.Resolution = Decimal('0.01')
        descr_max.AveragingPeriod = 0.02

        descr_min = dc.NumericMetricDescriptorContainer(nsmap, 'my_handle', None)
        descr_min.Resolution = Decimal('0.02')
        for obj in (descr_max, descr_min):
            self.check_convert(obj)


    def test_string_metric_descriptor(self):
        # properties of AbstractMetricDescriptorContainer
        descr_max = dc.StringMetricDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.Unit = pmtypes.CodedValue('ah')
        descr_max.BodySite = [pmtypes.CodedValue('ah')]
        descr_max.Relation = [pmtypes.Relation()]
        descr_max.MetricCategory = pmtypes.MetricCategory.PRESETTING #'Preset'
        descr_max.DerivationMethod = pmtypes.DerivationMethod.MANUAL #'Man'
        descr_max.MetricAvailability = 'Intr'
        descr_max.MaxMeasurementTime = 3
        descr_max.MaxDelayTime = 1
        descr_max.DeterminationPeriod = 1
        descr_max.LifeTimePeriod = 2
        descr_max.ActivationDuration = 3

        descr_min = dc.StringMetricDescriptorContainer(nsmap, 'my_handle', None)
        descr_min.Resolution = Decimal('0.02')
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_enum_string_metric_descriptor(self):
        # properties of AbstractMetricDescriptorContainer
        descr_max = dc.EnumStringMetricDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.Unit = pmtypes.CodedValue('ah')
        descr_max.BodySite = [pmtypes.CodedValue('ah')]
        descr_max.Relation = [pmtypes.Relation()]
        descr_max.MetricCategory = pmtypes.MetricCategory.PRESETTING #'Preset'
        descr_max.DerivationMethod = pmtypes.DerivationMethod.MANUAL #'Man'
        descr_max.MetricAvailability = 'Intr'
        descr_max.MaxMeasurementTime = 3
        descr_max.MaxDelayTime = 1
        descr_max.DeterminationPeriod = 1
        descr_max.LifeTimePeriod = 2
        descr_max.ActivationDuration = 3
        descr_max.AllowedValue = [pmtypes.AllowedValue('an_allowed_value', pmtypes.CodedValue('abc')),
                                  pmtypes.AllowedValue('another_allowed_value', pmtypes.CodedValue('def'))]

        descr_min = dc.StringMetricDescriptorContainer(nsmap, 'my_handle', None)
        descr_min.Resolution = Decimal('0.02')
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_realtime_sample_array_metric_descriptor(self):
        # properties of AbstractMetricDescriptorContainer
        descr_max = dc.RealTimeSampleArrayMetricDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.Unit = pmtypes.CodedValue('ah')
        descr_max.BodySite = [pmtypes.CodedValue('ah')]
        descr_max.Relation = [pmtypes.Relation()]
        descr_max.MetricCategory = pmtypes.MetricCategory.PRESETTING #'Preset'
        descr_max.DerivationMethod = pmtypes.DerivationMethod.MANUAL #'Man'
        descr_max.MetricAvailability = 'Intr'
        descr_max.MaxMeasurementTime = 3
        descr_max.MaxDelayTime = 1
        descr_max.DeterminationPeriod = 1
        descr_max.LifeTimePeriod = 2
        descr_max.ActivationDuration = 3

        descr_max.TechnicalRange = [pmtypes.Range(0, 1)]
        descr_max.Resolution = Decimal('0.02')
        descr_min = dc.RealTimeSampleArrayMetricDescriptorContainer(nsmap, 'my_handle', None)
        descr_min.Resolution = Decimal('0.02')
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_distribution_sample_array_metric_descriptor(self):
        # properties of AbstractMetricDescriptorContainer
        descr_max = dc.DistributionSampleArrayMetricDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.Unit = pmtypes.CodedValue('ah')
        descr_max.BodySite = [pmtypes.CodedValue('ah')]
        descr_max.Relation = [pmtypes.Relation()]
        descr_max.MetricCategory = pmtypes.MetricCategory.PRESETTING #'Preset'
        descr_max.DerivationMethod = pmtypes.DerivationMethod.MANUAL #'Man'
        descr_max.MetricAvailability = 'Intr'
        descr_max.MaxMeasurementTime = 3
        descr_max.MaxDelayTime = 1
        descr_max.DeterminationPeriod = 1
        descr_max.LifeTimePeriod = 2
        descr_max.ActivationDuration = 3

        descr_max.TechnicalRange = [pmtypes.Range(0, 1)]
        descr_max.Resolution = Decimal('0.02')
        descr_max.DomainUnit = pmtypes.CodedValue('abc')
        descr_max.DistributionRange = pmtypes.Range(0, 200, 0,1)
        descr_min = dc.DistributionSampleArrayMetricDescriptorContainer(nsmap, 'my_handle', None)
        descr_min.Resolution = Decimal('0.02')
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def _set_abstract_operation_descriptor(self, descr, max):
        descr.OperationTarget = '4711'
        if not max:
            return
        descr.MaxTimeToFinish = 1.1
        descr.InvocationEffectiveTimeout = 2
        descr.Retriggerable = False
        descr.MaxLength = 12

    def _set_abstract_set_state_operation_descriptor(self, descr, max):
        self._set_abstract_operation_descriptor(descr, max)
        if not max:
            return
        descr.ModifiableData = ['a', 'b']

    def test_set_value_operation_descriptor(self):
        descr_max = dc.SetValueOperationDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self._set_abstract_operation_descriptor(descr_max, True)
        descr_min = dc.SetValueOperationDescriptorContainer(nsmap, 'my_handle', None)
        self._set_abstract_operation_descriptor(descr_min, False)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_set_string_operation_descriptor(self):
        descr_max = dc.SetStringOperationDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self._set_abstract_operation_descriptor(descr_max, True)
        descr_min = dc.SetStringOperationDescriptorContainer(nsmap, 'my_handle', None)
        self._set_abstract_operation_descriptor(descr_min, False)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_set_context_state_operation_descriptor(self):
        descr_max = dc.SetContextStateOperationDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self._set_abstract_set_state_operation_descriptor(descr_max, True)
        descr_min = dc.SetContextStateOperationDescriptorContainer(nsmap, 'my_handle', None)
        self._set_abstract_set_state_operation_descriptor(descr_min, True)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_set_metric_state_operation_descriptor(self):
        descr_max = dc.SetMetricStateOperationDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self._set_abstract_set_state_operation_descriptor(descr_max, True)
        descr_min = dc.SetMetricStateOperationDescriptorContainer(nsmap, 'my_handle', None)
        self._set_abstract_set_state_operation_descriptor(descr_min, True)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_set_component_state_operation_descriptor(self):
        descr_max = dc.SetComponentStateOperationDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self._set_abstract_set_state_operation_descriptor(descr_max, True)
        descr_min = dc.SetComponentStateOperationDescriptorContainer(nsmap, 'my_handle', None)
        self._set_abstract_set_state_operation_descriptor(descr_min, True)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_set_alert_state_operation_descriptor(self):
        descr_max = dc.SetAlertStateOperationDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self._set_abstract_set_state_operation_descriptor(descr_max, True)
        descr_min = dc.SetAlertStateOperationDescriptorContainer(nsmap, 'my_handle', None)
        self._set_abstract_set_state_operation_descriptor(descr_min, True)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_activate_operation_descriptor(self):
        descr_max = dc.ActivateOperationDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        self._set_abstract_set_state_operation_descriptor(descr_max, True)
        descr_max.Argument = [pmtypes.ActivateOperationDescriptorArgument(pmtypes.CodedValue('aaa'), domTag('oh')),
                              pmtypes.ActivateOperationDescriptorArgument(pmtypes.CodedValue('bbb'), domTag('nooo')),]
        descr_min = dc.ActivateOperationDescriptorContainer(nsmap, 'my_handle', None)
        self._set_abstract_set_state_operation_descriptor(descr_min, True)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_alert_system_descriptor(self):
        descr_max = dc.AlertSystemDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.MaxPhysiologicalParallelAlarms = 3
        descr_max.MaxTechnicalParallelAlarms = 2
        descr_max.SelfCheckPeriod = 60.0
        descr_max.Argument = [pmtypes.ActivateOperationDescriptorArgument(pmtypes.CodedValue('aaa'), domTag('oh')),
                              pmtypes.ActivateOperationDescriptorArgument(pmtypes.CodedValue('bbb'), domTag('nooo')),]
        descr_min = dc.AlertSystemDescriptorContainer(nsmap, 'my_handle', None)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_alert_condition_descriptor(self):
        descr_max = dc.AlertConditionDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.Source = ['a', 'b']
        descr_max.CauseInfo = [pmtypes.CauseInfo(pmtypes.RemedyInfo([pmtypes.LocalizedText('rembla')]),
                                   [pmtypes.LocalizedText('caubla')])]
        descr_max.Kind = pmtypes.AlertConditionKind.PHYSIOLOGICAL
        descr_max.Priority = pmtypes.AlertConditionPriority.MEDIUM
        descr_max.DefaultConditionGenerationDelay = 2.5
        descr_max.CanEscalate = pmtypes.CanEscalateAlertConditionPriority.MEDIUM
        descr_max.CanDeescalate = pmtypes.CanDeEscalateAlertConditionPriority.LOW
        descr_min = dc.AlertConditionDescriptorContainer(nsmap, 'my_handle', None)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_limit_alert_condition_descriptor(self):
        descr_max = dc.LimitAlertConditionDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.Source = ['a', 'b']
        descr_max.CauseInfo = [pmtypes.CauseInfo(pmtypes.RemedyInfo([pmtypes.LocalizedText('rembla')]),
                                   [pmtypes.LocalizedText('caubla')])]
        descr_max.Kind = pmtypes.AlertConditionKind.PHYSIOLOGICAL
        descr_max.Priority = pmtypes.AlertConditionPriority.MEDIUM
        descr_max.DefaultConditionGenerationDelay = 2.5
        descr_max.CanEscalate = pmtypes.CanEscalateAlertConditionPriority.MEDIUM
        descr_max.CanDeescalate = pmtypes.CanDeEscalateAlertConditionPriority.LOW
        descr_max.MaxLimits = pmtypes.Range(0, 10)
        descr_max.AutoLimitSupported = True
        descr_min = dc.LimitAlertConditionDescriptorContainer(nsmap, 'my_handle', None)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_alert_signal_descriptor(self):
        descr_max = dc.AlertSignalDescriptorContainer(nsmap, 'my_handle', 'p_handle')
        descr_max.ConditionSignaled = 'handle123'
        descr_max.Manifestation = pmtypes.AlertSignalManifestation.AUD
        descr_max.Latching = True
        descr_max.DefaultSignalGenerationDelay = 1.5
        descr_max.SignalDelegationSupported = True
        descr_max.AcknowledgementSupported = True
        descr_max.AcknowledgeTimeout = 5.5
        descr_min = dc.AlertSignalDescriptorContainer(nsmap, 'my_handle', None)
        for obj in (descr_max, descr_min):
            self.check_convert(obj)

    def test_context_descriptors(self):
        # all these classes have no own properties, therefore no need for max and min variants
        for descr_cls in (dc.PatientContextDescriptorContainer,
                          dc.LocationContextDescriptorContainer,
                          dc.WorkflowContextDescriptorContainer,
                          dc.OperatorContextDescriptorContainer,
                          dc.MeansContextDescriptorContainer,
                          dc.EnsembleContextDescriptorContainer):
            descr = descr_cls(nsmap, 'my_handle', 'p_handle')
            self.check_convert(descr)
