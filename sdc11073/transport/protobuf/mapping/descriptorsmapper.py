from sdc11073.mdib import descriptorcontainers as dc
from .pmtypesmapper import generic_from_p, generic_to_p
#from org.somda.sdc.proto.model .biceps
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


def alert_condition_descriptor_to_oneof_p(
        acd:dc.AbstractAlertDescriptorContainer,
        p:AlertConditionDescriptorOneOfMsg)->AlertConditionDescriptorOneOfMsg:
    if p is None:
        p = AlertConditionDescriptorOneOfMsg()
    if isinstance(acd, dc.LimitAlertConditionDescriptorContainer):
        generic_to_p(acd, p.limit_alert_condition_descriptor, '   (alert_condition_descriptor_to_oneof_p)')
    elif isinstance(acd, dc.AlertConditionDescriptorContainer):
        generic_to_p(acd, p.alert_condition_descriptor, '   (alert_condition_descriptor_to_oneof_p)')
    else:
        raise TypeError(f'alert_condition_descriptor_to_oneof_p cannot handle cls {acd.__class__}')
    return p


def alert_condition_descriptor_from_oneof_p(p:AlertConditionDescriptorOneOfMsg, parent_handle, nsmap) -> dc.AbstractAlertDescriptorContainer:
    if p.HasField('limit_alert_condition_descriptor'):
        ret = dc.LimitAlertConditionDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.limit_alert_condition_descriptor, ret, indent='   (alert_condition_descriptor_from_oneof_p)')
        return ret
    elif p.HasField('alert_condition_descriptor'):
        ret = dc.AlertConditionDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.alert_condition_descriptor, ret, indent='   (alert_condition_descriptor_from_oneof_p)')
        return ret
    else:
        raise TypeError(f'alert_condition_descriptor_from_oneof_p cannot handle cls {p.__class__}')


def stringmetric_descriptor_to_p(descr: dc.StringMetricDescriptorContainer,
                           p: [StringMetricDescriptorOneOfMsg, None]) -> StringMetricDescriptorOneOfMsg:
    if p is None:
        p = StringMetricDescriptorOneOfMsg()
    if isinstance(descr, dc.EnumStringMetricDescriptorContainer):
        generic_to_p(descr, p.enum_string_metric_descriptor)
    elif isinstance(descr, dc.StringMetricDescriptorContainer):
        generic_to_p(descr, p.string_metric_descriptor)
    else:
        raise TypeError(f'metric_descriptor_to_p cannot handle cls {descr.__class__}')
    return p


def abstract_metric_descriptor_to_p(descr: dc.AbstractMetricDescriptorContainer,
                           p: [AbstractMetricDescriptorOneOfMsg, None]) -> AbstractMetricDescriptorOneOfMsg:
    if p is None:
        p = AbstractMetricDescriptorOneOfMsg()
    if isinstance(descr, dc.NumericMetricDescriptorContainer):
        generic_to_p(descr, p.numeric_metric_descriptor)
    elif isinstance(descr, dc.StringMetricDescriptorContainer):
        stringmetric_descriptor_to_p(descr, p.string_metric_descriptor_one_of)
    elif isinstance(descr, dc.RealTimeSampleArrayMetricDescriptorContainer):
        generic_to_p(descr, p.real_time_sample_array_metric_descriptor)
    else:
        raise TypeError(f'metric_descriptor_to_p cannot handle cls {descr.__class__}')
    return p


def string_metric_descriptor_from_oneof_p(p, parent_handle, nsmap):
    if p.HasField('enum_string_metric_descriptor'):
        ret = dc.EnumStringMetricDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.enum_string_metric_descriptor, ret, indent='   (string_metric_descriptor_from_oneof_p)')
        return ret
    elif p.HasField('string_metric_descriptor'):
        ret = dc.StringMetricDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.string_metric_descriptor, ret, indent='   (string_metric_descriptor_from_oneof_p)')
        return ret
    else:
        raise TypeError(f'string_metric_descriptor_from_oneof_p cannot handle cls {p.__class__}')



def abstract_metric_descriptor_from_oneof_p(p, parent_handle, nsmap):
    if p.HasField('numeric_metric_descriptor'):
        ret = dc.NumericMetricDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.numeric_metric_descriptor, ret, indent='   (abstract_metric_descriptor_from_oneof_p)')
        return ret
    elif p.HasField('string_metric_descriptor_one_of'):
        ret = string_metric_descriptor_from_oneof_p(p.string_metric_descriptor_one_of, parent_handle, nsmap)
        return ret
    elif p.HasField('real_time_sample_array_metric_descriptor'):
        ret = dc.RealTimeSampleArrayMetricDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.real_time_sample_array_metric_descriptor, ret, indent='   (abstract_metric_descriptor_from_oneof_p)')
        return ret
    elif p.HasField('distribution_sample_array_metric_descriptor'):
        ret = dc.DistributionSampleArrayMetricDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.distribution_sample_array_metric_descriptor, ret,
                       indent='   (abstract_metric_descriptor_from_oneof_p)')
        return ret
    else:
        raise TypeError(f'alert_condition_descriptor_from_oneof_p cannot handle cls {p.__class__}')


