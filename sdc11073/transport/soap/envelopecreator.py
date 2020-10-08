from lxml import etree as etree_
import weakref
from ...namespaces import msgTag, QN_TYPE, nsmap, DocNamespaceHelper
from ...namespaces import Prefix_Namespace as Prefix
from . import soapenvelope
from .safety import SafetyInfoHeader


class SoapEnvelopeCreator:

    def __init__(self, sdc_definitions, logger):
        self._logger = logger
        self._sdc_definitions = sdc_definitions
        self._mdib_wref = None

    def register_mdib(self, mdib):
        ''' Client sometimes must know the mdib data (e.g. Set service, activate method).'''
        if mdib is not None and self._mdib_wref is not None:
            raise RuntimeError('SoapEnvelopeCreator has already an registered mdib')
        self._mdib_wref = None if mdib is None else weakref.ref(mdib)

    def mk_getdescriptor_envelope(self, to, port_type, handles):
        """

        :param handles: a list of strings
        :return: a list of etree nodes
        """
        requestparams = []
        for h in handles:
            node = etree_.Element(msgTag('HandleRef'))
            node.text = h
            requestparams.append(node)
        method = 'GetMdState'
        return self._mk_get_method_envelope(to, port_type, method, params=requestparams)

    def mk_getmdib_envelope(self, to, port_type):
        method = 'GetMdib'
        return self._mk_get_method_envelope(to, port_type, method)

    def mk_getmddescription_envelope(self, to, port_type, requestedHandles=None):
        """
        @param requestedHandles: None if all descriptors shall be requested, otherwise a list of handles
        """
        requestparams = []
        if requestedHandles is not None:
            for h in requestedHandles:
                node = etree_.Element(msgTag('HandleRef'))
                node.text = h
                requestparams.append(node)
        method = 'GetMdDescription'
        return self._mk_get_method_envelope(to, port_type, method, params=requestparams)

    def mk_getmdstate_envelope(self, to, port_type, requestedHandles=None):
        """
        @param requestedHandles: None if all states shall be requested, otherwise a list of handles
        """
        requestparams = []
        if requestedHandles is not None:
            for h in requestedHandles:
                node = etree_.Element(msgTag('HandleRef'))
                node.text = h
            requestparams.append(node)
        method = 'GetMdState'
        return self._mk_get_method_envelope(to, port_type, method, params=requestparams)

    def mk_getcontainmenttree_envelope(self, to, port_type, handles):
        """

        :param handles: a list of strings
        :return: a list of etree nodes
        """
        requestparams = []
        for h in handles:
            node = etree_.Element(msgTag('HandleRef'))
            node.text = h
            requestparams.append(node)
        method = 'GetContainmentTree'
        return self._mk_get_method_envelope(to, port_type, method, params=requestparams)

    def mk_getcontextstates_envelope(self, to, port_type, handles=None):
        """
        @param handles: a list of handles
        """
        requestparams = []
        if handles:
            for h in handles:
                requestparams.append(etree_.Element(msgTag('HandleRef'), attrib={QN_TYPE: '{}:HandleRef'.format(Prefix.MSG.prefix)},
                                             nsmap=Prefix.partialMap(Prefix.MSG, Prefix.PM)))
                requestparams[-1].text = h
        method = 'GetContextStates'
        return self._mk_get_method_envelope(to, port_type, method, params=requestparams)


    def mk_requestednumericvalue_envelope(self, to, port_type, operationHandle, requestedNumericValue):
        """create soap envelope, but do not send it. Used for unit testing"""
        requestedValueNode = etree_.Element(msgTag('RequestedNumericValue'),
                                            attrib={QN_TYPE: '{}:decimal'.format(Prefix.XSD.prefix)})
        requestedValueNode.text = str(requestedNumericValue)
        return self._mk_setmethod_envelope(to, port_type, 'SetValue', operationHandle, [requestedValueNode],
                                           additional_namespaces=[Prefix.XSD])

    def mk_requestedstring_envelope(self, to, port_type, operationHandle, requestedString):
        """create soap envelope, but do not send it. Used for unit testing"""
        requestedStringNode = etree_.Element(msgTag('RequestedStringValue'),
                                             attrib={QN_TYPE: '{}:string'.format(Prefix.XSD.prefix)})
        requestedStringNode.text = requestedString
        return self._mk_setmethod_envelope(to, port_type, 'SetString', operationHandle, [requestedStringNode],
                                           additional_namespaces=[Prefix.XSD])

    def mk_setalert_envelope(self, to, port_type, operationHandle, proposedAlertStates):
        """create soap envelope, but do not send it. Used for unit testing
        :param proposedAlertStates: a list AbstractAlertStateContainer or derived class """
        _proposedAlertStates = [p.mkCopy() for p in proposedAlertStates]
        for p in _proposedAlertStates:
            p.nsmapper = DocNamespaceHelper()  # use my namespaces
        _proposedAlertStateNodes = [p.mkStateNode(msgTag('ProposedAlertState')) for p in _proposedAlertStates]

        return self._mk_setmethod_envelope(to, port_type, 'SetAlertState', operationHandle, _proposedAlertStateNodes)

    def mk_setmetricstate_envelope(self, to, port_type, operationHandle, proposedMetricStates):
        """create soap envelope, but do not send it. Used for unit testing
        :param proposedMetricState: a list of AbstractMetricStateContainer or derived classes """
        _proposedMetricStates = [p.mkCopy() for p in proposedMetricStates]
        nsmapper = DocNamespaceHelper()
        for p in _proposedMetricStates:
            p.nsmapper = nsmapper  # use my namespaces
        _proposedMetricStateNodes = [p.mkStateNode(msgTag('ProposedMetricState')) for p in _proposedMetricStates]

        return self._mk_setmethod_envelope(to, port_type, 'SetMetricState', operationHandle, _proposedMetricStateNodes)

    def mk_setcomponentstate_envelope(self, to, port_type, operationHandle, proposedComponentStates):
        """Create soap envelope, but do not send it. Used for unit testing
        :param proposedComponentStates: a list of AbstractComponentStateContainers or derived classes """
        _proposedComponentStates = [p.mkCopy() for p in proposedComponentStates]
        nsmapper = DocNamespaceHelper()
        for p in _proposedComponentStates:
            p.nsmapper = nsmapper  # use my namespaces
        _proposedComponentStateNodes = [p.mkStateNode(msgTag('ProposedComponentState')) for p in
                                        _proposedComponentStates]

        return self._mk_setmethod_envelope(to, port_type, 'SetComponentState', operationHandle, _proposedComponentStateNodes)

    def mk_setcontextstate_envelope(self, to, port_type, operationHandle, proposedContextStates):
        """create soap envelope, but do not send it. Used for unit testing
        :param proposedContextStates: a list AbstractContextState or derived class """
        _proposedContextStates = [p.mkCopy() for p in proposedContextStates]
        for p in _proposedContextStates:
            # BICEPS: if handle == descriptorHandle, it means insert.
            if p.Handle is None:
                p.Handle = p.DescriptorHandle
            p.nsmapper = DocNamespaceHelper()  # use my namespaces
        _nodes = [p.mkStateNode(msgTag('ProposedContextState')) for p in _proposedContextStates]

        return self._mk_setmethod_envelope(to, port_type, 'SetContextState', operationHandle, _nodes)

    def mk_activate_envelope(self, to, port_type, operationHandle, value):
        """ an activate call does not return the result of the operation directly. Instead you get an transaction id,
        and will receive the status of this transaction as notification ("OperationInvokedReport").
        This method returns a "future" object. The future object has a result as soon as a final transaction state is received.
        @param operationHandle: a string
        @param value: a string
        @return: a concurrent.futures.Future object
        """
        # make message body
        soapBodyNode = etree_.Element(msgTag('Activate'), attrib=None, nsmap=nsmap)
        ref = etree_.SubElement(soapBodyNode, msgTag('OperationHandleRef'))
        ref.text = operationHandle
        argNode = None
        if value is not None:
            argNode = etree_.SubElement(soapBodyNode, msgTag('Argument'))
            argVal = etree_.SubElement(argNode, msgTag('ArgValue'))
            argVal.text = value

        # look for safety context in mdib
        sih = self._mk_optional_safetyheader(soapBodyNode, operationHandle)
        if sih is not None:
            sih = [sih]

        tmp = etree_.tostring(soapBodyNode)

        soapEnvelope = self._mk_soapenvelope(to, port_type, 'Activate', tmp, additionalHeaders=sih)

        #soapEnvelope = self._mk_soapenvelope_with_etree_body(to, port_type, 'Activate', soapBodyNode, additionalHeaders=sih)
        return soapEnvelope

    def mk_getlocalizedtext_envelope(self, to, port_type, refs=None, version=None, langs=None, textWidths=None, numberOfLines=None):
        '''

        :param refs: a list of strings or None
        :param version: an unsigned integer or None
        :param langs: a list of strings or None
        :param textWidths: a list of strings or None (each string one of xs, s, m, l, xs, xxs)
        :param numberOfLines: a list of unsigned integers or None
        :param request_manipulator:
        :return: a list of LocalizedText objects
        '''
        requestparams = []
        if refs is not None:
            for r in refs:
                node = etree_.Element(msgTag('Ref'))
                node.text = r
                requestparams.append(node)
        if version is not None:
            node = etree_.Element(msgTag('Version'))
            node.text = str(version)
            requestparams.append(node)
        if langs is not None:
            for l in langs:
                node = etree_.Element(msgTag('Lang'))
                node.text = l
                requestparams.append(node)
        if textWidths is not None:
            for tw in textWidths:
                node = etree_.Element(msgTag('TextWidth'))
                node.text = tw
                requestparams.append(node)
        if numberOfLines is not None:
            for nol in numberOfLines:
                node = etree_.Element(msgTag('NumberOfLines'))
                node.text = nol
                requestparams.append(node)
        method = 'GetLocalizedText'
        return self._mk_get_method_envelope(to, port_type, method, params=requestparams)

    def mk_getsupportedlanguages_envelope(self, to, port_type):
        method = 'GetSupportedLanguages'
        return self._mk_get_method_envelope(to, port_type, method)

    def _mk_get_method_envelope(self, to, port_type, method_name, params = None):
        bodyNode = etree_.Element(msgTag(method_name))
        soapEnvelope = soapenvelope.Soap12Envelope(Prefix.partialMap(Prefix.S12, Prefix.WSA, Prefix.MSG))
        action_string = self.get_action_string(port_type, method_name)
        soapEnvelope.setAddress(soapenvelope.WsAddress(action=action_string, to=to))
        if params:
            for p in params:
                bodyNode.append(p)
        soapEnvelope.addBodyObject(soapenvelope.GenericNode(bodyNode))
        return soapEnvelope

    def _mk_setmethod_envelope(self, to, port_type, method_name, operation_handle, request_nodes, additional_namespaces=None):
        ''' helper to create the soap envelope
        @param methodName: last element of name of the called action
        @param operationHandle: handle name as string
        @param requestNodes: a list of etree_ nodes that will become Subelement of Method name element
        '''
        soapBodyNode = etree_.Element( msgTag(method_name))
        ref = etree_.SubElement(soapBodyNode, msgTag('OperationHandleRef'), attrib={QN_TYPE: '{}:HandleRef'.format(Prefix.PM.prefix)}, nsmap=Prefix.partialMap(Prefix.PM))
        ref.text = operation_handle
        for n in request_nodes:
            soapBodyNode.append(n)
        if additional_namespaces:
            my_ns = Prefix.partialMap(Prefix.S12, Prefix.WSA, Prefix.PM, Prefix.MSG, *additional_namespaces)
        else:
            my_ns = Prefix.partialMap(Prefix.S12, Prefix.WSA, Prefix.PM, Prefix.MSG)

        sih = self._mk_optional_safetyheader(soapBodyNode, operation_handle) # a header or None

        soapEnvelope = soapenvelope.Soap12Envelope(my_ns)
        action_string = self.get_action_string(port_type, method_name)
        soapEnvelope.setAddress(soapenvelope.WsAddress(action=action_string, to=to))# self.endpoint_reference.address
        if sih is not None:
            soapEnvelope.addHeaderObject(sih)

        soapEnvelope.addBodyElement(soapBodyNode)
