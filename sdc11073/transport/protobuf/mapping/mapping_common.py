import inspect
import traceback
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


def find_populated_one_of(p, oneof_fields_lookup):
    """This function recursively checks all one_of fields for content
     It returns the deepest nested field it can find.
     The lookup is a dictionary with a Msg class as key and a list of the names of its one-of fields as value."""
    one_of_names = oneof_fields_lookup.get(p.__class__)
    if one_of_names:
        for n in one_of_names:
            if p.HasField(n):
                tmp = getattr(p, n)
                return find_populated_one_of(tmp, oneof_fields_lookup)
        raise ValueError(f'{p.__class__.__name__} has no active field!')
    else:
        return p


def find_one_of_p_for_container(container, one_of_p):#, child_classes_lookup):
    """Returns the correct field for a container class inside a one_of_p message"""
#    if container.__class__ not in child_classes_lookup:
#        # this is not a one-of class
#        return one_of_p
    classes = [ c for c in inspect.getmro(container.__class__) if not c.__name__.startswith('_')]
    classes.reverse()
    del classes[0]  # object
    start_cls = None
    while classes:
        cls = classes[0]
        name = cls.__name__
        if name.endswith('Container'):
            name = name[:-9]
        if one_of_p.__class__.__name__.startswith(name):
            start_cls = cls
            break
        else:
            del classes[0]
    if start_cls is None:
        raise ValueError(f'could not match {container.__class__.__name__} and {p.__class__.__name__}')
    tmp = one_of_p
    if len(classes) > 1:
        del classes[0]
    try:
        for cls in classes:
#            child_classes = child_classes_lookup.get(cls)
            p_member_name = name_to_p(cls.__name__)
            if cls is not classes[-1]:
                tmp = getattr(tmp, p_member_name + '_one_of')
            elif cls is classes[-1]:
                if tmp.__class__.__name__.endswith('OneOfMsg'):
                    if hasattr(tmp, p_member_name + '_one_of'):
                        tmp = getattr(tmp, p_member_name + '_one_of')
                    tmp = getattr(tmp, p_member_name)
        return tmp
    except:
        print(traceback.format_exc())
        raise
