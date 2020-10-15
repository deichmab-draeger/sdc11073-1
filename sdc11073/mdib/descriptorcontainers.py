import inspect
from collections import defaultdict, namedtuple
from lxml import etree as etree_
from .containerbase import ContainerBase
from .. import observableproperties as properties
from ..namespaces import domTag, extTag, siTag
from .. import pmtypes
from . import containerproperties as cp

_ChildElem = namedtuple('_ChildDef', 'name')  # member of own class
__ChildCont = namedtuple('__ChildCont', 'name type')  # a different container
__ChildConts = namedtuple('__ChildConts', 'name types')  # a different container

class _ChildCont(__ChildCont):
    def __repr__(self):
        return f'{self.__class__.__name__} name={self.name.localname} type={self.type.localname}'

class _ChildConts(__ChildConts):
    def __repr__(self):
        types = ', '.join([t.localname for t in self.types])
        return f'{self.__class__.__name__} name={self.name.localname} types={types}'


class AbstractDescriptorContainer(ContainerBase):
    '''
    This class represents the AbstractDescriptor type. It contains a DOM node of a descriptor.
    For convenience it makes some data of that node available as members:
    nodeName: QName of the node
    nodeType: QName of the type. If no type is defined, value is None
    parentHandle: string, never None (except root node)
    handle: string, but can be None
    descriptorVersion: int
    codingSystem
    codeId
    '''
    # these class variables allow easy type-checking. Derived classes will set corresponding values to True
    isSystemContextDescriptor = False
    isRealtimeSampleArrayMetricDescriptor = False
    isMetricDescriptor = False
    isOperationalDescriptor = False
    isComponentDescriptor = False
    isAlertDescriptor = False
    isAlertSignalDescriptor = False
    isAlertConditionDescriptor = False
    isContextDescriptor = False


    node = properties.ObservableProperty()  # the elementtree node

    Handle = cp.NodeAttributeProperty('Handle')
    handle = Handle
    ext_Extension = cp.ExtensionNodeProperty()
    DescriptorVersion = cp.IntegerAttributeProperty('DescriptorVersion',
                                                    defaultPyValue=0)  # optional, integer, defaults to 0
    SafetyClassification = cp.NodeAttributeProperty('SafetyClassification', impliedPyValue='Inf')  # optional
    Type = cp.SubElementProperty([domTag('Type')], valueClass=pmtypes.CodedValue)
    _props = ('Handle', 'DescriptorVersion', 'SafetyClassification', 'ext_Extension', 'Type')
    _children = (_ChildElem(extTag('Extension')),
                 _ChildElem(domTag('Type'))
                 )
    NODETYPE = None
    STATE_QNAME = None

    def __init__(self, nsmapper, handle, parentHandle):
        super(AbstractDescriptorContainer, self).__init__(nsmapper)
        self.parentHandle = parentHandle
        self.Handle = handle
        self._orderedChildContainers = defaultdict(list)  # needed to keep the order,  key is node name

    @property
    def coding(self):
        return self.Type.coding if self.Type is not None else None

    @property
    def codeId(self):
        return self.Type.coding.code if self.Type is not None else None  # pylint:disable=no-member

    @property
    def codingSystem(self):
        return self.Type.coding.codingSystem if self.Type is not None else None  # pylint:disable=no-member

    def incrementDescriptorVersion(self):
        if self.DescriptorVersion is None:
            self.DescriptorVersion = 1
        else:
            self.DescriptorVersion += 1

    def update_from_other_container(self, other, skipped_properties=None):
        if other.Handle != self.Handle:
            raise RuntimeError('Update from a container with different handle is not possible! Have "{}", got "{}"'.format(self.Handle, other.Handle))
        self._update_from_other(other, skipped_properties)

    def connectChildContainers(self, node, containers):
        ret = self._connectChildNodes(node, containers)
        order = self._sortedChildNames()
        self._sortChildNodes(node, order)
        return ret

    def addChild(self, childDescriptorContainer):
        self._orderedChildContainers[childDescriptorContainer.NODETYPE].append(childDescriptorContainer)

    def rmChild(self, childDescriptorContainer):
        tag_specific_list = self._orderedChildContainers[childDescriptorContainer.NODETYPE]
        for container in tag_specific_list:
            if container.handle == childDescriptorContainer.handle:
                tag_specific_list.remove(container)

    def getOrderedChildContainers(self):
        ret = []
        for n in self._sortedChildNames():
            if hasattr(n, 'type'):  # _ChildCont
                ret.extend(self._orderedChildContainers[n.type])
            elif hasattr(n, 'types'):  # _ChildConts
                for t in n.types:
                    ret.extend(self._orderedChildContainers[t])
        return ret

    @property
    def orderedChildHandles(self):
        return [c.handle for c in self.getOrderedChildContainers()]

    def getActualValue(self, attr_name):
        ''' ignores default value and implied value, e.g. returns None if value is not present in xml'''
        return getattr(self.__class__, attr_name).getActualValue(self)

    def _connectChildNodes(self, node, containers):
        ret = []
        # add all child container nodes
        child_defs = self._sortedChildNames()
        for c in containers:
            child_def = [ch for ch in child_defs if (hasattr(ch, 'type') and c.NODETYPE == ch.type)]
            child_def.extend([ ch for ch in child_defs if (hasattr(ch, 'types') and c.NODETYPE in ch.types)])
            if len(child_def) != 1:
                raise ValueError(f'{self.__class__.__name__} has no child definition for {c.NODETYPE}')
            n = c.mkDescriptorNode(tag=child_def[0].name)
            node.append(n)
            ret.append((c, n))
        return ret

    def _sortedContainerProperties(self):
        '''
        @return: a list of (name, object) tuples of all GenericProperties ( and subclasses)
        '''
        ret = []
        classes = inspect.getmro(self.__class__)
        for cls in reversed(classes):
            try:
                names = cls.__dict__['_props']  # only access class member of this class, not parent
            except:
                continue
            for name in names:
                obj = getattr(cls, name)
                if obj is not None:
                    ret.append((name, obj))
        return ret

    def _sortedChildNames(self):
        '''
        @return: a list of _Child definitions (_ChildElem or ChildCont)
        '''
        ret = []
        classes = inspect.getmro(self.__class__)
        for cls in reversed(classes):
            try:
                names = cls.__dict__['_children']  # only access class member of this class, not parent
                ret.extend(names)
            except:
                continue
        return ret

    def mkDescriptorNode(self, tag, setXsiType=True):
        '''
        Creates a lxml etree node from instance data.
        :param setXsiType:
        :param tag: tag of node, defaults to self.nodeName
        :return: an etree node
        '''
        if tag is None:
            raise Exception('no tag name!')
        node = etree_.Element(tag, attrib={'Handle': self.handle}, nsmap=self.nsmapper.docNssmap)
        self._updateNode(node, setXsiType)
        order = self._sortedChildNames()
        self._sortChildNodes(node, order)
        return node

    def _sortChildNodes(self, node, ordered_tags):
        '''
        raises an ValueError if a child node exist that is not listed in ordered_tags
        @param ordered_tags: a list of QNames
        '''
        qnames = [o.name for o in ordered_tags]
        not_in_order = [n for n in node if n.tag not in qnames]
        if len(not_in_order) > 0:
            raise ValueError('{}: not in Order:{} node={}, order={}'.format(self.__class__.__name__,
                                                                            [n.tag for n in not_in_order], node.tag,
                                                                            [o.localname for o in qnames]))
        allChildNodes = node[:]
        for c in allChildNodes:
            node.remove(c)
        for qname in qnames:
            for n in allChildNodes:
                if n.tag == qname:
                    node.append(n)

    def __str__(self):
        name = self.NODETYPE.localname or None
        return 'Descriptor "{}": handle={} descrVersion={} parent={}'.format(name, self.handle,
                                                                             self.DescriptorVersion, self.parentHandle)

    def __repr__(self):
        name = self.NODETYPE.localname or None
        return 'Descriptor "{}": handle={} descrVersion={} parent={}'.format(name, self.handle,
                                                                             self.DescriptorVersion, self.parentHandle)

    @classmethod
    def fromNode(cls, nsmapper, node, parentHandle):
        obj = cls(nsmapper,
                  handle=None,  # will be determined in constructor from node value
                  parentHandle=parentHandle)
        obj._updateFromNode(node)
        return obj


