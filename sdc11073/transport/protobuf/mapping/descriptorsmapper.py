import logging
from sdc11073.mdib import descriptorcontainers as dc
from .pmtypesmapper import generic_from_p, generic_to_p
from .mapping_common import find_one_of_p_for_container, find_populated_one_of
from org.somda.sdc.proto.model.biceps.mdsdescriptor_pb2 import MdsDescriptorMsg
from org.somda.sdc.proto.model.biceps.vmddescriptor_pb2 import VmdDescriptorMsg
from org.somda.sdc.proto.model.biceps.channeldescriptor_pb2 import ChannelDescriptorMsg
from org.somda.sdc.proto.model.biceps.scodescriptor_pb2 import ScoDescriptorMsg
from org.somda.sdc.proto.model.biceps.clockdescriptor_pb2 import ClockDescriptorMsg
from org.somda.sdc.proto.model.biceps.batterydescriptor_pb2 import BatteryDescriptorMsg
from org.somda.sdc.proto.model.biceps.numericmetricdescriptor_pb2 import NumericMetricDescriptorMsg
from org.somda.sdc.proto.model.biceps.stringmetricdescriptor_pb2 import StringMetricDescriptorMsg
from org.somda.sdc.proto.model.biceps.enumstringmetricdescriptor_pb2 import EnumStringMetricDescriptorMsg
from org.somda.sdc.proto.model.biceps.realtimesamplearraymetricdescriptor_pb2 import RealTimeSampleArrayMetricDescriptorMsg
from org.somda.sdc.proto.model.biceps.abstractmetricdescriptoroneof_pb2 import AbstractMetricDescriptorOneOfMsg
from org.somda.sdc.proto.model.biceps.stringmetricdescriptoroneof_pb2 import StringMetricDescriptorOneOfMsg
from org.somda.sdc.proto.model.biceps.distributionsamplearraymetricdescriptor_pb2 import DistributionSampleArrayMetricDescriptorMsg
from org.somda.sdc.proto.model.biceps.setvalueoperationdescriptor_pb2 import SetValueOperationDescriptorMsg
from org.somda.sdc.proto.model.biceps.setstringoperationdescriptor_pb2 import SetStringOperationDescriptorMsg
from org.somda.sdc.proto.model.biceps.setcontextstateoperationdescriptor_pb2 import SetContextStateOperationDescriptorMsg
from org.somda.sdc.proto.model.biceps.setmetricstateoperationdescriptor_pb2 import SetMetricStateOperationDescriptorMsg
from org.somda.sdc.proto.model.biceps.setcomponentstateoperationdescriptor_pb2 import SetComponentStateOperationDescriptorMsg
from org.somda.sdc.proto.model.biceps.setalertstateoperationdescriptor_pb2 import SetAlertStateOperationDescriptorMsg
from org.somda.sdc.proto.model.biceps.activateoperationdescriptor_pb2 import ActivateOperationDescriptorMsg
from org.somda.sdc.proto.model.biceps.abstractoperationdescriptoroneof_pb2 import AbstractOperationDescriptorOneOfMsg
from org.somda.sdc.proto.model.biceps.alertsystemdescriptor_pb2 import AlertSystemDescriptorMsg
from org.somda.sdc.proto.model.biceps.alertconditiondescriptor_pb2 import AlertConditionDescriptorMsg
from org.somda.sdc.proto.model.biceps.alertconditiondescriptoroneof_pb2 import AlertConditionDescriptorOneOfMsg
from org.somda.sdc.proto.model.biceps.limitalertconditiondescriptor_pb2 import LimitAlertConditionDescriptorMsg
from org.somda.sdc.proto.model.biceps.alertsignaldescriptor_pb2 import AlertSignalDescriptorMsg
from org.somda.sdc.proto.model.biceps.patientcontextdescriptor_pb2 import PatientContextDescriptorMsg
from org.somda.sdc.proto.model.biceps.locationcontextdescriptor_pb2 import LocationContextDescriptorMsg
from org.somda.sdc.proto.model.biceps.workflowcontextdescriptor_pb2 import WorkflowContextDescriptorMsg
from org.somda.sdc.proto.model.biceps.operatorcontextdescriptor_pb2 import OperatorContextDescriptorMsg
from org.somda.sdc.proto.model.biceps.meanscontextdescriptor_pb2 import MeansContextDescriptorMsg
from org.somda.sdc.proto.model.biceps.ensemblecontextdescriptor_pb2 import EnsembleContextDescriptorMsg
from org.somda.sdc.proto.model.biceps.systemcontextdescriptor_pb2 import SystemContextDescriptorMsg
from org.somda.sdc.proto.model.biceps.abstractdescriptoroneof_pb2 import AbstractDescriptorOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractalertdescriptoroneof_pb2 import AbstractAlertDescriptorOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractdevicecomponentdescriptoroneof_pb2 import AbstractDeviceComponentDescriptorOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractcomplexdevicecomponentdescriptoroneof_pb2 import AbstractComplexDeviceComponentDescriptorOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractsetstateoperationdescriptoroneof_pb2 import AbstractSetStateOperationDescriptorOneOfMsg
_logger = logging.getLogger('pysdc.grpc.map.descriptor')

