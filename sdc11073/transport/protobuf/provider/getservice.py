import logging
import traceback
from collections import namedtuple
import grpc

from org.somda.sdc.proto.model import sdc_services_pb2_grpc
from org.somda.sdc.proto.model.sdc_messages_pb2 import GetMdibResponse, GetMdDescriptionResponse, GetMdStateResponse

from org.somda.sdc.proto.model.biceps.mdib_pb2 import MdibMsg
from org.somda.sdc.proto.model.biceps.mddescription_pb2 import MdDescriptionMsg

from sdc11073.namespaces import domTag
from sdc11073.transport.protobuf.mapping import descriptorsmapper as dm
from sdc11073.transport.protobuf.mapping import statesmapper as sm

_StackEntry = namedtuple('Stackentry', 'src dest')


def _alert_system_all_to_p(mdib, alert_system_descr, p_parent):
    if alert_system_descr.NODETYPE != domTag('AlertSystemDescriptor'):
        raise ValueError('wrong NodeType')
    dm.generic_descriptor_to_p(alert_system_descr, p_parent.abstract_complex_device_component_descriptor.alert_system)
    dest_alert_system = p_parent.abstract_complex_device_component_descriptor.alert_system
    src_as_children = mdib.descriptions.parentHandle.get(alert_system_descr.Handle)
    for src_as_child in src_as_children:
        # dest_as_child = dm.generic_descriptor_to_p(src_as_child, None)
        if src_as_child.NODETYPE == domTag('AlertSignalDescriptor'):
            dest_as_child = dest_alert_system.alert_signal.add()
            dm.generic_descriptor_to_p(src_as_child, dest_as_child)
            #dest_alert_system.alert_signal.append(dest_as_child)
            src_asd_children = mdib.descriptions.parentHandle.get(src_as_child.Handle, [])
            for src_asd_child in src_asd_children:
                raise RuntimeError(f'handling of {src_asd_child.NODETYPE.localname} not implemented')
        elif src_as_child.NODETYPE in (domTag('AlertConditionDescriptor'), domTag('LimitAlertConditionDescriptor')):
            dest_as_child = dest_alert_system.alert_condition.add()
            dm.generic_descriptor_to_p(src_as_child, dest_as_child)
            # dest_alert_system.alert_condition.append(dest_as_child)
            src_asd_children = mdib.descriptions.parentHandle.get(src_as_child.Handle, [])
            for src_asd_child in src_asd_children:
                raise RuntimeError(
                    f'handling of {src_asd_child.NODETYPE.localname} not implemented')
        else:
            raise RuntimeError(f'handling of {src_as_child.NODETYPE.localname} not implemented')


def _sco_all_to_p(mdib, sco_descr, p_parent):
    dm.generic_descriptor_to_p(sco_descr,
                               p_parent.abstract_complex_device_component_descriptor.sco)
    src_sco_children = mdib.descriptions.parentHandle.get(sco_descr.Handle, [])
    dest_sco = p_parent.abstract_complex_device_component_descriptor.sco
    for src_sco_child in src_sco_children:
        # dest_sco_child = dm.generic_descriptor_to_p(src_sco_child, None)
        # dest_sco.operation.append(dest_sco_child)
        dest_sco_child = dest_sco.operation.add()
        dm.generic_descriptor_to_p(src_sco_child, dest_sco_child)


def _mdib_to_p(mdib, p_mds_list, p_state_list):
    #mds_dest = get_mdib_response.payload.mdib.md_description.mds
    src_mds_list = mdib.descriptions.NODETYPE.get(domTag('MdsDescriptor'))
    for scr_mds in src_mds_list:
        p_mds = p_mds_list.add()  # this creates a new entry in list with correct type
        _mds_to_p(mdib, scr_mds, p_mds)
    _md_state_to_p(mdib.states.objects, p_state_list)
    # for stateContainer in mdib.states.objects:
    #     abstract_state_one_of_msg = p_state_list.add()
    #     sm.generic_state_to_p(stateContainer, abstract_state_one_of_msg)


def _md_state_to_p(state_container_list, p_state_list):
    for stateContainer in state_container_list: #mdib.states.objects:
        abstract_state_one_of_msg = p_state_list.add()
        sm.generic_state_to_p(stateContainer, abstract_state_one_of_msg)


