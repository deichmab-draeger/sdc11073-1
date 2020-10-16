import unittest
from sdc11073.pmtypes import LocalizedText
from sdc.biceps.localizedtext_pb2 import LocalizedTextMsg
from sdc11073.transport.protobuf.mapping import basemapper

class TestBaseMapper(unittest.TestCase):

    def test_localized_text(self):
        l_min = LocalizedText('foo')
        l_max = LocalizedText('foo', lang='de_eng', ref='abc', version=42, textWidth='l')
        for l in l_min, l_max:
            p = LocalizedTextMsg()
            basemapper.localizedtext_to_p(l, p)
            l2 = basemapper.localizedtext_from_p(p)
            self.assertEqual(l, l2)