_to_cls= {}
_to_cls[dc.MdsDescriptorContainer] = MdsDescriptorMsg
_to_cls[dc.VmdDescriptorContainer] = VmdDescriptorMsg
_to_cls[dc.ChannelDescriptorContainer] = ChannelDescriptorMsg
_to_cls[dc.ScoDescriptorContainer] = ScoDescriptorMsg
_to_cls[dc.ClockDescriptorContainer] = ClockDescriptorMsg
_to_cls[dc.BatteryDescriptorContainer] = BatteryDescriptorMsg
_to_cls[dc.NumericMetricDescriptorContainer] = NumericMetricDescriptorMsg
_to_cls[dc.StringMetricDescriptorContainer] = StringMetricDescriptorMsg
_to_cls[dc.EnumStringMetricDescriptorContainer] = EnumStringMetricDescriptorMsg
_to_cls[dc.RealTimeSampleArrayMetricDescriptorContainer] = RealTimeSampleArrayMetricDescriptorMsg
_to_cls[dc.DistributionSampleArrayMetricDescriptorContainer] = DistributionSampleArrayMetricDescriptorMsg
_to_cls[dc.SetValueOperationDescriptorContainer] = SetValueOperationDescriptorMsg
_to_cls[dc.SetStringOperationDescriptorContainer] = SetStringOperationDescriptorMsg
_to_cls[dc.SetContextStateOperationDescriptorContainer] = SetContextStateOperationDescriptorMsg
_to_cls[dc.SetMetricStateOperationDescriptorContainer] = SetMetricStateOperationDescriptorMsg
_to_cls[dc.SetComponentStateOperationDescriptorContainer] = SetComponentStateOperationDescriptorMsg
_to_cls[dc.SetAlertStateOperationDescriptorContainer] = SetAlertStateOperationDescriptorMsg
_to_cls[dc.ActivateOperationDescriptorContainer] = ActivateOperationDescriptorMsg
_to_cls[dc.AlertSystemDescriptorContainer] = AlertSystemDescriptorMsg
_to_cls[dc.AlertConditionDescriptorContainer] = AlertConditionDescriptorMsg
_to_cls[dc.LimitAlertConditionDescriptorContainer] = LimitAlertConditionDescriptorMsg
_to_cls[dc.AlertSignalDescriptorContainer] = AlertSignalDescriptorMsg
_to_cls[dc.PatientContextDescriptorContainer] = PatientContextDescriptorMsg
_to_cls[dc.LocationContextDescriptorContainer] = LocationContextDescriptorMsg
_to_cls[dc.WorkflowContextDescriptorContainer] = WorkflowContextDescriptorMsg
_to_cls[dc.OperatorContextDescriptorContainer] = OperatorContextDescriptorMsg
_to_cls[dc.MeansContextDescriptorContainer] = MeansContextDescriptorMsg
_to_cls[dc.EnsembleContextDescriptorContainer] = EnsembleContextDescriptorMsg
_to_cls[dc.SystemContextDescriptorContainer] = SystemContextDescriptorMsg

# invert for other direction lookup
_from_cls = dict((v, k) for (k, v) in _to_cls.items())


_one_of_descr_fields = {
    AbstractDescriptorOneOfMsg: ('abstract_alert_descriptor_one_of',
                                 'abstract_device_component_descriptor_one_of',
                                 'abstract_metric_descriptor_one_of',
                                 'abstract_multi_descriptor_one_of',
                                 'abstract_operation_descriptor_one_of'),
    AbstractMetricDescriptorOneOfMsg: ('numeric_metric_descriptor',
                                       'real_time_sample_array_metric_descriptor',
                                       'string_metric_descriptor_one_of',
                                       'distribution_sample_array_metric_descriptor'),
    StringMetricDescriptorOneOfMsg: ('enum_string_metric_descriptor',
                                     'string_metric_descriptor'),
    AbstractAlertDescriptorOneOfMsg: ('alert_condition_descriptor_one_of',
                                      'alert_signal_descriptor',
                                      'alert_system_descriptor'),
    AlertConditionDescriptorOneOfMsg: ('alert_condition_descriptor',
                                       'limit_alert_condition_descriptor'),
    AbstractDeviceComponentDescriptorOneOfMsg: ('abstract_complex_device_component_descriptor_one_of',
                                                'abstract_device_component_descriptor',
                                                'battery_descriptor',
                                                'channel_descriptor',
                                                'clock_descriptor',
                                                'sco_descriptor',
                                                'system_context_descriptor'),
    AbstractComplexDeviceComponentDescriptorOneOfMsg: ('mds_descriptor', 'vmd_descriptor'),
    AbstractOperationDescriptorOneOfMsg: ('abstract_set_state_operation_descriptor_one_of',
                                          'set_string_operation_descriptor',
                                          'set_value_operation_descriptor'),
    AbstractSetStateOperationDescriptorOneOfMsg: ('activate_operation_descriptor',
                                                  'set_alert_state_operation_descriptor',
                                                  'set_component_state_operation_descriptor',
                                                  'set_context_state_operation_descriptor',
                                                  'set_metric_state_operation_descriptor'),
}


# def find_one_of_descr(p):
#     return find_populated_one_of(p, _one_of_descr_fields)


def generic_descriptor_to_p(descr, p):
    try:
        if p is None:
            cls = _to_cls[descr.__class__]
            p = cls()
        if p.__class__ in _one_of_descr_fields:
            p = find_one_of_p_for_container(descr, p)
        generic_to_p(descr, p)
        return p
    except:
        raise


def generic_descriptor_from_p(p, parent_handle, nsmap):
    p_field = find_populated_one_of(p, _one_of_descr_fields)
    cls = _from_cls[p_field.__class__]
    ret = cls(nsmap, None, parent_handle)
    generic_from_p(p_field, ret)
    return ret