#         soapEnvelope.validateBody(self._bmmSchema)
        return soapEnvelope

    def _mk_optional_safetyheader(self, soapBodyNode, operationHandle):

        if self._mdib_wref is not None:
            op_descriptor = self._mdib_wref().descriptions.handle.getOne(operationHandle, allowNone=True)
            if op_descriptor is not None and op_descriptor.SafetyReq is not None:
                mdib_node = self._mdib_wref().reconstructMdibWithContextStates()
                return self._mk_safetyheader(soapBodyNode, op_descriptor.SafetyReq, mdib_node)
        return None

    def _mk_safetyheader(self, soapBodyNode, t_SafetyReq, mdibNode):
        dualChannelSelectors = {}
        safetyContextSelectors = {}

        if not t_SafetyReq.DualChannelDef:
            self._logger.info('no DualChannel selectors specified')
        else:
            for sel in  t_SafetyReq.DualChannelDef.Selector:
                selectorId = sel.Id
                selectorPath = sel.text
                values = soapBodyNode.xpath(selectorPath, namespaces=mdibNode.nsmap)
                if len(values) == 1:
                    self._logger.debug('DualChannel selector "{}": value = "{}", path= "{}"', selectorId, values[0], selectorPath)
                    dualChannelSelectors[selectorId] = str(values[0]).strip()
                elif len(values) == 0:
                    self._logger.error('DualChannel selector "{}": no value found! path= "{}"', selectorId, selectorPath)
                else:
                    self._logger.error('DualChannel selector "{}": path= "{}", multiple values found: {}', selectorId, selectorPath, values)

        if not t_SafetyReq.SafetyContextDef:
            self._logger.info('no Safety selectors specified')
        else:
            for sel in  t_SafetyReq.SafetyContextDef.Selector:
                selectorId = sel.Id
                selectorPath = sel.text
                # check the selector, there is a potential problem with the starting point of the xpath search path:
                if selectorPath.startswith('//'):
                    # double slashes means that the matching pattern can be located anywhere in the dom tree.
                    # No problem.
                    pass #
                elif selectorPath.startswith('/'):
                    # Problem! if the selector starts with a single slash, this is a xpath search that starts at the document root.
                    # But the convention is that the xpath search shall start from the top level element (=> without the toplevel element in the path)
                    # In order to follow this convention, remove the leading slash and start the search relative to the lop level node.
                    selectorPath = selectorPath[1:]
                values =  mdibNode.xpath(selectorPath, namespaces=mdibNode.nsmap)
                if len(values) == 1:
                    self._logger.debug('Safety selector "{}": value = "{}"  path= "{}"', selectorId, values[0], selectorPath)
                    safetyContextSelectors[selectorId] = str(values[0]).strip()
                elif len(values) == 0:
                    self._logger.error('Safety selector "{}":  no value found! path= "{}"', selectorId, selectorPath)
                else:
                    self._logger.error('Safety selector "{}": path= "{}", multiple values found: {}', selectorId, selectorPath, values)

        if dualChannelSelectors or safetyContextSelectors:
            return SafetyInfoHeader(dualChannelSelectors, safetyContextSelectors)
        else:
            return None

    def get_action_string(self, port_type, method_name):
        actions_lookup = self._sdc_definitions.Actions
        try:
            return getattr(actions_lookup, method_name)
        except AttributeError: # fallback, if a definition is missing
            return '{}/{}/{}'.format(self._sdc_definitions.ActionsNamespace, port_type, method_name)

    def _mk_soapenvelope(self, to, port_type, method_name, xmlBodyString=None, additionalHeaders=None):
        action = self.get_action_string(port_type, method_name)
        envelope = soapenvelope.Soap12Envelope(Prefix.partialMap(Prefix.S12, Prefix.MSG, Prefix.WSA))
        envelope.setAddress(soapenvelope.WsAddress(action=action, to=to))
        if additionalHeaders is not None:
            for h in additionalHeaders:
                envelope.addHeaderObject(h)
        if xmlBodyString is not None:
            envelope.addBodyString(xmlBodyString)
        return envelope
