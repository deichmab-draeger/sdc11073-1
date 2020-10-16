from sdc11073.pmtypes import LocalizedText
from sdc.biceps.localizedtext_pb2 import LocalizedTextMsg
from sdc.biceps.localizedtextwidth_pb2 import LocalizedTextWidthMsg
from google.protobuf.wrappers_pb2 import StringValue, UInt64Value, Int64Value


def string_value_to_p(s: str, p_string_value: StringValue) -> None:
    """modify protobuf StringValue inline """
    if s is not None:
        p_string_value.value = s

def string_value_from_p(p_string_value: StringValue) -> (str, None):
    """read protobuf StringValue """
    return None if not p_string_value.value else p_string_value.value


def int_value_to_p(i: int, p_int_value: [UInt64Value, Int64Value], implied_value:int=None) -> None:
    """modify protobuf int value inline """
    if i is not None:
        p_int_value.value = i
    elif implied_value is not None:
        p_int_value.value = implied_value


def int_value_from_p(p_int_value: [UInt64Value, Int64Value], implied_value:int=None) -> (int, None):
    """read protobuf IntValue
    """
    if implied_value is None:
        return p_int_value.value
    else:
        return None if p_int_value.value == implied_value else p_int_value.value


def enum_to_p(s: str, p_enum) -> None:
    """modify protobuf StringValue inline """
    if s is not None:
        e = p_enum.EnumType.Value(s)
        p_enum.enum_value = e


def enum_from_p(p_enum) -> str:
    """read protobuf enum StringValue """
    return p_enum.EnumType.Name(p_enum.enum_value)


def localizedtext_to_p(localized_text: LocalizedText, p: LocalizedTextMsg) -> LocalizedTextMsg:
    p.string = localized_text.text
    if localized_text.Lang:
        string_value_to_p(localized_text.Lang, p.a_lang)
    if localized_text.Ref:
        string_value_to_p(localized_text.Ref, p.a_ref)
    if localized_text.Version:
        int_value_to_p(localized_text.Version, p.a_version, 0)
    if localized_text.TextWidth:
        enum_to_p(localized_text.TextWidth.upper(), p.a_text_width)
    return p


def localizedtext_from_p(localized_text_msg: LocalizedTextMsg) -> LocalizedText:
    ret = LocalizedText(None)
    ret.text = localized_text_msg.string
    if localized_text_msg.HasField('a_lang'):
        ret.Lang = string_value_from_p(localized_text_msg.a_lang)
    if localized_text_msg.HasField('a_ref'):
        ret.Ref = string_value_from_p(localized_text_msg.a_ref)
    if localized_text_msg.HasField('a_version'):
        ret.Version = int_value_from_p(localized_text_msg.a_version, 0)
    if localized_text_msg.HasField('a_text_width'):
        ret.TextWidth = enum_from_p(localized_text_msg.a_text_width).lower()
    return ret