class AbstractDeviceComponentDescriptorContainer(AbstractDescriptorContainer):
    isComponentDescriptor = True
    ProductionSpecification = cp.SubElementListProperty([domTag('ProductionSpecification')],
                                                        cls=pmtypes.ProductionSpecification)
    _props = ('ProductionSpecification',)
    _children = (_ChildElem(domTag('ProductionSpecification')),
                 )



class AbstractComplexDeviceComponentDescriptorContainer(AbstractDeviceComponentDescriptorContainer):
    _children = (_ChildCont(domTag('AlertSystem'), domTag('AlertSystemDescriptor')),
                 _ChildCont(domTag('Sco'), domTag('ScoDescriptor'))
                 )


class MdsDescriptorContainer(AbstractComplexDeviceComponentDescriptorContainer):
    NODETYPE = domTag('MdsDescriptor')
    STATE_QNAME = domTag('MdsState')
    mNodeName = domTag('MetaData')
    Udi = cp.SubElementListProperty([mNodeName, domTag('Udi')], cls=pmtypes.T_Udi)  # 0...n
    Manufacturer = cp.SubElementListProperty([mNodeName, domTag('Manufacturer')], cls=pmtypes.LocalizedText)
    ModelName = cp.SubElementListProperty([mNodeName, domTag('ModelName')], cls=pmtypes.LocalizedText)
    ModelNumber = cp.NodeTextProperty([mNodeName, domTag('ModelNumber')])
    SerialNumber = cp.SubElementListProperty([mNodeName, domTag('SerialNumber')],
                                             cls=pmtypes.ElementWithTextOnly)
    _props = ('Udi', 'Manufacturer', 'ModelName', 'ModelNumber', 'SerialNumber')
    _children = (_ChildElem(domTag('MetaData')),
                 _ChildCont(domTag('SystemContext'), domTag('SystemContextDescriptor')),
                 _ChildCont(domTag('Clock'), domTag('ClockDescriptor')),
                 _ChildCont(domTag('Battery'), domTag('BatteryDescriptor')),
                 _ChildElem(domTag('ApprovedJurisdictions')),  #Todo: implement
                 _ChildCont(domTag('Vmd'), domTag('VmdDescriptor')),
                 )

    def connectChildContainers(self, node, containers):
        ret = super(MdsDescriptorContainer, self).connectChildContainers(node, containers)
        self._sortMetaData(node)
        return ret

    def _sortMetaData(self, node):
        # sort also MetaData SubNode
        metaDataNode = node.find(domTag('MetaData'))
        if metaDataNode is not None:
            order = (_ChildElem(domTag('Udi')),
                     _ChildElem(domTag('Manufacturer')),
                     _ChildElem(domTag('ModelName')),
                     _ChildElem(domTag('ModelNumber')),
                     _ChildElem(domTag('SerialNumber')),
                     )
            self._sortChildNodes(metaDataNode, order)

    def mkDescriptorNode(self, tag, setXsiType=True):
        '''returns a node without any child with a handle'''
        node = super(MdsDescriptorContainer, self).mkDescriptorNode(tag, setXsiType)
        self._sortMetaData(node)
        return node


