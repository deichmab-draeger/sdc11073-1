import inspect
import logging
from typing import List
from lxml import etree as etree_
from sdc11073.pmtypes import LocalizedText, CodedValue, T_Translation, Annotation
from sdc11073.pmtypes import T_MetricQuality, NumericMetricValue, StringMetricValue, SampleArrayValue
from sdc11073.pmtypes import ApplyAnnotation, CauseInfo, RemedyInfo, ActivateOperationDescriptorArgument
from sdc11073.pmtypes import SystemSignalActivation, ProductionSpecification, InstanceIdentifier, OperatingJurisdiction
from sdc11073.pmtypes import Range, Measurement, PersonParticipation, PhysicalConnectorInfo
from sdc11073.pmtypes import AllowedValue, BaseDemographics, PatientDemographicsCoreData
from sdc11073.pmtypes import NeonatalPatientDemographicsCoreData, PersonReference, LocationDetail, LocationReference
from sdc11073.pmtypes import ReferenceRange, RelatedMeasurement, ClinicalInfo, ImagingProcedure
from sdc11073.pmtypes import OrderDetail, PerformedOrderDetail, WorkflowDetail, AbstractMetricDescriptorRelation, T_Udi
from sdc11073.pmtypes import RequestedOrderDetail, MetaData, OperationGroup
from sdc11073.dataconverters import DecimalConverter
from sdc11073.mdib.containerproperties import DecimalAttributeProperty, TimestampAttributeProperty, CurrentTimestampAttributeProperty
from sdc11073.mdib.containerproperties import IntegerAttributeProperty, DurationAttributeProperty, EnumAttributeProperty
from sdc11073.mdib.containerproperties import NodeAttributeProperty, NodeAttributeListProperty, SubElementListProperty
from sdc11073.mdib.containerproperties import HandleRefListAttributeProperty,  OperationRefListAttributeProperty, AlertConditionRefListAttributeProperty
from sdc11073.mdib.containerproperties import NodeTextProperty, NodeEnumTextProperty, NodeTextQNameProperty, SubElementTextListProperty
from org.somda.sdc.proto.model.biceps.localizedtext_pb2 import LocalizedTextMsg
from org.somda.sdc.proto.model.biceps.codedvalue_pb2 import CodedValueMsg
from org.somda.sdc.proto.model.biceps.instanceidentifier_pb2 import InstanceIdentifierMsg
from org.somda.sdc.proto.model.biceps.operatingjurisdiction_pb2 import OperatingJurisdictionMsg
from org.somda.sdc.proto.model.biceps.instanceidentifieroneof_pb2 import InstanceIdentifierOneOfMsg
from org.somda.sdc.proto.model.biceps.range_pb2 import RangeMsg
from org.somda.sdc.proto.model.biceps.measurement_pb2 import MeasurementMsg
from org.somda.sdc.proto.model.biceps.enumstringmetricdescriptor_pb2 import EnumStringMetricDescriptorMsg
from org.somda.sdc.proto.model.biceps.abstractmetricvalue_pb2 import AbstractMetricValueMsg
from org.somda.sdc.proto.model.biceps.numericmetricvalue_pb2 import NumericMetricValueMsg
from org.somda.sdc.proto.model.biceps.stringmetricvalue_pb2 import StringMetricValueMsg
from org.somda.sdc.proto.model.biceps.samplearrayvalue_pb2 import SampleArrayValueMsg
from org.somda.sdc.proto.model.biceps.realtimevaluetype_pb2 import RealTimeValueTypeMsg
from org.somda.sdc.proto.model.biceps.causeinfo_pb2 import CauseInfoMsg
from org.somda.sdc.proto.model.biceps.remedyinfo_pb2 import RemedyInfoMsg
from org.somda.sdc.proto.model.biceps.activateoperationdescriptor_pb2 import ActivateOperationDescriptorMsg
from org.somda.sdc.proto.model.biceps.physicalconnectorinfo_pb2 import PhysicalConnectorInfoMsg
from org.somda.sdc.proto.model.biceps.abstractdevicecomponentdescriptor_pb2 import AbstractDeviceComponentDescriptorMsg
from org.somda.sdc.proto.model.biceps.systemsignalactivation_pb2 import SystemSignalActivationMsg
from org.somda.sdc.proto.model.biceps.basedemographics_pb2 import BaseDemographicsMsg, BaseDemographicsOneOfMsg
from org.somda.sdc.proto.model.biceps.basedemographics_pb2 import PatientDemographicsCoreDataMsg, PatientDemographicsCoreDataOneOfMsg
from org.somda.sdc.proto.model.biceps.basedemographics_pb2 import NeonatalPatientDemographicsCoreDataMsg
from org.somda.sdc.proto.model.biceps.basedemographics_pb2 import PersonReferenceMsg, PersonReferenceOneOfMsg, PersonParticipationMsg
from org.somda.sdc.proto.model.biceps.locationdetail_pb2 import LocationDetailMsg
from org.somda.sdc.proto.model.biceps.locationreference_pb2 import LocationReferenceMsg
from org.somda.sdc.proto.model.biceps.clinicalinfo_pb2 import ClinicalInfoMsg
from org.somda.sdc.proto.model.biceps.imagingprocedure_pb2 import ImagingProcedureMsg
from org.somda.sdc.proto.model.biceps.orderdetail_pb2 import OrderDetailMsg
from org.somda.sdc.proto.model.biceps.workflowcontextstate_pb2 import WorkflowContextStateMsg
from org.somda.sdc.proto.model.biceps.abstractmetricdescriptor_pb2 import AbstractMetricDescriptorMsg
from org.somda.sdc.proto.model.biceps.mdsdescriptor_pb2 import MdsDescriptorMsg
from org.somda.sdc.proto.model.biceps.setstringoperationstate_pb2 import SetStringOperationStateMsg
from org.somda.sdc.proto.model.biceps.scostate_pb2 import ScoStateMsg

