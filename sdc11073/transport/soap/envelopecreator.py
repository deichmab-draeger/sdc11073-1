from lxml import etree as etree_
import weakref
from ...namespaces import msgTag, QN_TYPE, nsmap, DocNamespaceHelper
from ...namespaces import Prefix_Namespace as Prefix
from ...namespaces import nsmap
from . import soapenvelope
from .safety import SafetyInfoHeader

class SoapEnvelopeCreator:

    def __init__(self, sdc_definitions, logger):
        self._logger = logger
        self._sdc_definitions = sdc_definitions
        self._mdib_wref = None


    @staticmethod
    def mk_getmetadata_envelope(to):
        soap_envelope = soapenvelope.Soap12Envelope(nsmap)
        soap_envelope.setAddress(
            soapenvelope.WsAddress(action='http://schemas.xmlsoap.org/ws/2004/09/mex/GetMetadata/Request',
                                   to=to))
        soap_envelope.addBodyObject(
            soapenvelope.GenericNode(etree_.Element('{http://schemas.xmlsoap.org/ws/2004/09/mex}GetMetadata')))
        return soap_envelope

    def register_mdib(self, mdib):
        """Client sometimes must know the mdib data (e.g. Set service, activate method).
        :param mdib: the current mdib
        """
        if mdib is not None and self._mdib_wref is not None:
            raise RuntimeError('SoapEnvelopeCreator has already an registered mdib')
        self._mdib_wref = None if mdib is None else weakref.ref(mdib)

    def mk_getdescriptor_envelope(self, to, port_type, requested_handles):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param requested_handles: a list of strings
        :return: a SoapEnvelope
        """
        method = 'GetMdState'
        return self._mk_get_method_envelope(to, port_type, method, params=_handles2params(requested_handles))

    def mk_getmdib_envelope(self, to, port_type):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :return: a SoapEnvelope
        """
        method = 'GetMdib'
        return self._mk_get_method_envelope(to, port_type, method)

    def mk_getmddescription_envelope(self, to, port_type, requested_handles=None):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param requested_handles: a list of strings
        :return: a SoapEnvelope
        """
        method = 'GetMdDescription'
        return self._mk_get_method_envelope(to, port_type, method, params=_handles2params(requested_handles))

    def mk_getmdstate_envelope(self, to, port_type, requested_handles=None):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param requested_handles: a list of strings
        :return: a SoapEnvelope
        """
        method = 'GetMdState'
        return self._mk_get_method_envelope(to, port_type, method, params=_handles2params(requested_handles))

    def mk_getcontainmenttree_envelope(self, to, port_type, requested_handles):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param requested_handles: a list of strings
        :return: a SoapEnvelope
        """
        method = 'GetContainmentTree'
        return self._mk_get_method_envelope(to, port_type, method, params=_handles2params(requested_handles))

    def mk_getcontextstates_envelope(self, to, port_type, requested_handles=None):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param requested_handles: a list of strings
        :return: a SoapEnvelope
        """
        requestparams = []
        if requested_handles:
            for h in requested_handles:
                requestparams.append(etree_.Element(msgTag('HandleRef'),
                                                    attrib={QN_TYPE: '{}:HandleRef'.format(Prefix.MSG.prefix)},
                                                    nsmap=Prefix.partialMap(Prefix.MSG, Prefix.PM)))
                requestparams[-1].text = h
        method = 'GetContextStates'
        return self._mk_get_method_envelope(to, port_type, method, params=requestparams)

    def mk_requestednumericvalue_envelope(self, to, port_type, operation_handle, requested_numeric_value):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param operation_handle: the handle of operation that is called
        :param requested_numeric_value: a string
        :return: a SoapEnvelope
        """
        requested_value_node = etree_.Element(msgTag('RequestedNumericValue'),
                                              attrib={QN_TYPE: '{}:decimal'.format(Prefix.XSD.prefix)})
        requested_value_node.text = str(requested_numeric_value)
        method = 'SetValue'
        return self._mk_setmethod_envelope(to, port_type, method,
                                           operation_handle,
                                           [requested_value_node],
                                           additional_namespaces=[Prefix.XSD])

    def mk_requestedstring_envelope(self, to, port_type, operation_handle, requested_string):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param operation_handle: the handle of operation that is called
        :param requested_string: a string
        :return: a SoapEnvelope
        """
        requested_string_node = etree_.Element(msgTag('RequestedStringValue'),
                                               attrib={QN_TYPE: '{}:string'.format(Prefix.XSD.prefix)})
        requested_string_node.text = requested_string
        method = 'SetString'
        return self._mk_setmethod_envelope(to, port_type, method, operation_handle, [requested_string_node],
                                           additional_namespaces=[Prefix.XSD])

    def mk_setalert_envelope(self, to, port_type, operation_handle, proposed_alert_states):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param operation_handle: the handle of operation that is called
        :param proposed_alert_states: a list of AbstractAlertStateContainer or derived class
        :return: a SoapEnvelope
        """
        _proposed_states = [p.mkCopy() for p in proposed_alert_states]
        for p in _proposed_states:
            p.nsmapper = DocNamespaceHelper()  # use my namespaces
        _proposed_state_nodes = [p.mkStateNode(msgTag('ProposedAlertState')) for p in _proposed_states]
        method = 'SetAlertState'
        return self._mk_setmethod_envelope(to, port_type, method, operation_handle, _proposed_state_nodes)

    def mk_setmetricstate_envelope(self, to, port_type, operation_handle, proposed_metric_states):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param operation_handle: the handle of operation that is called
        :param proposed_metric_states: a list of AbstractMetricStateContainer or derived class
        :return: a SoapEnvelope
        """
        _proposed_states = [p.mkCopy() for p in proposed_metric_states]
        nsmapper = DocNamespaceHelper()
        for p in _proposed_states:
            p.nsmapper = nsmapper  # use my namespaces
        _proposed_state_nodes = [p.mkStateNode(msgTag('ProposedMetricState')) for p in _proposed_states]
        return self._mk_setmethod_envelope(to, port_type, 'SetMetricState', operation_handle, _proposed_state_nodes)

    def mk_setcomponentstate_envelope(self, to, port_type, operation_handle, proposed_component_states):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param operation_handle: the handle of operation that is called
        :param proposed_component_states: a list of AbstractComponentStateContainers or derived class
        :return: a SoapEnvelope
        """
        _proposed_states = [p.mkCopy() for p in proposed_component_states]
        nsmapper = DocNamespaceHelper()
        for p in _proposed_states:
            p.nsmapper = nsmapper  # use my namespaces
        _proposed_state_nodes = [p.mkStateNode(msgTag('ProposedComponentState')) for p in _proposed_states]
        return self._mk_setmethod_envelope(to, port_type, 'SetComponentState', operation_handle, _proposed_state_nodes)

    def mk_setcontextstate_envelope(self, to, port_type, operation_handle, proposed_context_states):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param operation_handle: the handle of operation that is called
        :param proposed_context_states: a list of AbstractContextStateContainers or derived class
        :return: a SoapEnvelope
        """
        _proposed_states = [p.mkCopy() for p in proposed_context_states]
        for p in _proposed_states:
            # BICEPS: if handle == descriptorHandle, it means insert.
            if p.Handle is None:
                p.Handle = p.DescriptorHandle
            p.nsmapper = DocNamespaceHelper()  # use my namespaces
        _proposed_state_nodes = [p.mkStateNode(msgTag('ProposedContextState')) for p in _proposed_states]

        return self._mk_setmethod_envelope(to, port_type, 'SetContextState', operation_handle, _proposed_state_nodes)

    def mk_activate_envelope(self, to, port_type, operation_handle, value):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param operation_handle: the handle of operation that is called
        :param value: a string used as argument
        :return: a SoapEnvelope
        """
        body_node = etree_.Element(msgTag('Activate'), attrib=None, nsmap=nsmap)
        ref = etree_.SubElement(body_node, msgTag('OperationHandleRef'))
        ref.text = operation_handle
        argument_node = None
        if value is not None:
            argument_node = etree_.SubElement(body_node, msgTag('Argument'))
            arg_val = etree_.SubElement(argument_node, msgTag('ArgValue'))
            arg_val.text = value
        # TODO: add argument_node to soap envelope somehow
        # look for safety context in mdib
        sih = self._mk_optional_safetyheader(body_node, operation_handle)
        if sih is not None:
            sih = [sih]
        tmp = etree_.tostring(body_node)
        soap_envelope = self._mk_soapenvelope(to, port_type, 'Activate', tmp, additional_headers=sih)
        return soap_envelope

    def mk_getlocalizedtext_envelope(self, to, port_type, refs=None, version=None, langs=None,
                                     text_widths=None, number_of_lines=None):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param refs: a list of strings or None
        :param version: an unsigned integer or None
        :param langs: a list of strings or None
        :param text_widths: a list of strings or None (each string one of xs, s, m, l, xs, xxs)
        :param number_of_lines: a list of unsigned integers or None
        :return: a SoapEnvelope
        """
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
            for lang in langs:
                node = etree_.Element(msgTag('Lang'))
                node.text = lang
                requestparams.append(node)
        if text_widths is not None:
            for tw in text_widths:
                node = etree_.Element(msgTag('TextWidth'))
                node.text = tw
                requestparams.append(node)
        if number_of_lines is not None:
            for nol in number_of_lines:
                node = etree_.Element(msgTag('NumberOfLines'))
                node.text = nol
                requestparams.append(node)
        method = 'GetLocalizedText'
        return self._mk_get_method_envelope(to, port_type, method, params=requestparams)

    def mk_getsupportedlanguages_envelope(self, to, port_type):
        """
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :return: a SoapEnvelope
        """
        method = 'GetSupportedLanguages'
        return self._mk_get_method_envelope(to, port_type, method)

    def _mk_get_method_envelope(self, to, port_type, method_name, params=None):
        body_node = etree_.Element(msgTag(method_name))
        soap_envelope = soapenvelope.Soap12Envelope(Prefix.partialMap(Prefix.S12, Prefix.WSA, Prefix.MSG))
        action_string = self.get_action_string(port_type, method_name)
        soap_envelope.setAddress(soapenvelope.WsAddress(action=action_string, to=to))
        if params:
            for p in params:
                body_node.append(p)
        soap_envelope.addBodyObject(soapenvelope.GenericNode(body_node))
        return soap_envelope

    def _mk_setmethod_envelope(self, to, port_type, method_name, operation_handle, request_nodes,
                               additional_namespaces=None):
        """ helper to create the soap envelope
        :param to: to-field value in address
        :param port_type: needed to construct the action string
        :param method_name: last element of name of the called action
        :param operation_handle: handle name as string
        :param request_nodes: a list of etree_ nodes that will become sub-element of Method name element
        """
        body_node = etree_.Element(msgTag(method_name))
        ref = etree_.SubElement(body_node, msgTag('OperationHandleRef'),
                                attrib={QN_TYPE: '{}:HandleRef'.format(Prefix.PM.prefix)},
                                nsmap=Prefix.partialMap(Prefix.PM))
        ref.text = operation_handle
        for n in request_nodes:
            body_node.append(n)
        if additional_namespaces:
            my_ns = Prefix.partialMap(Prefix.S12, Prefix.WSA, Prefix.PM, Prefix.MSG, *additional_namespaces)
        else:
            my_ns = Prefix.partialMap(Prefix.S12, Prefix.WSA, Prefix.PM, Prefix.MSG)

        sih = self._mk_optional_safetyheader(body_node, operation_handle)  # a header or None

        soap_envelope = soapenvelope.Soap12Envelope(my_ns)
        action_string = self.get_action_string(port_type, method_name)
        soap_envelope.setAddress(soapenvelope.WsAddress(action=action_string, to=to))
        if sih is not None:
            soap_envelope.addHeaderObject(sih)

        soap_envelope.addBodyElement(body_node)