class VmdDescriptorContainer(AbstractComplexDeviceComponentDescriptorContainer):
    NODETYPE = domTag('VmdDescriptor')
    STATE_QNAME = domTag('VmdState')
    _children = (_ChildCont(domTag('Channel'), domTag('ChannelDescriptor')),
                 )


class ChannelDescriptorContainer(AbstractDeviceComponentDescriptorContainer):
    NODETYPE = domTag('ChannelDescriptor')
    STATE_QNAME = domTag('ChannelState')
    _children = (_ChildConts(domTag('Metric'), (domTag('NumericMetricDescriptor'),
                                                domTag('StringMetricDescriptor'),
                                                domTag('EnumStringMetricDescriptor'),
                                                domTag('RealTimeSampleArrayMetricDescriptor'),
                                                domTag('DistributionSampleArrayMetricDescriptor'),
                                               )
                            ),
                 )


class ClockDescriptorContainer(AbstractDeviceComponentDescriptorContainer):
    NODETYPE = domTag('ClockDescriptor')
    STATE_QNAME = domTag('ClockState')
    TimeProtocol = cp.SubElementListProperty([domTag('TimeProtocol')], cls=pmtypes.CodedValue)
    Resolution = cp.DurationAttributeProperty('Resolution')  # optional,  xsd:duration
    _props = ('TimeProtocol', 'Resolution')
    _children = (_ChildElem(domTag('TimeProtocol')),
                 )