from google.protobuf.wrappers_pb2 import StringValue
from google.protobuf.duration_pb2 import Duration
from decimal import Decimal
from .mapping_common import name_to_p, attr_name_to_p, p_name_from_pm_name
_logger = logging.getLogger('pysdc.grpc.pmtypes_mapper')

#  str <->StringValue
def string_value_to_p(s: (str, None), p: (StringValue, None)) -> StringValue:
    """modify protobuf StringValue
    if p is None, a new StringValue is returned; otherwise the parameter is modified
    """
    if p is None:
        p = StringValue()
    if s is not None:
        p.value = s
        return p


def string_value_from_p(p, attr_name) -> (str, None):
    if p.HasField(attr_name):
       opt = getattr(p, attr_name)
       return opt.value


def _enum_name_to_p(name):
    # insert an underscore when changing from an lowercase to an uppercase char
    tmp = []
    tmp.append(name[0])
    for c in name[1:]:
        if c.isupper() and tmp[-1].islower():
            tmp.append('_')
        tmp.append(c)
    return ''.join(tmp).upper()


def enum_attr_to_p(s: str, p) -> None:
    """modify protobuf StringValue inline """
    if s is not None:
        s = _enum_name_to_p(s) # protobuf is always upper case
        e = p.EnumType.Value(s)
        p.enum_value = e


def enum_attr_from_p(p_src, p_attr_name, dest, dest_attr_name):
    """
    returns the converted value or None
    """
    p = getattr(p_src, p_attr_name)
    s = p.EnumType.Name(p.enum_value)
    s = s.replace('_', '') # simplified reverse logic of name mapping: remove underscores
    prop = getattr(dest.__class__, dest_attr_name)
    enum_cls = prop.enum_cls
    for name, member in enum_cls.__members__.items():
        if member.value.upper() == s:
            return member
    raise ValueError(f'unknown enum "{s}" for {dest_attr_name}, type={enum_cls.__name__}')


def duration_to_p(f: [float, Decimal], p: Duration) -> None:
    """modify protobuf Duration value inline """
    if f is None:
        return
    p.seconds = int(f)
    p.nanos = int((f - int(f))*1e9)


def duration_from_p(p: Duration) -> float:
    """read protobuf Duration """
    ret = float(p.seconds) + float(p.nanos)/1e9
    return ret


