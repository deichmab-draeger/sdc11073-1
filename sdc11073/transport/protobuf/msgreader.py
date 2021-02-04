from typing import List
from sdc11073.mdib.descriptorcontainers import AbstractDescriptorContainer
from .mapping import descriptorsmapper as dm
from .mapping import statesmapper as sm


class MdibStructureError(Exception):
    pass


class MessageReader(object):
    """ This class does all the conversions from protobuf messages to MDIB objects."""
    def __init__(self, logger, log_prefix=''):
        self._logger = logger
        self._log_prefix = log_prefix

    @staticmethod
    def _read_abstract_complex_device_component_descriptor_children(p_descr, mdib):
        ret = []
        p_acdcd = p_descr.abstract_complex_device_component_descriptor
        parent_handle = p_acdcd.abstract_device_component_descriptor.abstract_descriptor.a_handle
        if p_acdcd.HasField('alert_system'):
            p_alert_system = p_acdcd.alert_system
            alert_system_descriptor = dm.generic_descriptor_from_p(
                p_alert_system, parent_handle, mdib.nsmapper)
            ret.append(alert_system_descriptor)
            for p_alert_condition in p_alert_system.alert_condition:
                alert_condition = dm.generic_descriptor_from_p(
                    p_alert_condition, alert_system_descriptor.Handle, mdib.nsmapper)
                ret.append(alert_condition)
            for p_alert_signal in p_alert_system.alert_signal:
                alert_condition = dm.generic_descriptor_from_p(
                    p_alert_signal, alert_system_descriptor.Handle, mdib.nsmapper)
                ret.append(alert_condition)
        if p_acdcd.HasField('sco'):
            p_sco = p_acdcd.sco
            sco_descriptor = dm.generic_descriptor_from_p(p_sco, parent_handle, mdib.nsmapper)
            ret.append(sco_descriptor)
            for p_operation in p_sco.operation:
                alert_condition = dm.generic_descriptor_from_p(
                    p_operation, sco_descriptor.Handle, mdib.nsmapper)
                ret.append(alert_condition)
        return ret

    def readMdDescription(self, p_md_description_msg, mdib) -> List[AbstractDescriptorContainer]:
        ret = []
        for p_mds in p_md_description_msg.mds:
            parent_handle = None
            mds = dm.generic_descriptor_from_p(p_mds, parent_handle, mdib.nsmapper)
            ret.append(mds)
            for p_vmd in p_mds.vmd:
                vmd = dm.generic_descriptor_from_p(p_vmd, mds.Handle, mdib.nsmapper)
                ret.append(vmd)
                ret.extend(self._read_abstract_complex_device_component_descriptor_children(p_vmd, mdib))
                for p_channel in p_vmd.channel:
                    channel = dm.generic_descriptor_from_p(p_channel, vmd.Handle, mdib.nsmapper)
                    ret.append(channel)
                    for p_metric in p_channel.metric:
                        metric = dm.generic_descriptor_from_p(p_metric, channel.Handle, mdib.nsmapper)
                        ret.append(metric)
            if p_mds.HasField('system_context'):
                p_system_context = p_mds.system_context
                system_context = dm.generic_descriptor_from_p(p_system_context, mds.Handle, mdib.nsmapper)
                ret.append(system_context)
                for p_child_list in (p_system_context.ensemble_context,
                                     p_system_context.means_context, p_system_context.operator_context,
                                     p_system_context.workflow_context):
                    for p_child in p_child_list:
                        child_descr = dm.generic_descriptor_from_p(p_child, system_context.Handle, mdib.nsmapper)
                        ret.append(child_descr)
                if p_system_context.HasField('location_context'):
                    location_context = dm.generic_descriptor_from_p(
                        p_system_context.location_context, system_context.Handle, mdib.nsmapper)
                    ret.append(location_context)
                if p_system_context.HasField('patient_context'):
                    patient_context = dm.generic_descriptor_from_p(
                        p_system_context.patient_context, system_context.Handle, mdib.nsmapper)
                    ret.append(patient_context)
            if p_mds.HasField('clock'):
                p_clock = p_mds.clock
                clock_descriptor = dm.generic_descriptor_from_p(p_clock, mds.Handle, mdib.nsmapper)
                ret.append(clock_descriptor)
            ret.extend(self._read_abstract_complex_device_component_descriptor_children(p_mds, mdib))
        return ret

    # def readMdState(self, p_md_state, mdib):
    #     ret = []
    #     for p_abstract_state in p_md_state.state:
    #         p_state = sm.find_one_of_state(p_abstract_state)
    #         descr_handle = sm.p_get_value(p_state, 'DescriptorHandle')
    #         descr = mdib.descriptions.handle.getOne(descr_handle)
    #         state = sm.generic_state_from_p(p_state, mdib.nsmapper, descr)
    #         ret.append(state)
    #
    #     return ret

    # def read_abstract_states(self, p_abstract_states, mdib):
    #     states = [sm.find_one_of_state(tmp) for tmp in p_abstract_states]
    #     return self.read_states(states, mdib)

    @staticmethod
    def read_states(p_states, mdib):
        ret = []
        for p_state in p_states:
            descr_handle = sm.p_get_value(p_state, 'DescriptorHandle')
            descr = mdib.descriptions.handle.getOne(descr_handle)
            state = sm.generic_state_from_p(p_state, mdib.nsmapper, descr)
            ret.append(state)
        return ret

    @staticmethod
    def read_descriptors(p_descriptors, parent_handle,  mdib):
        ret = []
        for p_descr in p_descriptors:
            descr = dm.generic_descriptor_from_p(p_descr, parent_handle, mdib.nsmapper)
            ret.append(descr)
        return ret