class BatteryDescriptorContainer(AbstractDeviceComponentDescriptorContainer):
    NODETYPE = domTag('BatteryDescriptor')
    STATE_QNAME = domTag('BatteryState')
    CapacityFullCharge = cp.SubElementProperty([domTag('CapacityFullCharge')],
                                               valueClass=pmtypes.Measurement)  # optional
    CapacitySpecified = cp.SubElementProperty([domTag('CapacitySpecified')], valueClass=pmtypes.Measurement)  # optional
    VoltageSpecified = cp.SubElementProperty([domTag('VoltageSpecified')], valueClass=pmtypes.Measurement)  # optional
    _props = ('CapacityFullCharge', 'CapacitySpecified', 'VoltageSpecified')
    _children = (_ChildElem(domTag('CapacityFullCharge')),
                 _ChildElem(domTag('CapacitySpecified')),
                 _ChildElem(domTag('VoltageSpecified')),
                 )


class ScoDescriptorContainer(AbstractDeviceComponentDescriptorContainer):
    NODETYPE = domTag('ScoDescriptor')
    STATE_QNAME = domTag('ScoState')
    # This has AbstractOperationDescriptor children. Not modeled here
    _children = (_ChildConts(domTag('Operation'), (domTag('SetValueOperationDescriptor'),
                                                   domTag('SetStringOperationDescriptor'),
                                                   domTag('SetContextStateOperationDescriptor'),
                                                   domTag('SetMetricStateOperationDescriptor'),
                                                   domTag('SetComponentStateOperationDescriptor'),
                                                   domTag('SetAlertStateOperationDescriptor'),
                                                   domTag('ActivateOperationDescriptor')
                                                   )
                             ),
                 )


class AbstractMetricDescriptorContainer(AbstractDescriptorContainer):
    isMetricDescriptor = True
    Unit = cp.SubElementProperty([domTag('Unit')], valueClass=pmtypes.CodedValue)
    BodySite = cp.SubElementListProperty([domTag('BodySite')], cls=pmtypes.CodedValue)
    Relation = cp.SubElementListProperty([domTag('Relation')], cls=pmtypes.Relation) # o...n
    MetricCategory = cp.NodeAttributeProperty('MetricCategory', defaultPyValue='Unspec')  # required
    DerivationMethod = cp.NodeAttributeProperty('DerivationMethod')  # optional
    #  There is an implied value defined, but it is complicated, therefore here not implemented:
    # - If pm:AbstractDescriptor/@MetricCategory is "Set" or "Preset", then the default value of DerivationMethod is "Man"
    # - If pm:AbstractDescriptor/@MetricCategory is "Clc", "Msrmt", "Rcmm", then the default value of DerivationMethod is "Auto"
    # - If pm:AbstractDescriptor/@MetricCategory is "Unspec", then no default value is being implied</xsd:documentation>
    MetricAvailability = cp.NodeAttributeProperty('MetricAvailability', defaultPyValue='Cont')  # required
    MaxMeasurementTime = cp.DurationAttributeProperty('MaxMeasurementTime')  # optional,  xsd:duration
    MaxDelayTime = cp.DurationAttributeProperty('MaxDelayTime')  # optional,  xsd:duration
    DeterminationPeriod = cp.DurationAttributeProperty('DeterminationPeriod')  # optional,  xsd:duration
    LifeTimePeriod = cp.DurationAttributeProperty('LifeTimePeriod')  # optional,  xsd:duration
    ActivationDuration = cp.DurationAttributeProperty('ActivationDuration')  # optional,  xsd:duration
    _props = ('Unit', 'BodySite', 'Relation', 'MetricCategory', 'DerivationMethod', 'MetricAvailability', 'MaxMeasurementTime',
              'MaxDelayTime', 'DeterminationPeriod', 'LifeTimePeriod', 'ActivationDuration')
    _children = (_ChildElem(domTag('Unit')),
                 _ChildElem(domTag('BodySite')),
                 _ChildElem(domTag('Relation')),
                 )

    def addChild(self, childDescriptorContainer):
        raise ValueError('Metric can not have children')

    def rmChild(self, childDescriptorContainer):
        raise ValueError('Metric can not have children')