def t_translation_from_p(p: CodedValueMsg.TranslationMsg) -> T_Translation:
    code = p.a_code
    coding_system = None if not p.HasField('a_coding_system') else p.a_coding_system.value
    version = None if not p.HasField('a_coding_system_version') else p.a_coding_system_version.value
    ret = T_Translation(code, coding_system, version)
    return ret


# CodedValue <->CodedValueMsg
def codedvalue_from_p(p: CodedValueMsg) -> CodedValue:
    code = p.a_code
    coding_system = string_value_from_p(p, 'a_coding_system')
    version = string_value_from_p(p, 'a_coding_system_version')
    ret = CodedValue(code, coding_system, version)  # qualified constructor => implicit call of mkCoding
    for elem in p.coding_system_name:
        ret.CodingSystemName.append(generic_from_p(elem))
    for elem in p.concept_description:
        ret.ConceptDescription.append(generic_from_p(elem))
    ret.SymbolicCodeName = string_value_from_p(p, 'a_symbolic_code_name')
    for elem in p.translation:
        ret.Translation.append(generic_from_p(elem))
    return ret


def annotation_from_p(p: AbstractMetricValueMsg.AnnotationMsg) -> Annotation:
    code = p.type.a_code
    coding_system = string_value_from_p(p.type, 'a_coding_system')
    coding_system_version = string_value_from_p(p.type, 'a_coding_system_version')
    c = CodedValue(code, coding_system, coding_system_version)  # qualified constructor=>implicit call of mkCoding
    return Annotation(c)


# [InstanceIdentifier, OperatingJurisdiction] <-> InstanceIdentifierOneOfMsg
def instance_identifier_to_oneof_p(inst:[InstanceIdentifier, OperatingJurisdiction],
                                   p:InstanceIdentifierOneOfMsg) -> InstanceIdentifierMsg:
    if p is None:
        p = InstanceIdentifierOneOfMsg()
    if isinstance(inst, OperatingJurisdiction):
        generic_to_p(inst, p.operating_jurisdiction, '   (instance_identifier_to_oneof_p)')
    elif isinstance(inst, InstanceIdentifier):
        generic_to_p(inst, p.instance_identifier, '   (instance_identifier_to_oneof_p)')
    else:
        raise TypeError(f'instance_identifier_to_oneof_p cannot handle cls {inst.__class__}')
    return p


def instance_identifier_from_oneof_p(p:InstanceIdentifierOneOfMsg) -> [InstanceIdentifier, OperatingJurisdiction]:
    if p.HasField('instance_identifier'):
        ret = InstanceIdentifier(None)
        generic_from_p(p.instance_identifier, ret, indent='   (instance_identifier_from_oneof_p)')
        return ret
    else:
        ret = OperatingJurisdiction(None)
        generic_from_p(p.operating_jurisdiction, ret, indent='   (instance_identifier_from_oneof_p)')
        return ret


# SampleArrayValue <-> RealTimeValueTypeMsg
def _realtime_array_to_p(samples: List[str], p: RealTimeValueTypeMsg) -> None:
    for s in samples:
        p.real_time_value_type.append(DecimalConverter.toXML(s))


def _realtime_array_from_p(p: RealTimeValueTypeMsg) -> Decimal:
    return [DecimalConverter.toPy(sc) for sc in p.real_time_value_type]


# BaseDemographics <-> BaseDemographicsMsg
def _base_demographics_to_p(bd: BaseDemographics, p:BaseDemographicsMsg) -> BaseDemographicsMsg:
    if p is None:
        p = BaseDemographicsMsg()
    string_value_to_p(bd.Givenname, p.givenname)
    string_value_to_p(bd.Familyname, p.familyname)
    string_value_to_p(bd.Birthname, p.birthname)
    p.middlename.extend(bd.Middlename)
    string_value_to_p(bd.Title, p.title)
    return p


def _base_demographics_from_p(p: BaseDemographicsMsg) -> BaseDemographics:
    ret = BaseDemographics()
    ret.Givenname = string_value_from_p(p, 'givenname')
    ret.Familyname = string_value_from_p(p, 'familyname')
    ret.Birthname = string_value_from_p(p, 'birthname')
    ret.Middlename.extend(p.middlename)
    ret.Title = string_value_from_p(p, 'title')
    return ret


