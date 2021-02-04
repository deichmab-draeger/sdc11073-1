import logging
import inspect
import traceback
from sdc11073.mdib import statecontainers as sc
from .pmtypesmapper import generic_from_p, generic_to_p
from .mapping_common import name_to_p, p_name_from_pm_name, find_populated_one_of, find_one_of_p_for_container
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
from org.somda.sdc.proto.model.biceps.abstractmetricstateoneof_pb2 import AbstractMetricStateOneOfMsg
from org.somda.sdc.proto.model.biceps.stringmetricstateoneof_pb2 import StringMetricStateOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractalertstateoneof_pb2 import AbstractAlertStateOneOfMsg
from org.somda.sdc.proto.model.biceps.alertconditionstateoneof_pb2 import AlertConditionStateOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractdevicecomponentstateoneof_pb2 import AbstractDeviceComponentStateOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractcomplexdevicecomponentstateoneof_pb2 import AbstractComplexDeviceComponentStateOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractoperationstateoneof_pb2 import AbstractOperationStateOneOfMsg
from org.somda.sdc.proto.model.biceps.abstractcontextstateoneof_pb2 import AbstractContextStateOneOfMsg
_logger = logging.getLogger('pysdc.grpc.map.state')


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


_one_of_states_fields = {
    AbstractStateOneOfMsg: ('abstract_alert_state_one_of', 'abstract_device_component_state_one_of',
                            'abstract_metric_state_one_of', 'abstract_multi_state_one_of',
                            'abstract_operation_state_one_of'),
    AbstractMetricStateOneOfMsg: ('numeric_metric_state', 'real_time_sample_array_metric_state',
                                  'string_metric_state_one_of', 'distribution_sample_array_metric_state'),
    StringMetricStateOneOfMsg: ('enum_string_metric_state', 'string_metric_state'),
    AbstractAlertStateOneOfMsg: ('alert_condition_state_one_of', 'alert_signal_state', 'alert_system_state'),
    AlertConditionStateOneOfMsg: ('alert_condition_state', 'limit_alert_condition_state'),
    AbstractDeviceComponentStateOneOfMsg: ('abstract_complex_device_component_state_one_of',
                                           'abstract_device_component_state', 'battery_state', 'channel_state',
                                           'clock_state', 'sco_state', 'system_context_state'),
    AbstractComplexDeviceComponentStateOneOfMsg: ('mds_state', 'vmd_state'),
    AbstractOperationStateOneOfMsg: ('activate_operation_state',
                                     'set_alert_state_operation_state', 'set_component_state_operation_state',
                                     'set_context_state_operation_state', 'set_metric_state_operation_state',
                                     'set_string_operation_state', 'set_value_operation_state'),
    AbstractContextStateOneOfMsg: ('ensemble_context_state', 'location_context_state', 'means_context_state',
                                   'operator_context_state', 'patient_context_state', 'workflow_context_state')
}


def find_one_of_state(p):
    return find_populated_one_of(p, _one_of_states_fields)


def generic_state_to_p(state, p):
    if p is None:
        cls = _to_cls[state.__class__]
        p = cls()
    p_field = find_one_of_p_for_container(state, p)
    generic_to_p(state, p_field)
    return p_field


def _p_walk(p, ret=None):
    if ret is None:
        ret = []
    one_of_fields = _one_of_states_fields.get(p.__class__)
    if one_of_fields  :
        for one_of_name in one_of_fields:
            if p.HasField(one_of_name):
                ret.extend(_p_walk(getattr(p, one_of_name)))
    else:
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
            ret.append((tmp_cls, p_current_entry_point, names))
    return ret


def p_get_value(p, pm_attr_name):
    for tmp_cls, p_current_entry_point, names in _p_walk(p):
        if pm_attr_name in names:
            p_name = p_name_from_pm_name(p_current_entry_point, tmp_cls, pm_attr_name)
            value = getattr(p_current_entry_point, p_name)
            return value


def _state_from_oneof_p(p, nsmap, descr):
    p_field = find_populated_one_of(p, _one_of_states_fields)
    cls = _from_cls[p_field.__class__]
    ret = cls(nsmap, descr)
    generic_from_p(p_field, ret)
    return ret


def generic_state_from_p(p, nsmap, descr):
    p_field = find_populated_one_of(p, _one_of_states_fields)
    cls = _from_cls[p_field.__class__]
    ret = cls(nsmap, descr)
    generic_from_p(p_field, ret)
    return ret