class NumericMetricDescriptorContainer(AbstractMetricDescriptorContainer):
    NODETYPE = domTag('NumericMetricDescriptor')
    STATE_QNAME = domTag('NumericMetricState')
    TechnicalRange = cp.SubElementListProperty([domTag('TechnicalRange')], cls=pmtypes.Range)
    Resolution = cp.DecimalAttributeProperty('Resolution')  # optional
    AveragingPeriod = cp.DurationAttributeProperty('AveragingPeriod')  # optional
    _props = ('TechnicalRange', 'Resolution', 'AveragingPeriod')
    _children = (_ChildElem(domTag('TechnicalRange')),
                 )


class StringMetricDescriptorContainer(AbstractMetricDescriptorContainer):
    NODETYPE = domTag('StringMetricDescriptor')
    STATE_QNAME = domTag('StringMetricState')


class EnumStringMetricDescriptorContainer(StringMetricDescriptorContainer):
    NODETYPE = domTag('EnumStringMetricDescriptor')
    STATE_QNAME = domTag('EnumStringMetricState')
    AllowedValue = cp.SubElementListProperty([domTag('AllowedValue')], cls=pmtypes.AllowedValue)
    _props = ('AllowedValue',)
    _children = (_ChildElem(domTag('AllowedValue')),
                 )


class RealTimeSampleArrayMetricDescriptorContainer(AbstractMetricDescriptorContainer):
    isRealtimeSampleArrayMetricDescriptor = True
    NODETYPE = domTag('RealTimeSampleArrayMetricDescriptor')
    STATE_QNAME = domTag('RealTimeSampleArrayMetricState')
    TechnicalRange = cp.SubElementListProperty([domTag('TechnicalRange')], cls=pmtypes.Range)
    Resolution = cp.DecimalAttributeProperty('Resolution')  # optional
    SamplePeriod = cp.DurationAttributeProperty('SamplePeriod')  # required
    _props = ('TechnicalRange', 'Resolution', 'SamplePeriod')
    _children = (_ChildElem(domTag('TechnicalRange')),
                 )


class DistributionSampleArrayMetricDescriptorContainer(AbstractMetricDescriptorContainer):
    NODETYPE = domTag('DistributionSampleArrayMetricDescriptor')
    STATE_QNAME = domTag('DistributionSampleArrayMetricState')
    TechnicalRange = cp.SubElementListProperty([domTag('TechnicalRange')], cls=pmtypes.Range)
    DomainUnit = cp.SubElementProperty([domTag('DomainUnit')], valueClass=pmtypes.CodedValue)
    DistributionRange = cp.SubElementProperty([domTag('DistributionRange')], valueClass=pmtypes.Range)
    Resolution = cp.DecimalAttributeProperty('Resolution')  # required
    _props = ('TechnicalRange', 'DomainUnit', 'DistributionRange', 'Resolution')
    _children = (_ChildElem(domTag('TechnicalRange')),
                 _ChildElem(domTag('DomainUnit')),
                 _ChildElem(domTag('DistributionRange')),
                 )


class AbstractOperationDescriptorContainer(AbstractDescriptorContainer):
    isOperationalDescriptor = True
    OperationTarget = cp.NodeAttributeProperty('OperationTarget')
    SafetyReq = cp.SubElementProperty([extTag('Extension'), siTag('SafetyReq')], valueClass=pmtypes.T_SafetyReq)
    InvocationEffectiveTimeout = cp.DurationAttributeProperty('InvocationEffectiveTimeout') # optional  xsd:duration
    MaxTimeToFinish = cp.DurationAttributeProperty('MaxTimeToFinish') # optional  xsd:duration
    Retriggerable = cp.BooleanAttributeProperty('Retriggerable', impliedPyValue=True) # optional
    #  AccessLevel can be: Usr (User), CSUsr (Clinical Super User), RO (Responsible Organization), SP (Service Personnel), Oth (Other)
    AccessLevel = cp.NodeAttributeProperty('AccessLevel', impliedPyValue='Usr')
    _props = ('OperationTarget', 'SafetyReq', 'InvocationEffectiveTimeout', 'MaxTimeToFinish', 'Retriggerable')


class SetValueOperationDescriptorContainer(AbstractOperationDescriptorContainer):
    NODETYPE = domTag('SetValueOperationDescriptor')
    STATE_QNAME = domTag('SetValueOperationState')



class SetStringOperationDescriptorContainer(AbstractOperationDescriptorContainer):
    NODETYPE = domTag('SetStringOperationDescriptor')
    STATE_QNAME = domTag('SetStringOperationState')
    MaxLength = cp.IntegerAttributeProperty('MaxLength')
    _props = ('MaxLength',)