# BaseDemographics <-> BaseDemographicsOneOfMsg
def base_demographics_to_oneof_p(bd: BaseDemographics, p:BaseDemographicsOneOfMsg) -> BaseDemographicsOneOfMsg:
    # ToDo: PatientDemographicsCoreData is not modeled!
    if p is None:
        if isinstance(bd, PatientDemographicsCoreData):
            p = PatientDemographicsCoreDataOneOfMsg()
        else:
            p = BaseDemographicsOneOfMsg()
    if isinstance(bd, NeonatalPatientDemographicsCoreData):
        generic_to_p(bd, p.neonatal_patient_demographics_core_data, '   (base_demographics_to_oneof_p)')
    elif isinstance(bd, PatientDemographicsCoreData):
        generic_to_p(bd, p.patient_demographics_core_data, '   (base_demographics_to_oneof_p)')
    else:
        # generic_to_p does not work, Middlename (list of strings <-> list of strings ) cannot be handled safely
        # return generic_to_p(bd, p.base_demographics, ' (base_demographics_to_oneof_p) ')
        _base_demographics_to_p(bd, p.base_demographics)
    return p

def base_demographics_from_oneof_p(p: BaseDemographicsOneOfMsg) -> BaseDemographics:
    return _base_demographics_from_p(p.base_demographics)

def patient_demographics_core_data_from_oneof_p(p: PatientDemographicsCoreDataOneOfMsg) -> PatientDemographicsCoreData:
    if p.HasField('neonatal_patient_demographics_core_data'):
        return generic_from_p(p.neonatal_patient_demographics_core_data, None, '  (patient_demographics_core_data_from_oneof_p) ')
    elif p.HasField('patient_demographics_core_data'):
        return generic_from_p(p.patient_demographics_core_data, None, '  (patient_demographics_core_data_from_oneof_p) ')
    else:
        raise TypeError(f'cannot convert {p.__class__.__name__}')


# PersonReference <-> PersonReferenceOneOfMsg
def person_reference_to_oneof_p(pr: PersonReference, p:PersonReferenceOneOfMsg) -> PersonReferenceOneOfMsg:
    if p is None:
        p = PersonReferenceOneOfMsg()
    if isinstance(pr, PersonParticipation):
        generic_to_p(pr, p.person_participation, '  (person_reference_to_oneof_p) ')
    elif isinstance(pr, PersonReference):
        generic_to_p(pr, p.person_reference, '  (person_reference_to_oneof_p) ')
    else:
        raise TypeError(f'cannot convert {pr.__class__.__name__}')
    return p

def person_reference_from_oneof_p(p: PersonReferenceOneOfMsg) -> PersonReference:
    if p.HasField('person_participation'):
        return generic_from_p(p.person_participation, None, '  (person_reference_from_oneof_p) ')
    else:
        return generic_from_p(p.person_reference, None, '  (person_reference_from_oneof_p) ')

def allowed_values_to_p(aw: List[str], p: SetStringOperationStateMsg.AllowedValuesMsg):
    p.value.extend(aw)


def allowed_values_from_p(p: SetStringOperationStateMsg.AllowedValuesMsg):
    return [v for v in p.value]

