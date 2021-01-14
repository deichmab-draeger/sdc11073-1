import inspect
import traceback
from sdc11073.mdib import statecontainers as sc
from .pmtypesmapper import generic_from_p, generic_to_p
from .mapping_common import name_to_p, attr_name_to_p, p_name_from_pm_name
from org.somda.sdc.proto.model.biceps.mdsstate_pb2 import MdsStateMsg
from org.somda.sdc.proto.model.biceps.setvalueoperationstate_pb2 import SetValueOperationStateMsg
from org.somda.sdc.proto.model.biceps.setstringoperationstate_pb2 import SetStringOperationStateMsg
from org.somda.sdc.proto.model.biceps.activateoperationstate_pb2 import ActivateOperationStateMsg
from org.somda.sdc.proto.model.biceps.setcontextstateoperationstate_pb2 import SetContextStateOperationStateMsg
from org.somda.sdc.proto.model.biceps.setmetricstateoperationstate_pb2 import SetMetricStateOperationStateMsg
from org.somda.sdc.proto.model.biceps.setcomponentstateoperationstate_pb2 import SetComponentStateOperationStateMsg
from org.somda.sdc.proto.model.biceps.setalertstateoperationstate_pb2 import SetAlertStateOperationStateMsg
from org.somda.sdc.proto.model.biceps.numericmetricstate_pb2 import NumericMetricStateMsg
from org.somda.sdc.proto.model.biceps.stringmetricstate_pb2 import StringMetricStateMsg
from org.somda.sdc.proto.model.biceps.enumstringmetricstate_pb2 import EnumStringMetricStateMsg
from org.somda.sdc.proto.model.biceps.realtimesamplearraymetricstate_pb2 import RealTimeSampleArrayMetricStateMsg
from org.somda.sdc.proto.model.biceps.distributionsamplearraymetricstate_pb2 import DistributionSampleArrayMetricStateMsg
from org.somda.sdc.proto.model.biceps.scostate_pb2 import ScoStateMsg
from org.somda.sdc.proto.model.biceps.vmdstate_pb2 import VmdStateMsg
from org.somda.sdc.proto.model.biceps.channelstate_pb2 import ChannelStateMsg
from org.somda.sdc.proto.model.biceps.clockstate_pb2 import ClockStateMsg
from org.somda.sdc.proto.model.biceps.systemcontextstate_pb2 import SystemContextStateMsg
from org.somda.sdc.proto.model.biceps.batterystate_pb2 import BatteryStateMsg
from org.somda.sdc.proto.model.biceps.alertsystemstate_pb2 import AlertSystemStateMsg
from org.somda.sdc.proto.model.biceps.alertsignalstate_pb2 import AlertSignalStateMsg
from org.somda.sdc.proto.model.biceps.alertconditionstate_pb2 import AlertConditionStateMsg
from org.somda.sdc.proto.model.biceps.limitalertconditionstate_pb2 import LimitAlertConditionStateMsg
from org.somda.sdc.proto.model.biceps.locationcontextstate_pb2 import LocationContextStateMsg
from org.somda.sdc.proto.model.biceps.patientcontextstate_pb2 import PatientContextStateMsg
from org.somda.sdc.proto.model.biceps.abstractstateoneof_pb2 import AbstractStateOneOfMsg


_to_cls= {}
_to_cls[sc.SetValueOperationStateContainer] = SetValueOperationStateMsg
_to_cls[sc.MdsStateContainer] = MdsStateMsg
_to_cls[sc.SetStringOperationStateContainer] = SetStringOperationStateMsg
_to_cls[sc.ActivateOperationStateContainer] = ActivateOperationStateMsg
_to_cls[sc.SetContextStateOperationStateContainer] = SetContextStateOperationStateMsg
_to_cls[sc.SetMetricStateOperationStateContainer] = SetMetricStateOperationStateMsg
_to_cls[sc.SetComponentStateOperationStateContainer] = SetComponentStateOperationStateMsg
_to_cls[sc.SetAlertStateOperationStateContainer] = SetAlertStateOperationStateMsg
_to_cls[sc.NumericMetricStateContainer] = NumericMetricStateMsg
_to_cls[sc.StringMetricStateContainer] = StringMetricStateMsg
_to_cls[sc.EnumStringMetricStateContainer] = EnumStringMetricStateMsg
_to_cls[sc.RealTimeSampleArrayMetricStateContainer] = RealTimeSampleArrayMetricStateMsg
_to_cls[sc.DistributionSampleArrayMetricStateContainer] = DistributionSampleArrayMetricStateMsg
_to_cls[sc.ScoStateContainer] = ScoStateMsg
_to_cls[sc.VmdStateContainer] = VmdStateMsg
_to_cls[sc.ChannelStateContainer] = ChannelStateMsg
_to_cls[sc.ClockStateContainer] = ClockStateMsg
_to_cls[sc.SystemContextStateContainer] = SystemContextStateMsg
_to_cls[sc.BatteryStateContainer] = BatteryStateMsg
_to_cls[sc.AlertSystemStateContainer] = AlertSystemStateMsg
_to_cls[sc.AlertSignalStateContainer] = AlertSignalStateMsg
_to_cls[sc.AlertConditionStateContainer] = AlertConditionStateMsg
_to_cls[sc.LimitAlertConditionStateContainer] = LimitAlertConditionStateMsg
_to_cls[sc.LocationContextStateContainer] = LocationContextStateMsg
_to_cls[sc.PatientContextStateContainer] = PatientContextStateMsg