class AbstractSetStateOperationDescriptor(AbstractOperationDescriptorContainer):
    ModifiableData = cp.SubElementListProperty([domTag('ModifiableData')], cls = pmtypes.ElementWithTextOnly)
    _props = ('ModifiableData',)
    _children = (_ChildElem(domTag('ModifiableData')),
                 )


class SetContextStateOperationDescriptorContainer(AbstractSetStateOperationDescriptor):
    NODETYPE = domTag('SetContextStateOperationDescriptor')
    STATE_QNAME = domTag('SetContextStateOperationState')


class SetMetricStateOperationDescriptorContainer(AbstractSetStateOperationDescriptor):
    NODETYPE = domTag('SetMetricStateOperationDescriptor')
    STATE_QNAME = domTag('SetMetricStateOperationState')


class SetComponentStateOperationDescriptorContainer(AbstractSetStateOperationDescriptor):
    NODETYPE = domTag('SetComponentStateOperationDescriptor')
    STATE_QNAME = domTag('SetComponentStateOperationState')


class SetAlertStateOperationDescriptorContainer(AbstractSetStateOperationDescriptor):
    NODETYPE = domTag('SetAlertStateOperationDescriptor')
    STATE_QNAME = domTag('SetAlertStateOperationState')


class ActivateOperationDescriptorContainer(AbstractSetStateOperationDescriptor):
    NODETYPE = domTag('ActivateOperationDescriptor')
    STATE_QNAME = domTag('ActivateOperationState')
    Argument = cp.SubElementListProperty([domTag('Argument')], cls = pmtypes.Argument)
    _props = ('Argument',)
    _children = (_ChildElem(domTag('Argument')),
                 )


class AbstractAlertDescriptorContainer(AbstractDescriptorContainer):
    '''AbstractAlertDescriptor acts as a base class for all alert descriptors that contain static alert meta information.
     This class has nor specific data.''' 
    isAlertDescriptor = True


class AlertSystemDescriptorContainer(AbstractAlertDescriptorContainer):
    '''AlertSystemDescriptor describes an ALERT SYSTEM to detect ALERT CONDITIONs and generate ALERT SIGNALs, 
    which belong to specific ALERT CONDITIONs.
    ALERT CONDITIONs are represented by a list of pm:AlertConditionDescriptor ELEMENTs and 
    ALERT SIGNALs are represented by a list of pm:AlertSignalDescriptor ELEMENTs.
    '''
    NODETYPE = domTag('AlertSystemDescriptor')
    STATE_QNAME = domTag('AlertSystemState')
    MaxPhysiologicalParallelAlarms = cp.IntegerAttributeProperty('MaxPhysiologicalParallelAlarms')
    MaxTechnicalParallelAlarms = cp.IntegerAttributeProperty('MaxTechnicalParallelAlarms')
    SelfCheckPeriod = cp.DurationAttributeProperty('SelfCheckPeriod')
    _props = ('MaxPhysiologicalParallelAlarms', 'MaxTechnicalParallelAlarms', 'SelfCheckPeriod')
    _children = (_ChildConts(domTag('AlertCondition'), (domTag('AlertConditionDescriptor'),
                                                        domTag('LimitAlertConditionDescriptor')
                                                        )
                             ),
                 _ChildCont(domTag('AlertSignal'), domTag('AlertSignalDescriptor')),
                 )


class AlertConditionDescriptorContainer(AbstractAlertDescriptorContainer):
    '''An ALERT CONDITION contains the information about a potentially or actually HAZARDOUS SITUATION.
      Examples: a physiological alarm limit has been exceeded or a sensor has been unplugged.'''
    isAlertConditionDescriptor = True
    NODETYPE = domTag('AlertConditionDescriptor')
    STATE_QNAME = domTag('AlertConditionState')
    Source = cp.SubElementListProperty([domTag('Source')], cls = pmtypes.ElementWithTextOnly) # a list of 0...n pm:HandleRef elements
    CauseInfo = cp.SubElementListProperty([domTag('CauseInfo')], cls = pmtypes.CauseInfo) # a list of 0...n pm:CauseInfo elements
    Kind = cp.NodeAttributeProperty('Kind', defaultPyValue=pmtypes.AlertConditionKind.OTHER)  # required, type=AlertConditionKind
    Priority = cp.NodeAttributeProperty('Priority', defaultPyValue=pmtypes.AlertConditionPriority.NONE)  # required, type= AlertConditionPriority
    DefaultConditionGenerationDelay = cp.DurationAttributeProperty('DefaultConditionGenerationDelay', impliedPyValue=0) # optional
    CanEscalate = cp.NodeAttributeProperty('CanEscalate') # AlertConditionPriority, without 'None'
    CanDeescalate = cp.NodeAttributeProperty('CanDeescalate') # AlertConditionPriority, without 'Hi'
    _props = ('Source', 'CauseInfo', 'Kind', 'Priority', 'DefaultConditionGenerationDelay', 'CanEscalate', 'CanDeescalate')
    _children = (_ChildElem(domTag('Source')),
                 _ChildElem(domTag('CauseInfo')),
                 )