_to_cls= {}
_to_cls[AbstractMetricDescriptorRelation] = AbstractMetricDescriptorMsg.RelationMsg
_to_cls[PerformedOrderDetail] = WorkflowContextStateMsg.WorkflowDetailMsg.PerformedOrderDetailMsg
_to_cls[RequestedOrderDetail] = WorkflowContextStateMsg.WorkflowDetailMsg.RequestedOrderDetailMsg
_to_cls[ClinicalInfo] = ClinicalInfoMsg
_to_cls[LocalizedText] = LocalizedTextMsg
_to_cls[PersonParticipation] = PersonParticipationMsg
_to_cls[ImagingProcedure] = ImagingProcedureMsg
_to_cls[CodedValue] = CodedValueMsg
_to_cls[WorkflowDetail] = WorkflowContextStateMsg.WorkflowDetailMsg
_to_cls[LocationReference] = LocationReferenceMsg
_to_cls[LocationDetail] = LocationDetailMsg
_to_cls[PersonReference] = PersonReferenceMsg
_to_cls[InstanceIdentifier] = InstanceIdentifierMsg
_to_cls[OperatingJurisdiction] = OperatingJurisdictionMsg
_to_cls[Range] = RangeMsg
_to_cls[T_MetricQuality] = AbstractMetricValueMsg.MetricQualityMsg
_to_cls[NumericMetricValue] = NumericMetricValueMsg
_to_cls[StringMetricValue] = StringMetricValueMsg
_to_cls[SampleArrayValue] = SampleArrayValueMsg
_to_cls[Annotation] = AbstractMetricValueMsg.AnnotationMsg
_to_cls[ApplyAnnotation] = SampleArrayValueMsg.ApplyAnnotationMsg
_to_cls[CauseInfo] = CauseInfoMsg
_to_cls[RemedyInfo] = RemedyInfoMsg
_to_cls[ActivateOperationDescriptorArgument] = ActivateOperationDescriptorMsg.ArgumentMsg
_to_cls[PhysicalConnectorInfo] = PhysicalConnectorInfoMsg
_to_cls[SystemSignalActivation] = SystemSignalActivationMsg
_to_cls[ProductionSpecification] = AbstractDeviceComponentDescriptorMsg.ProductionSpecificationMsg
_to_cls[BaseDemographics] = BaseDemographicsMsg
_to_cls[PatientDemographicsCoreData] = PatientDemographicsCoreDataMsg
_to_cls[ReferenceRange] = ClinicalInfoMsg.RelatedMeasurementMsg.ReferenceRangeMsg
_to_cls[RelatedMeasurement] = ClinicalInfoMsg.RelatedMeasurementMsg
_to_cls[OrderDetail] = OrderDetailMsg
_to_cls[T_Udi] = MdsDescriptorMsg.MetaDataMsg.UdiMsg
_to_cls[AllowedValue] = EnumStringMetricDescriptorMsg.AllowedValueMsg
_to_cls[T_Translation] = CodedValueMsg.TranslationMsg
_to_cls[Measurement] = MeasurementMsg
_to_cls[MetaData] = MdsDescriptorMsg.MetaDataMsg
_to_cls[OperationGroup] = ScoStateMsg.OperationGroupMsg

# invert for other direction lookup
_from_cls = dict((v, k) for (k, v) in _to_cls.items())

_to_special_funcs = {InstanceIdentifier: instance_identifier_to_oneof_p,
                     PersonReference: person_reference_to_oneof_p,
                     BaseDemographics: base_demographics_to_oneof_p,
                     PatientDemographicsCoreData: base_demographics_to_oneof_p,
                     NeonatalPatientDemographicsCoreData: base_demographics_to_oneof_p,
                     RealTimeValueTypeMsg: _realtime_array_to_p,
                     SetStringOperationStateMsg.AllowedValuesMsg: allowed_values_to_p
                     }


_from_special_funcs = {InstanceIdentifierOneOfMsg: instance_identifier_from_oneof_p,
                       CodedValueMsg: codedvalue_from_p,
                       PersonReferenceOneOfMsg: person_reference_from_oneof_p,
                       BaseDemographicsOneOfMsg: base_demographics_from_oneof_p,
                       PatientDemographicsCoreDataOneOfMsg: patient_demographics_core_data_from_oneof_p,
                       AbstractMetricValueMsg.AnnotationMsg: annotation_from_p,
                       RealTimeValueTypeMsg: _realtime_array_from_p,
                       CodedValueMsg.TranslationMsg: t_translation_from_p,
                       SetStringOperationStateMsg.AllowedValuesMsg: allowed_values_from_p
                       }


