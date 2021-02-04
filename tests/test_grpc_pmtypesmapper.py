import unittest
import logging
import time
from math import isclose
from decimal import Decimal
from sdc11073 import pmtypes
from sdc11073.namespaces import nsmap, domTag
from sdc11073.transport.protobuf.mapping import pmtypesmapper

def diff(a: pmtypes.PropertyBasedPMType, b:pmtypes.PropertyBasedPMType) ->dict:
    ret = {}
    for name, dummy in a._sortedContainerProperties():
        try:
            a_value = getattr(a, name)
            b_value = getattr(b, name)
            if a_value == b_value:
                continue
            elif (isinstance(a_value, float) or isinstance(b_value, float)) and isclose(a_value, b_value):
                continue  # float compare (almost equal)
            else:
                ret[name] = (a_value, b_value)
        except (TypeError, AttributeError) as ex:
            ret[name] = ex
    return ret

def _start_logger():
    logger = logging.getLogger('pysdc.grpc.map')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return ch

def _stop_logger(handler):
    logger = logging.getLogger('pysdc.grpc')
    logger.setLevel(logging.WARNING)
    logger.removeHandler(handler)


class TestPmtypesMapper(unittest.TestCase):
    def setUp(self) -> None:
        self._log_handler = _start_logger()

    def tearDown(self) -> None:
        _stop_logger(self._log_handler)

    def check_convert(self,obj):
        obj_p = pmtypesmapper.generic_to_p(obj, None)
        print('\n################################# generic_from_p##################')
        obj2 = pmtypesmapper.generic_from_p(obj_p)
        delta = diff(obj, obj2)
        self.assertEqual(obj, obj2)

    def test_localized_text(self):
        l_min = pmtypes.LocalizedText('foo')
        l_max = pmtypes.LocalizedText('foo', lang='de_eng', ref='abc', version=42, textWidth='l')
        for obj in l_min, l_max:
            self.check_convert(obj)

    def test_codedvalue(self):
        c_min = pmtypes.CodedValue(123)
        c_max = pmtypes.CodedValue(345, 'foo', '42',
                                   codingSystemNames=[pmtypes.LocalizedText('csn')],
                                   conceptDescriptions=[pmtypes.LocalizedText('cd')],
                                   symbolicCodeName='scn')
        c_max.Translation.append(pmtypes.T_Translation('code', 'codingsystem', codingSystemVersion='12'))
        for obj in c_min, c_max:
            self.check_convert(obj)

    def test_instance_identifier(self):
        inst_min = pmtypes.InstanceIdentifier('my_root')
        inst_max = pmtypes.InstanceIdentifier('my_root',
                                              pmtypes.CodedValue('abc', 'def'),
                                              [pmtypes.LocalizedText('xxx'), pmtypes.LocalizedText('yyy')],
                                              'ext_string')
        op_min = pmtypes.OperatingJurisdiction('my_root')
        op_max = pmtypes.OperatingJurisdiction('my_root',
                                              pmtypes.CodedValue('abc', 'def'),
                                              [pmtypes.LocalizedText('xxx'), pmtypes.LocalizedText('yyy')],
                                              'ext_string')

        for obj in (inst_max, inst_min, op_max, op_min):
            self.check_convert(obj)

    def test_range(self):
        rg_max = pmtypes.Range(Decimal('0'), Decimal('42'), Decimal('0.1'), Decimal('0.2'), Decimal('0.3'))
        rg_min = pmtypes.Range()
        for obj in (rg_max, rg_min):
            self.check_convert(obj)

    def test_measurement(self):
        obj = pmtypes.Measurement(Decimal('42'), pmtypes.CodedValue('abc'))
        self.check_convert(obj)

    def test_allowed_value(self):
        aw_max = pmtypes.AllowedValue('an_allowed_value', pmtypes.CodedValue('abc'))
        aw_min = pmtypes.AllowedValue('another_allowed_value')
        for obj in (aw_max, aw_min):
            self.check_convert(obj)

    def test_numericmetricvalue(self):
        n_min = pmtypes.NumericMetricValue()
        n_max = pmtypes.NumericMetricValue()
        n_max.DeterminationTime = 12345
        n_max.MetricQuality.Mode = 'Test'
        n_max.MetricQuality.Qi = Decimal('2.111')
        n_max.MetricQuality.Validity= 'Calib'
        n_max.StartTime = 999
        n_max.StopTime = 9999
        n_max.Value = Decimal('0.9')
        annot = pmtypes.Annotation(pmtypes.CodedValue('a','b'))
        n_max.Annotation.append(annot)
        for obj in n_max, n_min:
            self.check_convert(obj)

    def test_stringmetricvalue(self):
        s_min = pmtypes.StringMetricValue()
        s_max = pmtypes.StringMetricValue()
        s_max.DeterminationTime = 12345
        s_max.MetricQuality.Mode = pmtypes.GenerationMode.TEST
        s_max.MetricQuality.Qi = Decimal('2.111')
        s_max.MetricQuality.Validity= pmtypes.MeasurementValidity.CALIBRATION_ONGOING
        s_max.StartTime = 999
        s_max.StopTime = 9999
        s_max.Value = 'hey!'
        annot = pmtypes.Annotation(pmtypes.CodedValue('a','b'))
        s_max.Annotation.append(annot)
        for obj in s_max, s_min:
            self.check_convert(obj)


    def test_samplearrayvalue(self):
        s_min = pmtypes.SampleArrayValue()
        s_max = pmtypes.SampleArrayValue()
        s_max.DeterminationTime = 12345
        s_max.MetricQuality.Mode = pmtypes.GenerationMode.TEST
        s_max.MetricQuality.Qi = Decimal('2.111')
        s_max.StartTime = 999
        s_max.StopTime = 9999
        s_max.MetricQuality.Validity= 'Calib'
        s_max.Samples = [Decimal('1'), Decimal('2.2')]
        annot = pmtypes.Annotation(pmtypes.CodedValue('a','b'))
        s_max.Annotation.append(annot)
        apply_annot = pmtypes.ApplyAnnotation(1, 1)
        s_max.ApplyAnnotation.append(apply_annot)

        for obj in [s_max, s_min]:
            self.check_convert(obj)

    def test_cause_info(self):
        ci_max = pmtypes.CauseInfo(pmtypes.RemedyInfo([pmtypes.LocalizedText('rembla')]),
                                   [pmtypes.LocalizedText('caubla')])
        ci_min = pmtypes.CauseInfo(None, [])
        for obj in [ci_min, ci_max]:
            self.check_convert(obj)

    def test_argument(self):
        obj = pmtypes.ActivateOperationDescriptorArgument(pmtypes.CodedValue('aaa'), domTag('oh'))
        self.check_convert(obj)

    def test_physical_connector_info(self):
        pci_max = pmtypes.PhysicalConnectorInfo([pmtypes.LocalizedText('foo'), pmtypes.LocalizedText('bar')], 42)
        pci_min = pmtypes.PhysicalConnectorInfo([], None)
        for obj in (pci_max, pci_min):
            self.check_convert(obj)

    def test_system_signal_activation(self):
        obj = pmtypes.SystemSignalActivation('Aud', 'Psd')
        self.check_convert(obj)

    def test_production_specification(self):
        ps_min = pmtypes.ProductionSpecification(pmtypes.CodedValue('abc', 'def'), 'prod_spec')
        ps_max = pmtypes.ProductionSpecification(pmtypes.CodedValue('abc', 'def'), 'prod_spec',
                                                 pmtypes.InstanceIdentifier('my_root',
                                                                            pmtypes.CodedValue('xxx', 'yyy')))
        for obj in (ps_max, ps_min):
            self.check_convert(obj)

    def test_base_demographics(self):
        bd_max = pmtypes.BaseDemographics()
        bd_max.Givenname = 'Charles'
        bd_max.Middlename = ['M.']
        bd_max.Familyname = 'Schulz'
        bd_max.Birthname = 'Meyer'
        bd_max.Title = 'Dr.'
        bd_min = pmtypes.BaseDemographics()
        for obj in (bd_max, bd_min):
            self.check_convert(obj)

    def test_patient_demographics_core_data(self):
        bd_max = pmtypes.PatientDemographicsCoreData()
        bd_max.Givenname = 'Charles'
        bd_max.Middlename = ['M.']
        bd_max.Familyname = 'Schulz'
        bd_max.Birthname = 'Meyer'
        bd_max.Title = 'Dr.'
        bd_max.Sex = pmtypes.T_Sex.FEMALE
        bd_min = pmtypes.BaseDemographics()
        for obj in (bd_max, bd_min):
            self.check_convert(obj)

    def test_location_detail(self):
        loc_max = pmtypes.LocationDetail('poc', 'room', 'bed', 'facility', 'building', 'floor')
        loc_min = pmtypes.LocationDetail()
        for obj in (loc_max, loc_min):
            self.check_convert(obj)

    def test_location_reference(self):
        loc_max = pmtypes.LocationReference(identifications=[pmtypes.InstanceIdentifier('root'),
                                                             pmtypes.InstanceIdentifier('root2')],
                                            locationdetail=pmtypes.LocationDetail('poc', 'room', 'bed'))
        loc_min = pmtypes.LocationReference()
        for obj in (loc_max, loc_min):
            self.check_convert(obj)

    def test_person_reference(self):
        pr_max = pmtypes.PersonReference([pmtypes.InstanceIdentifier('root'), pmtypes.InstanceIdentifier('root2')],
                                         name=pmtypes.BaseDemographics('Charles', ['M.'], 'Schulz', 'Meyer', 'Dr.'))
        pr_min = pmtypes.PersonReference()
        for obj in (pr_max, pr_min):
            self.check_convert(obj)

    def test_person_participation(self):
        pp_max = pmtypes.PersonParticipation([pmtypes.InstanceIdentifier('root'), pmtypes.InstanceIdentifier('root2')],
                                             name=pmtypes.BaseDemographics('Charles', ['M.'], 'Schulz', 'Meyer', 'Dr.'),
                                             roles=[pmtypes.CodedValue('abc')])
        pp_min = pmtypes.PersonParticipation()
        for obj in (pp_max, pp_min):
            self.check_convert(obj)

    def test_person_reference_oneof(self):
        pr_max = pmtypes.PersonReference([pmtypes.InstanceIdentifier('root'), pmtypes.InstanceIdentifier('root2')],
                                         name=pmtypes.BaseDemographics('Charles', ['M.'], 'Schulz', 'Meyer', 'Dr.'))
        pp_max = pmtypes.PersonParticipation([pmtypes.InstanceIdentifier('root'), pmtypes.InstanceIdentifier('root2')],
                                             name=pmtypes.BaseDemographics('Charles', ['M.'], 'Schulz', 'Meyer', 'Dr.'),
                                             roles=[pmtypes.CodedValue('abc')])
        for obj in (pr_max, pp_max):
            self.check_convert(obj)

    def test_reference_range(self):
        rr_max = pmtypes.ReferenceRange(range=pmtypes.Range(Decimal('0.11'), 42), meaning=pmtypes.CodedValue('42'))
        rr_min = pmtypes.ReferenceRange(range=pmtypes.Range(0, 1))
        for obj in (rr_max, rr_min):
            self.check_convert(obj)

    def test_related_measurement(self):
        _rr1 = pmtypes.ReferenceRange(range=pmtypes.Range(Decimal('0.11'), 42), meaning=pmtypes.CodedValue('42'))
        _rr2 = pmtypes.ReferenceRange(range=pmtypes.Range(0, 1))
        rm_max = pmtypes.RelatedMeasurement(
            value=pmtypes.Measurement(42, pmtypes.CodedValue('abc')),
            reference_range=[_rr1, _rr2])
        rm_min = pmtypes.RelatedMeasurement(value=pmtypes.Measurement(1, pmtypes.CodedValue('def')))
        for obj in (rm_max, rm_min):
            self.check_convert(obj)

    def test_clinical_info(self):
        related_measurements = [
            pmtypes.RelatedMeasurement(pmtypes.Measurement(Decimal('42'), pmtypes.CodedValue('def'))),
            pmtypes.RelatedMeasurement(pmtypes.Measurement(Decimal('43'), pmtypes.CodedValue('xyz')))]
        ci_max = pmtypes.ClinicalInfo(
            typecode=pmtypes.CodedValue('abc'),
            descriptions=[pmtypes.LocalizedText('a', 'de'),
                          pmtypes.LocalizedText('b', 'en')],
            relatedmeasurements=related_measurements)
        ci_min = pmtypes.ClinicalInfo()
        for obj in (ci_max, ci_min):
            self.check_convert(obj)

    def test_imaging_procedure(self):
        imgp_max = pmtypes.ImagingProcedure(accessionidentifier=pmtypes.InstanceIdentifier('abc'),
                                            requestedprocedureid=pmtypes.InstanceIdentifier('abc'),
                                            studyinstanceuid=pmtypes.InstanceIdentifier('abc'),
                                            scheduledprocedurestepid=pmtypes.InstanceIdentifier('abc'),
                                            modality=pmtypes.CodedValue('333'),
                                            protocolcode=pmtypes.CodedValue('333'))
        imgp_min = pmtypes.ImagingProcedure(accessionidentifier=pmtypes.InstanceIdentifier('abc'),
                                            requestedprocedureid=pmtypes.InstanceIdentifier('abc'),
                                            studyinstanceuid=pmtypes.InstanceIdentifier('abc'),
                                            scheduledprocedurestepid=pmtypes.InstanceIdentifier('abc'))
        for obj in (imgp_max, imgp_min):
            self.check_convert(obj)

    def test_order_detail(self):
        _imgp_max = pmtypes.ImagingProcedure(accessionidentifier=pmtypes.InstanceIdentifier('abc'),
                                            requestedprocedureid=pmtypes.InstanceIdentifier('abc'),
                                            studyinstanceuid=pmtypes.InstanceIdentifier('abc'),
                                            scheduledprocedurestepid=pmtypes.InstanceIdentifier('abc'),
                                            modality=pmtypes.CodedValue('333'),
                                            protocolcode=pmtypes.CodedValue('333'))

        od_max = pmtypes.OrderDetail(
            start='2020-10-31',
            end='2020-11-01',
            performer=[pmtypes.PersonParticipation()],
            service=[pmtypes.CodedValue('abc')],
            imagingprocedure=[_imgp_max]
        )
        od_min = pmtypes.OrderDetail()
        for obj in (od_max, od_min):
            self.check_convert(obj)

    def test_requested_order_detail(self):
        _imgp_max = pmtypes.ImagingProcedure(accessionidentifier=pmtypes.InstanceIdentifier('abc'),
                                            requestedprocedureid=pmtypes.InstanceIdentifier('abc'),
                                            studyinstanceuid=pmtypes.InstanceIdentifier('abc'),
                                            scheduledprocedurestepid=pmtypes.InstanceIdentifier('abc'),
                                            modality=pmtypes.CodedValue('333'),
                                            protocolcode=pmtypes.CodedValue('333'))
        pr_max = pmtypes.PersonReference([pmtypes.InstanceIdentifier('root'), pmtypes.InstanceIdentifier('root2')],
                                         name=pmtypes.BaseDemographics('Charles', ['M.'], 'Schulz', 'Meyer', 'Dr.'))
        pr_max2 = pmtypes.PersonReference([pmtypes.InstanceIdentifier('root'),],
                                           name=pmtypes.BaseDemographics('Charles', ['M.'], 'Schulz', 'Meyer', 'Dr.'))

        od_max = pmtypes.RequestedOrderDetail(
            start='2020-10-31',
            end='2020-11-01',
            performer=[pmtypes.PersonParticipation()],
            service=[pmtypes.CodedValue('abc')],
            imagingprocedure=[_imgp_max],
            referringphysician=pr_max,
            requestingphysician=pr_max2,
            placerordernumber=pmtypes.InstanceIdentifier('root')
        )
        od_min = pmtypes.RequestedOrderDetail()
        for obj in (od_max, od_min):
            self.check_convert(obj)


    def test_performed_order_detail(self):
        _imgp_max = pmtypes.ImagingProcedure(accessionidentifier=pmtypes.InstanceIdentifier('abc'),
                                            requestedprocedureid=pmtypes.InstanceIdentifier('abc'),
                                            studyinstanceuid=pmtypes.InstanceIdentifier('abc'),
                                            scheduledprocedurestepid=pmtypes.InstanceIdentifier('abc'),
                                            modality=pmtypes.CodedValue('333'),
                                            protocolcode=pmtypes.CodedValue('333'))
        od_max = pmtypes.PerformedOrderDetail(
            start='2020-10-31',
            end='2020-11-01',
            performer=[pmtypes.PersonParticipation()],
            service=[pmtypes.CodedValue('abc')],
            imagingprocedure=[_imgp_max],
            fillerordernumber=pmtypes.InstanceIdentifier('abc'),
            resultingclinicalinfos=[pmtypes.ClinicalInfo(
                typecode=pmtypes.CodedValue('abc'),
                descriptions=[pmtypes.LocalizedText('a', 'de'),
                              pmtypes.LocalizedText('b', 'en')],
                relatedmeasurements=None
            )]
        )
        od_min = pmtypes.PerformedOrderDetail()
        for obj in (od_max, od_min):
            self.check_convert(obj)

    def test_workflow_detail(self):
        patient = pmtypes.PersonReference([pmtypes.InstanceIdentifier('root'), pmtypes.InstanceIdentifier('root2')],
                                          name=pmtypes.BaseDemographics('Charles', ['M.'], 'Schulz', 'Meyer', 'Dr.'))
        referring_physician = pmtypes.PersonReference(
            [pmtypes.InstanceIdentifier('root2')],
            name=pmtypes.BaseDemographics('Cindy', ['L.'], 'Miller', 'Meyer', 'Dr.'))
        requesting_physician = pmtypes.PersonReference(
            [pmtypes.InstanceIdentifier('root2')],
            name=pmtypes.BaseDemographics('Henry', ['L.'], 'Miller'))

        assigned_location = pmtypes.LocationReference(identifications=[pmtypes.InstanceIdentifier('root'),
                                                                       pmtypes.InstanceIdentifier('root2')],
                                                      locationdetail=pmtypes.LocationDetail('poc', 'room', 'bed'))
        visit_number = pmtypes.InstanceIdentifier('abc')
        danger_codes = [pmtypes.CodedValue('434343'), pmtypes.CodedValue('545454')]
        relevant_clinical_info = [pmtypes.ClinicalInfo(typecode=pmtypes.CodedValue('abc'),
                                                       descriptions=[pmtypes.LocalizedText('a', 'de'),
                                                                     pmtypes.LocalizedText('b', 'en')],
                                                       relatedmeasurements=None),
                                  pmtypes.ClinicalInfo(typecode=pmtypes.CodedValue('yxz'),
                                                       descriptions=[pmtypes.LocalizedText('u', 'de'),
                                                                     pmtypes.LocalizedText('v', 'en')],
                                                       relatedmeasurements=None)]
        requested_order_detail = pmtypes.RequestedOrderDetail(
            start='2020-10-31',
            end='2020-11-01',
            performer=[pmtypes.PersonParticipation()],
            service=[pmtypes.CodedValue('abc')],
            imagingprocedure=[],
            referringphysician=referring_physician,
            requestingphysician=requesting_physician,
            placerordernumber=pmtypes.InstanceIdentifier('root'))
        performed_order_detail = pmtypes.PerformedOrderDetail(
            start='2020-10-31',
            end='2020-11-01',
            performer=[pmtypes.PersonParticipation()],
            service=[pmtypes.CodedValue('abc')],
            imagingprocedure=[],
            fillerordernumber=pmtypes.InstanceIdentifier('abc'),
            resultingclinicalinfos=[pmtypes.ClinicalInfo(
                typecode=pmtypes.CodedValue('abc'),
                descriptions=[pmtypes.LocalizedText('a', 'de'),
                              pmtypes.LocalizedText('b', 'en')],
                relatedmeasurements=None
            )]
)

        wfd_max = pmtypes.WorkflowDetail(patient, assigned_location, visit_number, danger_codes,
                                         relevant_clinical_info, requested_order_detail, performed_order_detail)
        wfd_min = pmtypes.WorkflowDetail()
        for obj in (wfd_max, wfd_min):
            self.check_convert(obj)

    def test_relation(self):
        rel_max = pmtypes.AbstractMetricDescriptorRelation()
        rel_max.Code = pmtypes.CodedValue('abc')
        rel_max.Identification = pmtypes.InstanceIdentifier('root')
        rel_max.Kind = 'Oth'
        rel_max.Entries = ['a', 'b', 'c']
        rel_min = pmtypes.AbstractMetricDescriptorRelation()
        for obj in (rel_max, rel_min):
            self.check_convert(obj)

    @unittest.skip
    def test_selector(self):
        sel_max = pmtypes.T_Selector()
        sel_min = pmtypes.T_Selector()
        for obj in (sel_max, sel_min):
            obj_p = pmtypesmapper.selector_to_p(obj, None)
            obj2 = pmtypesmapper.selector_from_p(obj_p)
            self.assertEqual(obj.__class__, obj2.__class__)
            delta = diff(obj, obj2)
            self.assertEqual(obj, obj2)

    @unittest.skip
    def test_dual_channel_def(self):
        pass

    @unittest.skip
    def test_safety_context_def(self):
        pass

    @unittest.skip
    def test_safety_req_def(self):
        pass

    def test_udi(self):
        udi_max = pmtypes.T_Udi(
            device_identifier='prx.y.3',
            humanreadable_form='my_device',
            issuer= pmtypes.InstanceIdentifier('root'),
            jurisdiction=pmtypes.InstanceIdentifier('jurisd')
        )
        udi_min = pmtypes.T_Udi('', '', pmtypes.InstanceIdentifier('root'))
        for obj in (udi_max, udi_min):
            self.check_convert(obj)

    def test_metadata(self):
        m_min = pmtypes.MetaData()
        m_max = pmtypes.MetaData()
        m_max.Udi = [pmtypes.T_Udi(device_identifier='prx.y.3',
                                   humanreadable_form='my_device',
                                   issuer= pmtypes.InstanceIdentifier('root'),
                                   jurisdiction=pmtypes.InstanceIdentifier('jurisd') )
                     ]
        m_max.LotNumber = '08/15'
        m_max.Manufacturer = [pmtypes.LocalizedText('a', 'de'), pmtypes.LocalizedText('b', 'en')]
        m_max.ManufactureDate = '2020_01_01'
        m_max.ExpirationDate = '2020_01_02'
        m_max.ModelName = [pmtypes.LocalizedText('foo', 'de'), pmtypes.LocalizedText('bar', 'en')]
        m_max.ModelNumber = '4711'
        m_max.SerialNumber = ['abcd-1234']
        for obj in (m_max, m_min):
            self.check_convert(obj)

    def test_operation_group(self):
        og_max = pmtypes.OperationGroup()
        og_max.Type = pmtypes.CodedValue('abc')
        og_max.OperatingMode = pmtypes.OperatingMode.NA
        og_max.Operations = ['a', 'b']
        og_min = pmtypes.OperationGroup()
        for obj in (og_max, og_min):
            self.check_convert(obj)