class LimitAlertConditionDescriptorContainer(AlertConditionDescriptorContainer):
    NODETYPE = domTag('LimitAlertConditionDescriptor')
    STATE_QNAME = domTag('LimitAlertConditionState')
    MaxLimits = cp.SubElementProperty([domTag('MaxLimits')], valueClass=pmtypes.Range)
    AutoLimitSupported = cp.BooleanAttributeProperty('AutoLimitSupported', impliedPyValue=False)
    _props = ('MaxLimits', 'AutoLimitSupported',)
    _children = (_ChildElem(domTag('MaxLimits')),
                 )


class AlertSignalDescriptorContainer(AbstractAlertDescriptorContainer):
    isAlertSignalDescriptor = True
    NODETYPE = domTag('AlertSignalDescriptor')
    STATE_QNAME = domTag('AlertSignalState')
    ConditionSignaled = cp.NodeAttributeProperty('ConditionSignaled') # required, a HandleRef
    Manifestation = cp.NodeAttributeProperty('Manifestation') # required, an AlertSignalManifestation ('Aud', 'Vis', 'Tan', 'Oth')
    Latching = cp.BooleanAttributeProperty('Latching') # required
    DefaultSignalGenerationDelay = cp.DurationAttributeProperty('DefaultSignalGenerationDelay', impliedPyValue=0)# optional, defaults to PT0s ( 0 seconds)
    SignalDelegationSupported = cp.BooleanAttributeProperty('SignalDelegationSupported', impliedPyValue=False) # optional, defaults to false
    AcknowledgementSupported = cp.BooleanAttributeProperty('AcknowledgementSupported', impliedPyValue=False) # optional, defaults to false
    AcknowledgeTimeout = cp.DurationAttributeProperty('AcknowledgeTimeout') # optional
    _props = ('ConditionSignaled', 'Manifestation', 'Latching', 'DefaultSignalGenerationDelay', 'SignalDelegationSupported', 
              'AcknowledgementSupported', 'AcknowledgeTimeout')


    
class SystemContextDescriptorContainer(AbstractDescriptorContainer):
    isSystemContextDescriptor = True
    NODETYPE = domTag('SystemContextDescriptor')
    STATE_QNAME = domTag('SystemContextState')
    _children = (_ChildCont(domTag('PatientContext'), domTag('PatientContextDescriptor')),
                 _ChildCont(domTag('LocationContext'), domTag('LocationContextDescriptor')),
                 _ChildCont(domTag('EnsembleContext'), domTag('EnsembleContextDescriptor')),
                 _ChildCont(domTag('OperatorContext'), domTag('OperatorContextDescriptor')),
                 _ChildCont(domTag('WorkflowContext'), domTag('WorkflowContextDescriptor')),
                 _ChildCont(domTag('MeansContext'), domTag('MeansContextDescriptor')),
                 )


class AbstractContextDescriptorContainer(AbstractDescriptorContainer):
    isContextDescriptor = True


class PatientContextDescriptorContainer(AbstractContextDescriptorContainer):
    NODETYPE = domTag('PatientContextDescriptor')
    STATE_QNAME = domTag('PatientContextState')


class LocationContextDescriptorContainer(AbstractContextDescriptorContainer):
    NODETYPE = domTag('LocationContextDescriptor')
    STATE_QNAME = domTag('LocationContextState')


class WorkflowContextDescriptorContainer(AbstractContextDescriptorContainer):
    NODETYPE = domTag('WorkflowContextDescriptor')
    STATE_QNAME = domTag('WorkflowContextState')