def abstract_operation_descriptor_to_p(descr: dc.AbstractOperationDescriptorContainer,
                           p: [AbstractOperationDescriptorOneOfMsg, None]) -> AbstractOperationDescriptorOneOfMsg:
    if p is None:
        p = AbstractOperationDescriptorOneOfMsg()
    if isinstance(descr, dc.ActivateOperationDescriptorContainer):
        generic_to_p(descr, p.abstract_set_state_operation_descriptor_one_of.activate_operation_descriptor)
    elif isinstance(descr, dc.SetAlertStateOperationDescriptorContainer):
        generic_to_p(descr, p.abstract_set_state_operation_descriptor_one_of.set_alert_state_operation_descriptor)
    elif isinstance(descr, dc.SetComponentStateOperationDescriptorContainer):
        generic_to_p(descr,
                     p.abstract_set_state_operation_descriptor_one_of.set_component_state_operation_descriptor)
    elif isinstance(descr, dc.SetContextStateOperationDescriptorContainer):
        generic_to_p(descr,
                     p.abstract_set_state_operation_descriptor_one_of.set_context_state_operation_descriptor)
    elif isinstance(descr, dc.SetMetricStateOperationDescriptorContainer):
        generic_to_p(descr,
                     p.abstract_set_state_operation_descriptor_one_of.set_metric_state_operation_descriptor)
    elif isinstance(descr, dc.SetStringOperationDescriptorContainer):
        generic_to_p(descr, p.set_string_operation_descriptor)
    elif isinstance(descr, dc.SetValueOperationDescriptorContainer):
        generic_to_p(descr, p.set_value_operation_descriptor)
    else:
        raise TypeError(f'abstract_operation_descriptor_to_p cannot handle cls {descr.__class__}')
    return p


def abstract_operation_descriptor_from_oneof_p(p: AbstractOperationDescriptorOneOfMsg,
                                               parent_handle, nsmap) -> dc.AbstractOperationDescriptorContainer:
    p_src = p.abstract_set_state_operation_descriptor_one_of  # a shortcut for better readability
    if p_src.HasField('activate_operation_descriptor'):
        ret = dc.ActivateOperationDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p_src.activate_operation_descriptor, ret, indent='   (abstract_operation_descriptor_from_oneof_p)')
        return ret
    elif p_src.HasField('set_alert_state_operation_descriptor'):
        ret = dc.SetAlertStateOperationDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p_src.set_alert_state_operation_descriptor, ret, indent='   (abstract_operation_descriptor_from_oneof_p)')
        return ret
    elif p_src.HasField('set_component_state_operation_descriptor'):
        ret = dc.SetComponentStateOperationDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p_src.set_component_state_operation_descriptor, ret, indent='   (abstract_operation_descriptor_from_oneof_p)')
        return ret
    elif p_src.HasField('set_context_state_operation_descriptor'):
        ret = dc.SetContextStateOperationDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p_src.set_context_state_operation_descriptor, ret, indent='   (abstract_operation_descriptor_from_oneof_p)')
        return ret
    elif p_src.HasField('set_metric_state_operation_descriptor'):
        ret = dc.SetMetricStateOperationDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p_src.set_metric_state_operation_descriptor, ret, indent='   (abstract_operation_descriptor_from_oneof_p)')
        return ret
    elif p.HasField('set_string_operation_descriptor'):
        ret = dc.SetStringOperationDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.set_string_operation_descriptor, ret, indent='   (abstract_operation_descriptor_from_oneof_p)')
        return ret
    elif p.HasField('set_value_operation_descriptor'):
        ret = dc.SetValueOperationDescriptorContainer(nsmap, None, parent_handle)
        generic_from_p(p.set_value_operation_descriptor, ret, indent='   (abstract_operation_descriptor_from_oneof_p)')
        return ret
    else:
        raise TypeError(f'abstract_operation_descriptor_from_oneof_p cannot handle cls {p.__class__}')



_to_special_funcs = {
    dc.LimitAlertConditionDescriptorContainer: alert_condition_descriptor_to_oneof_p,
    dc.AlertConditionDescriptorContainer: alert_condition_descriptor_to_oneof_p,
    dc.NumericMetricDescriptorContainer: abstract_metric_descriptor_to_p,
    dc.StringMetricDescriptorContainer: abstract_metric_descriptor_to_p,
    dc.EnumStringMetricDescriptorContainer: abstract_metric_descriptor_to_p,
    dc.RealTimeSampleArrayMetricDescriptorContainer: abstract_metric_descriptor_to_p,
    dc.ActivateOperationDescriptorContainer: abstract_operation_descriptor_to_p,
    dc.SetStringOperationDescriptorContainer: abstract_operation_descriptor_to_p,
    dc.SetValueOperationDescriptorContainer: abstract_operation_descriptor_to_p,
    dc.SetContextStateOperationDescriptorContainer: abstract_operation_descriptor_to_p,
}

_from_special_funcs = {
    AlertConditionDescriptorOneOfMsg: alert_condition_descriptor_from_oneof_p,
    AbstractOperationDescriptorOneOfMsg: abstract_operation_descriptor_from_oneof_p,
    AbstractMetricDescriptorOneOfMsg: abstract_metric_descriptor_from_oneof_p,
}

def generic_descriptor_to_p(descr, p):
    special_handler = _to_special_funcs.get(descr.__class__)
    if special_handler:
        print(f'special handling cls={descr.__class__.__name__}, handler = {special_handler.__name__}')
        p = special_handler(descr, p)
        print(f'special handling cls={descr.__class__.__name__} done')
        return p
    if p is None:
        cls = _to_cls[descr.__class__]
        p = cls()
    generic_to_p(descr, p, indent='    ')
    return p


def generic_descriptor_from_p(p, parent_handle, nsmap):
    special_handler = _from_special_funcs.get(p.__class__)
    if special_handler:
        print(f'special handling cls={p.__class__.__name__}, handler = {special_handler.__name__}')
        ret = special_handler(p, parent_handle, nsmap)
        print(f'special handling cls={p.__class__.__name__} done')
        return ret
    cls = _from_cls[p.__class__]
    ret = cls(nsmap, None, parent_handle)
    generic_from_p(p, ret)
    return ret