def generic_to_p(pm_src, p, indent='', to_special_funcs=None):
    if p is None:
        # is there a special handler for whole class?
        special_handler = None
        if to_special_funcs:
            special_handler = to_special_funcs.get(pm_src.__class__)
        if special_handler is None:
            special_handler = _to_special_funcs.get(pm_src.__class__)
        if special_handler:
            print(f'{indent}special handling cls={pm_src.__class__.__name__}, handler = {special_handler.__name__}')
            p = special_handler(pm_src, None)
            print(f'{indent}special handling cls={pm_src.__class__.__name__} done')
            return p
        else:
            p = _to_cls[pm_src.__class__]()
    p_current_entry_point = None
    classes = inspect.getmro(pm_src.__class__)
    for tmp_cls in classes:
        if tmp_cls.__name__.startswith('_'):
            # convention: if a class name starts with underscore, it is not part of biceps inheritance hierarchy
            continue
        try:
            names = tmp_cls._props  # pylint: disable=protected-access
        except AttributeError:
            continue
        print(f'{indent}handling class {tmp_cls.__name__}')
        # determine p_current_entry_point
        if p_current_entry_point is None:
            p_current_entry_point = p
        else:
            # find parent class members entry point
            p_name = name_to_p(tmp_cls.__name__)
            p_current_entry_point = getattr(p_current_entry_point, p_name)
        # iterate over all properties
        for name in names:
            cp_type = getattr(pm_src.__class__, name) # containerproperties type
            print(f'{indent}handling {tmp_cls.__name__}.{name}, cls={cp_type.__class__.__name__}')
            # special handler for property?
            special_handler = _to_special_funcs.get(cp_type.__class__)  # e.g. EnumAttributeProperty
            if special_handler:
                print(f'{indent}special handling handling {pm_src.__class__.__name__} = {special_handler.__name__}')
                special_handler(pm_src, p_current_entry_point)
                print(f'{indent}special handling handling {pm_src.__class__.__name__} done')
                continue
            value = getattr(pm_src, name)
            if value in (None, []):
                continue
            # determine member name in p:
            if name == 'text' and isinstance(p, LocalizedTextMsg):
                p_name = 'string'
            elif name == 'ext_Extension':
                p_name = 'element1'
            else:
                if isinstance(cp_type, (NodeAttributeProperty, NodeAttributeListProperty)):
                    p_name = attr_name_to_p(name)
                else:
                    p_name = name_to_p(name)
            # convert
            p_dest = getattr(p_current_entry_point, p_name)
            special_handler_dest = _to_special_funcs.get(p_dest.__class__)
            special_handler_value = _to_special_funcs.get(value.__class__)
            if isinstance(cp_type, EnumAttributeProperty):
                enum_attr_to_p(value, p_dest)
            elif isinstance(cp_type, NodeEnumTextProperty):
                enum_attr_to_p(value, p_dest)
            elif hasattr(p_dest, 'enum_value'):
                raise RuntimeError('bla')
            elif isinstance(cp_type, DurationAttributeProperty):
                duration_to_p(value, p_dest)
            elif isinstance(cp_type, NodeAttributeProperty):
                # type conversion if needed
                if isinstance(cp_type, DecimalAttributeProperty):
                    value = DecimalConverter.toXML(value)
                elif isinstance(cp_type, (TimestampAttributeProperty, CurrentTimestampAttributeProperty)):
                    value = int(value) # float is not supported
                if cp_type.isOptional:
                    p_dest.value = value
                else:
                    setattr(p_current_entry_point, p_name, value)
            elif special_handler_dest is not None:
                print(f'{indent}special p_dest handling {p_dest.__class__.__name__} = {special_handler_dest.__name__}')
                special_handler_dest(value, p_dest)
                print(f'{indent}special p_dest handling {p_dest.__class__.__name__}, done')
            elif special_handler_value is not None:
                print(f'{indent}special value handling {value.__class__.__name__} = {special_handler_value.__name__}')
                special_handler_value(value, p_dest)
                print(f'{indent}special value handling {p_dest.__class__.__name__}, done')
            elif isinstance(cp_type, OperationRefListAttributeProperty):
                pm_list = getattr(pm_src, name)
                if pm_list is not None:
                    p_dest.operation_ref.extend(pm_list)
            elif isinstance(cp_type, AlertConditionRefListAttributeProperty):
                pm_list = getattr(pm_src, name)
                if pm_list is not None:
                    p_dest.alert_condition_reference.extend(pm_list)
            elif isinstance(cp_type, NodeAttributeListProperty):
                # This is always a list of handles ( values in 'entry_ref')
                pm_list = getattr(pm_src, name)
                if pm_list is not None:
                    p_dest.entry_ref.extend(pm_list)

            elif isinstance(cp_type, NodeTextProperty):
                if cp_type.isOptional:
                    p_dest.value = value
                else:
                    setattr(p_current_entry_point, p_name, value)
            elif isinstance(cp_type, NodeTextQNameProperty):
                # ToDo: convert external namespace to normalized internal one
                if cp_type.isOptional:
                    raise TypeError(f'no handler for optional {p_dest.__class__.__name__} ')
                else:
                    setattr(p_current_entry_point, p_name, str(value))
            elif isinstance(cp_type, SubElementListProperty):
                for elem in value:
                    print(f'{indent}recursive list elem generic_to_p({elem.__class__.__name__}, None)')
                    p_value = generic_to_p(elem, None, indent+'    ')
                    print(f'{indent}recursive list elem generic_to_p ({elem.__class__.__name__}) done')
                    p_dest.append(p_value)
            elif isinstance(cp_type, SubElementTextListProperty):
                p_dest.extend(value)
            else:
                print (f'{indent}recursive generic_to_p({value.__class__.__name__}, {p_dest.__class__.__name__})')
                generic_to_p(value, p_dest, indent+'    ')
                print(f'{indent}recursive generic_to_p done')
    return p


