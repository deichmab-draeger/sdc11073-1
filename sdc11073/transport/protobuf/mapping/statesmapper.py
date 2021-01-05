from sdc11073.mdib import statecontainers as sc
from .pmtypesmapper import generic_from_p, generic_to_p
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


def generic_state_to_p(descr, p):
    if p is None:
        cls = _to_cls[descr.__class__]
        p = cls()
    generic_to_p(descr, p)
    return p


def generic_state_from_p(p, nsmap, descr):
    cls = _from_cls[p.__class__]
    ret = cls(nsmap, descr)
    generic_from_p(p, ret)
    return ret