class OperatorContextDescriptorContainer(AbstractContextDescriptorContainer):
    NODETYPE = domTag('OperatorContextDescriptor')
    STATE_QNAME = domTag('OperatorContextState')

class MeansContextDescriptorContainer(AbstractContextDescriptorContainer):
    NODETYPE = domTag('MeansContextDescriptor')
    STATE_QNAME = domTag('MeansContextState')

class EnsembleContextDescriptorContainer(AbstractContextDescriptorContainer):
    NODETYPE = domTag('EnsembleContextDescriptor')
    STATE_QNAME = domTag('EnsembleContextState')


_name_class_lookup = {
    domTag('Battery'): BatteryDescriptorContainer,
    domTag('BatteryDescriptor'): BatteryDescriptorContainer,
    domTag('Mds'): MdsDescriptorContainer,
    domTag('MdsDescriptor'): MdsDescriptorContainer,
    domTag('Vmd'): VmdDescriptorContainer,
    domTag('VmdDescriptor'): VmdDescriptorContainer,
    domTag('Sco'): ScoDescriptorContainer,
    domTag('ScoDescriptor'): ScoDescriptorContainer,
    domTag('Channel'): ChannelDescriptorContainer,
    domTag('ChannelDescriptor'): ChannelDescriptorContainer,
    domTag('Clock'): ClockDescriptorContainer,
    domTag('ClockDescriptor'): ClockDescriptorContainer,
    domTag('SystemContext'): SystemContextDescriptorContainer,
    domTag('SystemContextDescriptor'): SystemContextDescriptorContainer,
    domTag('PatientContext'): PatientContextDescriptorContainer,
    domTag('LocationContext'): LocationContextDescriptorContainer,
    domTag('PatientContextDescriptor'): PatientContextDescriptorContainer,
    domTag('LocationContextDescriptor'): LocationContextDescriptorContainer,
    domTag('WorkflowContext'): WorkflowContextDescriptorContainer,
    domTag('WorkflowContextDescriptor'): WorkflowContextDescriptorContainer,
    domTag('OperatorContext'): OperatorContextDescriptorContainer,
    domTag('OperatorContextDescriptor'): OperatorContextDescriptorContainer,
    domTag('MeansContext'): MeansContextDescriptorContainer,
    domTag('MeansContextDescriptor'): MeansContextDescriptorContainer,
    domTag('EnsembleContext'): EnsembleContextDescriptorContainer,
    domTag('EnsembleContextDescriptor'): EnsembleContextDescriptorContainer,
    domTag('AlertSystem'): AlertSystemDescriptorContainer,
    domTag('AlertSystemDescriptor'): AlertSystemDescriptorContainer,
    domTag('AlertCondition'): AlertConditionDescriptorContainer,
    domTag('AlertConditionDescriptor'): AlertConditionDescriptorContainer,
    domTag('AlertSignal'): AlertSignalDescriptorContainer,
    domTag('AlertSignalDescriptor'): AlertSignalDescriptorContainer,
    domTag('StringMetricDescriptor'): StringMetricDescriptorContainer,
    domTag('EnumStringMetricDescriptor'): EnumStringMetricDescriptorContainer,
    domTag('NumericMetricDescriptor'): NumericMetricDescriptorContainer,
    domTag('RealTimeSampleArrayMetricDescriptor'): RealTimeSampleArrayMetricDescriptorContainer,
    domTag('DistributionSampleArrayMetricDescriptor'): DistributionSampleArrayMetricDescriptorContainer,
    domTag('LimitAlertConditionDescriptor'): LimitAlertConditionDescriptorContainer,
    domTag('SetValueOperationDescriptor'): SetValueOperationDescriptorContainer,
    domTag('SetStringOperationDescriptor'): SetStringOperationDescriptorContainer,
    domTag('ActivateOperationDescriptor'): ActivateOperationDescriptorContainer,
    domTag('SetContextStateOperationDescriptor'): SetContextStateOperationDescriptorContainer,
    domTag('SetMetricStateOperationDescriptor'): SetMetricStateOperationDescriptorContainer,
    domTag('SetComponentStateOperationDescriptor'): SetComponentStateOperationDescriptorContainer,
    domTag('SetAlertStateOperationDescriptor'): SetAlertStateOperationDescriptorContainer,
    }

def getContainerClass(qNameType):
    '''
    @param qNameType: a QName instance
    '''
    # first check type, this is more specific. 
    return _name_class_lookup.get(qNameType)