# invert for other direction lookup
_from_cls = dict((v, k) for (k, v) in _to_cls.items())

_abstract_state_to_oneof_p_lookup = {
sc.NumericMetricStateContainer: ('abstract_metric_state_one_of', 'numeric_metric_state'),
sc.StringMetricStateContainer: ('abstract_metric_state_one_of', 'string_metric_state_one_of','string_metric_state'),
sc.EnumStringMetricStateContainer: ('abstract_metric_state_one_of', 'string_metric_state_one_of','enum_string_metric_state'),
sc.RealTimeSampleArrayMetricStateContainer: ('abstract_metric_state_one_of', 'real_time_sample_array_metric_state'),
sc.VmdStateContainer: ('abstract_device_component_state_one_of', 'abstract_complex_device_component_state_one_of', 'vmd_state'),
sc.MdsStateContainer: ('abstract_device_component_state_one_of', 'abstract_complex_device_component_state_one_of', 'mds_state'),
sc.ChannelStateContainer: ('abstract_device_component_state_one_of', 'channel_state'),
sc.BatteryStateContainer: ('abstract_device_component_state_one_of', 'battery_state'),
sc.ClockStateContainer: ('abstract_device_component_state_one_of', 'clock_state'),
sc.ScoStateContainer: ('abstract_device_component_state_one_of', 'sco_state'),
sc.SystemContextStateContainer: ('abstract_device_component_state_one_of', 'system_context_state'),
sc.ScoStateContainer: ('abstract_device_component_state_one_of', 'sco_state'),
sc.AlertSystemStateContainer: ('abstract_alert_state_one_of', 'alert_system_state'),
sc.AlertSignalStateContainer: ('abstract_alert_state_one_of', 'alert_signal_state'),
sc.AlertConditionStateContainer: ('abstract_alert_state_one_of', 'alert_condition_state_one_of', 'alert_condition_state'),
sc.LimitAlertConditionStateContainer: ('abstract_alert_state_one_of', 'alert_condition_state_one_of', 'limit_alert_condition_state'),
sc.ActivateOperationStateContainer: ('abstract_operation_state_one_of', 'activate_operation_state'),
sc.SetAlertStateOperationStateContainer: ('abstract_operation_state_one_of', 'set_alert_state_operation_state'),
sc.SetComponentStateOperationStateContainer: ('abstract_operation_state_one_of', 'set_component_state_operation_state'),
sc.SetContextStateOperationStateContainer: ('abstract_operation_state_one_of', 'set_context_state_operation_state'),
sc.SetMetricStateOperationStateContainer: ('abstract_operation_state_one_of', 'set_metric_state_operation_state'),
sc.SetStringOperationStateContainer: ('abstract_operation_state_one_of', 'set_string_operation_state'),
sc.SetValueOperationStateContainer: ('abstract_operation_state_one_of', 'set_value_operation_state'),
}

def abstract_state_to_oneof_p(state, p):
    try:
        member_names = _abstract_state_to_oneof_p_lookup[state.__class__]
    except:
        print(traceback.format_exc())
        print('bah')
    tmp = p
    for n in member_names:
        tmp = getattr(tmp, n)
    generic_to_p(state, tmp)


_to_special_funcs = {AbstractStateOneOfMsg: abstract_state_to_oneof_p
                     }


def generic_state_to_p(state, p):
    if p is None:
        cls = _to_cls[state.__class__]
        p = cls()
    special_handler = _to_special_funcs.get(state.__class__) or _to_special_funcs.get(p.__class__)
    if special_handler:
        special_handler(state, p)
    else:
        generic_to_p(state, p)
    return p


def find_abstract_state_one_of(p):
    for path_elements in _abstract_state_to_oneof_p_lookup.values():
        tmp = p
        for path_element in path_elements[:-1]:
            tmp = getattr(tmp, path_element)
        if tmp.HasField(path_elements[-1]):
            return getattr(tmp, path_elements[-1])
    raise ValueError(f'found no data in {p.__class__.__name__}')


def p_walk(p):
    # does not work for "one_of" instances
    pm_cls = _from_cls[p.__class__]
    classes = inspect.getmro(pm_cls)
    p_current_entry_point = None
    for tmp_cls in classes:
        if tmp_cls.__name__.startswith('_'):
            # convention: if a class name starts with underscore, it is not part of biceps inheritance hierarchy
            continue
        try:
            names = tmp_cls._props  # pylint: disable=protected-access
        except:
            continue
        # determine p_current_entry_point
        if p_current_entry_point is None:
            p_current_entry_point = p
        else:
            # find parent class members entry point
            p_name = name_to_p(tmp_cls.__name__)
            p_current_entry_point = getattr(p_current_entry_point, p_name)
        yield(tmp_cls, p_current_entry_point, names)


def p_get_value(p, pm_attr_name):
    for tmp_cls, p_current_entry_point, names in p_walk(p):
        if pm_attr_name in names:
            p_name = p_name_from_pm_name(p_current_entry_point, tmp_cls, pm_attr_name)
            value = getattr(p_current_entry_point, p_name)
            return value


def generic_state_from_p(p, nsmap, descr):
    cls = _from_cls[p.__class__]
    ret = cls(nsmap, descr)
    generic_from_p(p, ret)
    return ret