def _mds_to_p(mdib, scr_mds, p_mds):
    """ reconstruct single mds """
    dm.generic_descriptor_to_p(scr_mds, p_mds)
    # children of mds (vmd, alertsystem, sco, ...)
    mds_children = mdib.descriptions.parentHandle.get(scr_mds.Handle, [])
    for mds_child in mds_children:  # e.g. vmd, sco, alertsystem,...
        if mds_child.NODETYPE == domTag('VmdDescriptor'):
            src_vmd = mds_child  # give it a better name for code readability
            dest_vmd = p_mds.vmd.add()
            dm.generic_descriptor_to_p(src_vmd, dest_vmd)
            # p_mds.vmd.append(dest_vmd)
            src_vmd_children = mdib.descriptions.parentHandle.get(src_vmd.Handle, [])
            for src_vmd_child in src_vmd_children:
                if src_vmd_child.NODETYPE == domTag('ChannelDescriptor'):
                    dest_vmd_child = dest_vmd.channel.add()
                    dm.generic_descriptor_to_p(src_vmd_child, dest_vmd_child)
                    # dest_vmd.channel.append(dest_vmd_child)
                    src_channel_children = mdib.descriptions.parentHandle.get(src_vmd_child.Handle, [])
                    for src_channel_child in src_channel_children:
                        # children of channels are always metrics
                        dest_metric = dest_vmd_child.metric.add()
                        dm.generic_descriptor_to_p(src_channel_child, dest_metric)
                        # dest_vmd_child.metric.append(dest_metric)
                elif src_vmd_child.NODETYPE == domTag('ScoDescriptor'):
                    dest_sco = dest_vmd.abstract_complex_device_component_descriptor.sco
                    _sco_all_to_p(mdib, src_vmd_child, dest_vmd)
                elif src_vmd_child.NODETYPE == domTag('AlertSystemDescriptor'):
                    _alert_system_all_to_p(mdib, src_vmd_child, dest_vmd)
                else:
                    raise RuntimeError(f'handling of {src_vmd_child.NODETYPE.localname} not implemented')
        elif mds_child.NODETYPE == domTag('AlertSystemDescriptor'):
            _alert_system_all_to_p(mdib, mds_child, p_mds)
        elif mds_child.NODETYPE == domTag('ScoDescriptor'):
            _sco_all_to_p(mdib, mds_child, p_mds)
        elif mds_child.NODETYPE == domTag('SystemContextDescriptor'):
            src_sc = mds_child  # give it a better name for code readability
            dm.generic_descriptor_to_p(src_sc,
                                       p_mds.system_context)
            src_sc_children = mdib.descriptions.parentHandle.get(src_sc.Handle, [])
            for src_sc_child in src_sc_children:
                p = dm.generic_descriptor_to_p(src_sc_child, None)
                if src_sc_child.NODETYPE == domTag('PatientContextDescriptor'):
                    dm.generic_descriptor_to_p(src_sc_child, p_mds.system_context.patient_context)
                elif src_sc_child.NODETYPE == domTag('LocationContextDescriptor'):
                    dm.generic_descriptor_to_p(src_sc_child, p_mds.system_context.location_context)
                else:
                    p = dm.generic_descriptor_to_p(src_sc_child, None)
                    if src_sc_child.NODETYPE == domTag('EnsembleContextDescriptor'):
                        p_mds.system_context.ensemble_context.append(p)
                    elif src_sc_child.NODETYPE == domTag('MeansContextDescriptor'):
                        p_mds.system_context.means_context.append(p)
                    elif src_sc_child.NODETYPE == domTag('OperatorContextDescriptor'):
                        p_mds.system_context.operator_context.append(p)
                    elif src_sc_child.NODETYPE == domTag('WorkflowContextDescriptor'):
                        p_mds.system_context.workflow_context.append(p)
                    else:
                        raise RuntimeError(
                            f'handling of {src_sc_child.NODETYPE.localname} not implemented')
        elif mds_child.NODETYPE == domTag('ClockDescriptor'):
            src_clock = mds_child  # give it a better name for code readability
            dm.generic_descriptor_to_p(src_clock,
                                       p_mds.clock)
            src_clk_children = mdib.descriptions.parentHandle.get(src_clock.Handle, [])
            for src_clk_child in src_clk_children:
                raise RuntimeError(
                    f'handling of {src_clk_child.NODETYPE.localname} not implemented')
        else:
            raise RuntimeError(f'handling of {mds_child.NODETYPE.localname} not implemented')


class GetService(sdc_services_pb2_grpc.GetServiceServicer):

    def __init__(self, mdib):
        super().__init__()
        self._mdib = mdib
        self._logger = logging.getLogger('pysdc.grpc.dev.GetService')

    def GetMdib(self, request, context):
        try:
            response = GetMdibResponse()
            _mdib_to_p(self._mdib, response.payload.mdib.md_description.mds, response.payload.mdib.md_state.state)
            response.payload.mdib.a_mdib_version_group.a_mdib_version.value = self._mdib.mdibVersion
            response.payload.mdib.a_mdib_version_group.a_sequence_id = self._mdib.sequenceId
            return response
        except:
            print(traceback.format_exc())
            self._logger.error(traceback.format_exc())
            raise

    def GetMdDescription(self, request, context):
        try:
            response = GetMdDescriptionResponse()
            p_mds_list = response.payload.md_description.mds
            src_mds_list = self._mdib.descriptions.NODETYPE.get(domTag('MdsDescriptor'))
            for scr_mds in src_mds_list:
                p_mds = p_mds_list.add()  # this creates a new entry in list with correct type
                _mds_to_p(self._mdib, scr_mds, p_mds)
            return response
        except:
            print(traceback.format_exc())
            self._logger.error(traceback.format_exc())
            raise

    def GetMdState(self, request, context):
        try:
            requested_handles = request.payload.handle_ref
            if not requested_handles:
                states = self._mdib.states.objects
            else:
                states = [self._mdib.states.descriptorHandle.getOne(h) for h in requested_handles]
            response = GetMdStateResponse()
            _md_state_to_p(states, response.payload.md_state.state)
            return response
        except:
            print(traceback.format_exc())
            self._logger.error(traceback.format_exc())
            raise