def generic_from_p(p, pm_dest=None, indent=''):
    if pm_dest is None:
        pm_factory = _from_special_funcs.get(p.__class__)
        if pm_factory:
            print(f'{indent}special factory for class {p.__class__.__name__} = {pm_factory.__name__}')
            return pm_factory(p)
        print(f'{indent}generic instantiate class {p.__class__.__name__}')
        # use inspect to determine number of parameters for constructor.
        # then call constructor with all parameters = None
        pm_cls = _from_cls[p.__class__]
        sig = inspect.signature(pm_cls.__init__)
        args = [None] * (len(sig.parameters)-1)
        pm_dest = pm_cls(*args)
    classes = inspect.getmro(pm_dest.__class__)
    print(f'{indent}inheritance = {[c.__name__ for c in classes]}')
    p_current_entry_point = None
    for tmp_cls in classes:
        if tmp_cls.__name__.startswith('_'):
            # convention: if a class name starts with underscore, it is not part of biceps inheritance hierarchy
            continue
        try:
            names = tmp_cls._props  # pylint: disable=protected-access
        except:
            continue
        print(f'{indent}handling tmp_cls {tmp_cls.__name__}')
        # determine p_current_entry_point
        if p_current_entry_point is None:
            p_current_entry_point = p
        else:
            # find parent class members entry point
            p_name = name_to_p(tmp_cls.__name__)
            p_current_entry_point = getattr(p_current_entry_point, p_name)
        # special handler for whole dest class?
        special_handler = _from_special_funcs.get(tmp_cls)
        if special_handler:
            print(f'{indent}special handling tmp_cls {tmp_cls.__class__.__name__} = {special_handler.__name__}')
            special_handler(pm_dest, p_current_entry_point)
            print(f'{indent}special handling handling {tmp_cls.__class__.__name__} done')
            break

        # iterate over all properties
        for name in names:
            print(f'{indent}handling {tmp_cls.__name__}.{name}')
            dest_type = getattr(pm_dest.__class__, name)
            # # determine member name in p:
            p_name = p_name_from_pm_name(p, pm_dest.__class__, name)
            p_src = getattr(p_current_entry_point, p_name)

            # special handler for property?
            special_handler_src_cls = None

            try:
                # assume this is an optional value, check availability
                isOptional = True
                if not p_current_entry_point.HasField(p_name):
                    continue
                else:
                    special_handler_src_cls = _from_special_funcs.get(p_src.__class__)
            except ValueError:
                isOptional = False

            if special_handler_src_cls:
                print(f'{indent}special handling src_cls {p_src.__class__.__name__} = {special_handler_src_cls.__name__}')
                value = special_handler_src_cls(p_src)
                setattr(pm_dest, name, value)
                print(f'{indent}special handling src_cls {p_src.__class__.__name__} done')
                continue
            if isinstance(dest_type, EnumAttributeProperty):
                if p_current_entry_point.HasField(p_name):
                    value = enum_attr_from_p(p_current_entry_point, p_name, pm_dest, name)
                    setattr(pm_dest, name, value)
            elif isinstance(dest_type, DurationAttributeProperty):
                value = duration_from_p(p_src)
                setattr(pm_dest, name, value)
            elif isinstance(dest_type, NodeAttributeProperty):
                # handle optional / non-optional fields
                value = None
                if isOptional:
                    if p_current_entry_point.HasField(p_name):
                        value = p_src.value
                else:
                    value = p_src
                if value is not None:
                    if isinstance(dest_type, DecimalAttributeProperty):
                        if value != '':
                            setattr(pm_dest, name, DecimalConverter.toPy(value))
                    else:
                        setattr(pm_dest, name, value)
            elif isinstance(dest_type, NodeTextQNameProperty):
                # ToDo: convert normalized internal namespace to external one
                str_value = p_src if not isOptional else p_src.value
                qname = etree_.QName(str_value)
                setattr(pm_dest, name, qname)
            elif isinstance(dest_type, NodeEnumTextProperty):
                if p_current_entry_point.HasField(p_name):
                    value = enum_attr_from_p(p_current_entry_point, p_name, pm_dest, name)
                    setattr(pm_dest, name, value)
            elif isinstance(dest_type, NodeTextProperty):
                special_handler = _from_special_funcs.get(p_src.__class__)
                if special_handler:
                    print(f'{indent}special node text handling {p_src.__class__.__name__} = {special_handler.__name__}')
                    value = special_handler(p_src)
                    setattr(pm_dest, name, value)
                    print(f'{indent}special node text handling {p_src.__class__.__name__} ={value}, done')
                else:
                    str_value = p_src if not isOptional else p_src.value
                    setattr(pm_dest, name, str_value)
            elif isinstance(dest_type, OperationRefListAttributeProperty):
                dest_list = getattr(pm_dest, name)
                for elem in p_src.operation_ref:
                    dest_list.append(elem)
            elif isinstance(dest_type, AlertConditionRefListAttributeProperty):
                dest_list = getattr(pm_dest, name)
                for elem in p_src.alert_condition_reference:
                    dest_list.append(elem)
            elif isinstance(dest_type, NodeAttributeListProperty):
                # This is always a list of handles
                dest_list = getattr(pm_dest, name)
                for elem in p_src.entry_ref:
                    dest_list.append(elem)
            elif isinstance(dest_type, SubElementListProperty):
                dest_list = getattr(pm_dest, name)
                for elem in p_src:
                    special_handler = _from_special_funcs.get(elem.__class__)
                    if special_handler:
                        print(f'{indent}special list elem handling {elem.__class__.__name__} = {special_handler.__name__}')
                        pm_value = special_handler(elem)
                        dest_list.append(pm_value)
                        print(f'{indent}special list elem handling {pm_dest.__class__.__name__} = {pm_value} done')
                    else:
                        print(f'{indent}recursive list elem generic_from_p({elem.__class__.__name__})')
                        pm_value = generic_from_p(elem, None, indent + '    ')
                        dest_list.append(pm_value)
                        print(f'{indent}recursive list elem handling {pm_dest.__class__.__name__} = {pm_value} done')
            elif isinstance(dest_type, SubElementTextListProperty):
                dest_list = getattr(pm_dest, name)
                dest_list.extend(p_src)
            else:
                if p_current_entry_point.HasField(p_name):
                    print(f'{indent}recursive generic_from_p({p_src.__class__.__name__}, {pm_dest.__class__.__name__})')
                    value = generic_from_p(p_src, None, indent + '    ')
                    setattr(pm_dest, name, value)
                    print(f'{indent}recursive generic_from_p done')
    return pm_dest