#         soap_envelope.validateBody(self._bmmSchema)
        return soap_envelope

    def _mk_optional_safetyheader(self, body_node, operation_handle):

        if self._mdib_wref is not None:
            op_descriptor = self._mdib_wref().descriptions.handle.getOne(operation_handle, allowNone=True)
            if op_descriptor is not None and op_descriptor.SafetyReq is not None:
                mdib_node = self._mdib_wref().reconstructMdibWithContextStates()
                return self._mk_safetyheader(body_node, op_descriptor.SafetyReq, mdib_node)
        return None

    def _mk_safetyheader(self, body_node, t_safety_req, mdib_node):
        dualchannel_selectors = {}
        safetycontext_selectors = {}

        if not t_safety_req.DualChannelDef:
            self._logger.info('no DualChannel selectors specified')
        else:
            for sel in t_safety_req.DualChannelDef.Selector:
                selector_id = sel.Id
                selector_path = sel.text
                values = body_node.xpath(selector_path, namespaces=mdib_node.nsmap)
                if len(values) == 1:
                    self._logger.debug('DualChannel selector "{}": value = "{}", path= "{}"',
                                       selector_id, values[0], selector_path)
                    dualchannel_selectors[selector_id] = str(values[0]).strip()
                elif len(values) == 0:
                    self._logger.error('DualChannel selector "{}": no value found! path= "{}"',
                                       selector_id, selector_path)
                else:
                    self._logger.error('DualChannel selector "{}": path= "{}", multiple values found: {}',
                                       selector_id, selector_path, values)

        if not t_safety_req.SafetyContextDef:
            self._logger.info('no Safety selectors specified')
        else:
            for sel in t_safety_req.SafetyContextDef.Selector:
                selector_id = sel.Id
                selector_path = sel.text
                # check the selector, there is a potential problem with the starting point of the xpath search path:
                if selector_path.startswith('//'):
                    # double slashes means that the matching pattern can be located anywhere in the dom tree.
                    # No problem.
                    pass
                elif selector_path.startswith('/'):
                    # Problem! if the selector starts with a single slash, this is a xpath search that starts
                    # at the document root.
                    # But the convention is that the xpath search shall start from the top level element
                    # (=> without the toplevel element in the path)
                    # In order to follow this convention, remove the leading slash and start the search
                    # relative to the lop level node.
                    selector_path = selector_path[1:]
                values = mdib_node.xpath(selector_path, namespaces=mdib_node.nsmap)
                if len(values) == 1:
                    self._logger.debug('Safety selector "{}": value = "{}"  path= "{}"',
                                       selector_id, values[0], selector_path)
                    safetycontext_selectors[selector_id] = str(values[0]).strip()
                elif len(values) == 0:
                    self._logger.error('Safety selector "{}":  no value found! path= "{}"', selector_id, selector_path)
                else:
                    self._logger.error('Safety selector "{}": path= "{}", multiple values found: {}',
                                       selector_id, selector_path, values)

        if dualchannel_selectors or safetycontext_selectors:
            return SafetyInfoHeader(dualchannel_selectors, safetycontext_selectors)
        else:
            return None

    def get_action_string(self, port_type, method_name):
        actions_lookup = self._sdc_definitions.Actions
        try:
            return getattr(actions_lookup, method_name)
        except AttributeError:  # fallback, if a definition is missing
            return '{}/{}/{}'.format(self._sdc_definitions.ActionsNamespace, port_type, method_name)

    def _mk_soapenvelope(self, to, port_type, method_name, xml_body_string=None, additional_headers=None):
        action = self.get_action_string(port_type, method_name)
        envelope = soapenvelope.Soap12Envelope(Prefix.partialMap(Prefix.S12, Prefix.MSG, Prefix.WSA))
        envelope.setAddress(soapenvelope.WsAddress(action=action, to=to))
        if additional_headers is not None:
            for h in additional_headers:
                envelope.addHeaderObject(h)
        if xml_body_string is not None:
            envelope.addBodyString(xml_body_string)
        return envelope


def _handles2params(handles):
    """
    Internal helper, converts handles to dom elements
    :param handles: a list of strings
    :return: a list of etree nodes
    """
    params = []
    if handles is not None:
        for h in handles:
            node = etree_.Element(msgTag('HandleRef'))
            node.text = h
            params.append(node)
    return params
