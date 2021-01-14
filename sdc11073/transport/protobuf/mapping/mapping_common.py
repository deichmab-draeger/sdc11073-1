from org.somda.sdc.proto.model.biceps.localizedtext_pb2 import LocalizedTextMsg
from sdc11073.mdib.containerproperties import NodeAttributeProperty, NodeAttributeListProperty

def name_to_p(name):
    """construct the protobuf member name from biceps name"""
    if name.endswith('Container'):
        name = name[:-9]
    if name.startswith('_'):
        name = name[1:]
    tmp = []
    tmp.append(name[0])
    for c in name[1:]:
        if c.isupper() and tmp[-1].islower():
            tmp.append('_')
        tmp.append(c)
    return ''.join(tmp).lower()


def attr_name_to_p(name):
    """ biceps attributes have a a_ prefix in protobuf"""
    return 'a_' + name_to_p(name)


def p_name_from_pm_name(p, pm_cls, pm_name):
    dest_type = getattr(pm_cls, pm_name)
    # determine member name in p:
    if pm_name == 'text' and isinstance(p, LocalizedTextMsg):
        p_name = 'string'
    elif pm_name == 'ext_Extension':
        p_name = 'element1'
    else:
        if isinstance(dest_type, (NodeAttributeProperty, NodeAttributeListProperty)):
            p_name = attr_name_to_p(pm_name)
        else:
            p_name = name_to_p(pm_name)
    return p_name
