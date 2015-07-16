# -*- coding: utf-8 -*-

#  Copyright 2015 www.suishouguan.com
#
#  Licensed under the Private License (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import datetime
import unittest

from core import properti
from core.error import CoreError, IllegalWordError, UniqueError, \
    RequiredError, ChoiceError, LengthError, RangeError, TypeDateError, \
    TypeDatetimeError, CompareError
from core.model import Model
from core.properti import LengthValidator, RangeValidator, CompareValidator


class PropertyTestSuit(unittest.TestSuite):
    def __init__(self):
        
        unittest.TestSuite.__init__(self)
        stringpropertysuit = unittest.makeSuite(StringPropertyTest, 'test')
        self.addTest(stringpropertysuit)
        integerpropertysuit = unittest.makeSuite(IntegerPropertyTest, 'test')
        self.addTest(integerpropertysuit)
        booleanpropertysuit = unittest.makeSuite(BooleanPropertyTest, 'test')
        self.addTest(booleanpropertysuit)
        datetimepropertysuit = unittest.makeSuite(DateTimePropertyTest, 'test')
        self.addTest(datetimepropertysuit)
        datepropertysuit = unittest.makeSuite(DatePropertyTest, 'test')
        self.addTest(datepropertysuit)
        blobpropertysuit = unittest.makeSuite(BlobPropertyTest, 'test')
        self.addTest(blobpropertysuit)
        
        
class StringPropertyTest(unittest.TestCase):
    
    def testMultiline(self):
        try:
            class TModel(Model):
                sf_1 = properti.StringProperty("sf1")
            tmodel = TModel()
            tmodel.sf_1 = 'abc\ndef'
            self.assertTrue(True)
            tmodel.sf_1 = 'abcdef'
            tmodel.row_version = 1
            tmodel.creator_id = -1
            tmodel.modifier_id = -1
            tmodel.validate_props()
            self.assertTrue(True)
        except CoreError, e:
            self.assertIn("sf_1 is not multi-line", str(e))
        
    def testLength(self):
        try: 
            class TModel(Model):
                sf_2 = properti.StringProperty("sf2", length=10)
            tmodel = TModel()
            tmodel.sf_2 = "12345678901"
            tmodel.validate_props()
            self.assertTrue(False)
            tmodel.sf_2 = "abcdefgh"
            tmodel.row_version = 1
            tmodel.creator_id = -1
            tmodel.modifier_id = -1
            tmodel.validate_props()
            self.assertTrue(True)
        except CoreError, e:
            self.assertIn("it must be 10 or less.", str(e))
    
    def testRequired(self):
        class TModel(Model):
            MODULE = "test"
            sf_3 = properti.StringProperty("sf3", required=True)
        try:
            tmodel = TModel()
            tmodel.sf_3 = None
            tmodel.validate_props()
            self.assertTrue(False)
        except RequiredError:
            self.assertTrue(True)

        try:
            tmodel = TModel()
            tmodel.validate_props()
            self.assertTrue(False)
        except RequiredError:
            self.assertTrue(True)
    
    def testChoices(self):
        try:
            class TModel(Model):
                sf_4 = properti.StringProperty("sf4", choices=['a', 'b', 'c'])
            tmodel = TModel()
            tmodel.sf_4 = 'd'
            tmodel.put(1)
            self.assertTrue(False)
            tmodel.sf_4 = 'c'
            self.assertTrue(True)
        except ChoiceError:
            self.assertTrue(True)
    
    def testDefault(self):
        class TModel(Model):
                sf_5 = properti.StringProperty("sf5", default='abcd')
        tmodel = TModel()
        self.assertEqual(tmodel.sf_5, 'abcd')
        self.assertNotEqual(tmodel.sf_5, 'abcf')
        try:
            class TModel(Model):
                sf_7 = properti.StringProperty("sf7", default='d', choices=['a', 'b', 'c'])
            TModel().validate_props()
            self.assertTrue(False)               
        except ChoiceError:
            self.assertTrue(True)
    
    def testIlleagalValidator(self):
        try:
            class TModel(Model):
                sf_6 = properti.StringProperty("sf6", validator=properti.IllegalValidator())
            tmodel = TModel()
            tmodel.sf_6 = "abcdef"
            self.assertTrue(True)
            tmodel.sf_6 = u"江泽民"
            tmodel.put(1)
            self.assertTrue(False)
            tmodel.sf_6 = u"骚女"
            tmodel.put(1)
            self.assertTrue(False)
            tmodel.sf_6 = u"2005年十大欠抽人物"
            tmodel.put(1)
            self.assertTrue(False)
            tmodel.sf_6 = u"2005语录排行榜"
            tmodel.put(1)
            self.assertTrue(False)
        except IllegalWordError:
            self.assertTrue(True)
            
    def testUniqueValidator(self):
        try:
            class TModelVal(Model):
                MODULE = "test"
                sf_6 = properti.StringProperty("sf6", validator=properti.UniqueValidator("sf_6"))
            TModelVal.create_table()
            tmodel = TModelVal()
            tmodel.sf_6 = "abcdef"
            tmodel.create(1)
            tmodel = TModelVal()
            tmodel.sf_6 = "abcdef"    
            tmodel.create(1)
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        tmodel.sf_6 = "abcdef11"
        tmodel.put(1)
        self.assertTrue(True)
                
        try:
            query = TModelVal.all()
            tm = query.get()
            tmodel = TModelVal()
            tmodel.sf_6 = tm.sf_6    
            tmodel.put(1)
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        
        TModelVal.delete_table()

class IntegerPropertyTest(unittest.TestCase):
        
    def testLength(self):
        try:
            class TModel(Model):
                if_1 = properti.IntegerProperty("if1", length=11)
                if_2 = properti.StringProperty("if2", length=8)
            tmodel = TModel()
            tmodel.if_1 = 0x8fffffffffffffff
            tmodel.validate_props()
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn("must fit in 64 bits", str(e))

class BooleanPropertyTest(unittest.TestCase):
        
    def testType(self):
        class TModel(Model):
            bf_1 = properti.BooleanProperty("bf1")
        tmodel = TModel(entityinst=True)
        tmodel.bf_1 = 1
        self.assertTrue(isinstance(tmodel.bf_1, bool))
        self.assertEqual(tmodel.bf_1, True)
        tmodel.bf_1 = False
        self.assertTrue(isinstance(tmodel.bf_1, bool))
        self.assertEqual(tmodel.bf_1, False)
    
    def testInt(self):
        class TModel(Model):
            bf_1 = properti.BooleanProperty("bf1")
        tmodel = TModel(entityinst=True, bf_1=1)
        self.assertTrue(isinstance(tmodel.bf_1, bool))
        self.assertEqual(tmodel.bf_1, True)
        tmodel = TModel(entityinst=True, bf_1=0)
        self.assertTrue(isinstance(tmodel.bf_1, bool))
        self.assertEqual(tmodel.bf_1, False)
        
    def testDefault(self):
        class TModel(Model):
            bf_2 = properti.BooleanProperty("bf2", default=True)
        tmodel = TModel()
        self.assertEqual(tmodel.bf_2, True)
        class TModel2(Model):
            bf_2 = properti.BooleanProperty("bf2", default=1)
        tmodel = TModel()
        self.assertTrue(isinstance(tmodel.bf_2, bool))
        self.assertEqual(tmodel.bf_2, True)
    
    def testRequired(self):
        class TModel(Model):
            bf_1 = properti.BooleanProperty("bf1")
        try:
            tmodel = TModel()
            tmodel.bf_1 = None
            tmodel.validate_props()
            self.assertTrue(False)
        except RequiredError:
            self.assertTrue(True)

        try:
            class TModel(Model):
                MODULE = "test"
                bf_1 = properti.BooleanProperty("bf1", default=None)
            tmodel = TModel()
            tmodel.validate_props()
            self.assertTrue(False)
        except RequiredError:
            self.assertTrue(True)
    
    def testValidate(self):
        class TModel(Model):
            dtf_2 = properti.BooleanProperty("dtf2")
        tmodel = TModel()
        try:
            tmodel.dtf_2 = properti.DateTimeProperty.utcnow()
        except CoreError, e:
            self.assertIn("must be a bool", str(e))
        
        try:
            tmodel.dtf_2 = 1
            tmodel.validate_props()
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn("must be a bool", str(e))
        
        tmodel = TModel(entityinst=True)
        tmodel.dtf_2 = 1
        self.assertTrue(isinstance(tmodel.dtf_2, bool))
        self.assertTrue(tmodel.dtf_2)
        
    def testLength(self):
        class TModel(Model):
            dtf_2 = properti.StringProperty("dtf2", validator=LengthValidator(minlength=2, maxlength=5))
        tmodel = TModel()
        try:
            tmodel.dtf_2 = "a"
            tmodel.validate_props()
            self.assertTrue(False)
        except LengthError:
            self.assertTrue(True)
        
        try:
            tmodel.dtf_2 = "abcdef1"
            tmodel.validate_props()
            self.assertTrue(False)
        except LengthError:
            self.assertTrue(True)
            
        try:
            tmodel.dtf_2 = "ab"
            tmodel.validate_props()
            self.assertTrue(True)
        except LengthError:
            self.assertTrue(False)
        
        try:
            tmodel.dtf_2 = "abcde"
            tmodel.validate_props()
            self.assertTrue(True)
        except LengthError:
            self.assertTrue(False)
    
    def testRangeInt(self):
        class TModel(Model):
            dtf_2 = properti.IntegerProperty("dtf2", validator=RangeValidator(minimum=2, maximum=5))
        tmodel = TModel()
        try:
            tmodel.dtf_2 = 1
            tmodel.validate_props()
            self.assertTrue(False)
        except RangeError:
            self.assertTrue(True)
        
        try:
            tmodel.dtf_2 = 6
            tmodel.validate_props()
            self.assertTrue(False)
        except RangeError:
            self.assertTrue(True)
            
        try:
            tmodel.dtf_2 = 5
            tmodel.validate_props()
            self.assertTrue(True)
        except RangeError:
            self.assertTrue(False)
        
        try:
            tmodel.dtf_2 = 2
            tmodel.validate_props()
            self.assertTrue(True)
        except RangeError:
            self.assertTrue(False)
            
    def testRangeFloat(self):
        class TModel(Model):
            dtf_2 = properti.FloatProperty("dtf2", validator=RangeValidator(minimum=2.0, maximum=5.0))
        tmodel = TModel()
        try:
            tmodel.dtf_2 = 1.0
            tmodel.validate_props()
            self.assertTrue(False)
        except RangeError:
            self.assertTrue(True)
        
        try:
            tmodel.dtf_2 = 6.5
            tmodel.validate_props()
            self.assertTrue(False)
        except RangeError:
            self.assertTrue(True)
            
        try:
            tmodel.dtf_2 = 5.0
            self.assertTrue(True)
        except RangeError:
            self.assertTrue(False)
        
        try:
            tmodel.dtf_2 = 2.0
            self.assertTrue(True)
        except RangeError:
            self.assertTrue(False)
    
    def testRangeNoSupportType(self):
        class TModel(Model):
            dtf_2 = properti.BlobProperty("dtf2", validator=RangeValidator(minimum=2.0, maximum=5.0))
        tmodel = TModel()
        try:
            tmodel.dtf_2 = False
            tmodel.put(1)
            self.assertTrue(False)
        except CoreError:
            self.assertTrue(True)
            
    def testRangeDate(self):
        class TModel(Model):
            dtf_2 = properti.DateProperty("dtf2", validator=RangeValidator(minimum=datetime.date(2014, 5, 6), maximum=datetime.date(2014, 8, 8)))
        tmodel = TModel()
        try:
            tmodel.dtf_2 = datetime.date(2014, 5, 5)
            tmodel.put(1)
            self.assertTrue(False)
        except RangeError:
            self.assertTrue(True)
        
        try:
            tmodel.dtf_2 = datetime.date(2014, 8, 9)
            tmodel.validate_props()
            self.assertTrue(False)
        except RangeError:
            self.assertTrue(True)
            
        try:
            tmodel.dtf_2 = datetime.date(2014, 5, 6)
            self.assertTrue(True)
        except RangeError:
            self.assertTrue(False)
        
        try:
            tmodel.dtf_2 = datetime.date(2014, 8, 8)
            self.assertTrue(True)
        except RangeError:
            self.assertTrue(False)
            
    def testCompareInt(self):
        
        class TModel(Model):
            MODULE = "test"
            dtf_1 = properti.IntegerProperty("dtf1", validator=CompareValidator("=", limit=2))
            dtf_2 = properti.IntegerProperty("dtf2", validator=CompareValidator(">=", limit=2))
            dtf_3 = properti.IntegerProperty("dtf3", validator=CompareValidator("<=", limit=2))
            dtf_4 = properti.IntegerProperty("dtf4", validator=CompareValidator(">", limit=2))
            dtf_5 = properti.IntegerProperty("dtf5", validator=CompareValidator("<", limit=2))
            
        tmodel = TModel()            
        try:
            tmodel.dtf_1 = 3
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
        
        tmodel = TModel()            
        try:
            tmodel.dtf_2 = 1
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_3 = 4
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_4 = 0
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_5 = 7
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
    
    def testCompareDate(self):
        
        class TModel(Model):
            MODULE = "test"
            dtf_1 = properti.DateProperty("dtf1", validator=CompareValidator("=", limit=datetime.date(2014,2,1)))
            dtf_2 = properti.DateProperty("dtf2", validator=CompareValidator(">=", limit=datetime.date(2014,2,1)))
            dtf_3 = properti.DateProperty("dtf3", validator=CompareValidator("<=", limit=datetime.date(2014,2,1)))
            dtf_4 = properti.DateProperty("dtf4", validator=CompareValidator(">", limit=datetime.date(2014,2,1)))
            dtf_5 = properti.DateProperty("dtf5", validator=CompareValidator("<", limit=datetime.date(2014,2,1)))
            
        tmodel = TModel()            
        try:
            tmodel.dtf_1 = datetime.date(2014,3,1)
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
        
        tmodel = TModel()            
        try:
            tmodel.dtf_2 = datetime.date(2014,1,1)
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_3 = datetime.date(2014,3,1)
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_4 = datetime.date(2014,2,1)
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_5 = datetime.date(2014,6,1)
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
       
    def testCompareBetweenProp(self):
        
        class TModel(Model):
            MODULE = "test"
            dtf_1 = properti.DateProperty("dtf1", validator=CompareValidator(">=", property_name="dtf_2"))
            dtf_2 = properti.DateProperty("dtf2")
            
        tmodel = TModel()            
        try:
            tmodel.dtf_1 = datetime.date(2014,1,1)
            tmodel.dtf_2 = datetime.date(2014,2,1)
            tmodel.put(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
            
class DateTimePropertyTest(unittest.TestCase):
    
    def testAutoUTC(self):
        class TModel(Model):
            dtf_2 = properti.DateTimeProperty("dtf2", auto_utcnow=True)
        tmodel = TModel()
        self.assertIsNotNone(tmodel.dtf_2)
    
    def testValidate(self):
        class TModel(Model):
            dtf_2 = properti.DateTimeProperty("dtf2")
        tmodel = TModel()
        try:
            tmodel.dtf_2 = 123
            tmodel.put(1)
            self.assertFalse(True)
        except CoreError:
                self.assertTrue(True)
        
        tmodel = TModel()
        try:
            tmodel.dtf_2 = "fafafa"
            tmodel.put(1)
            self.assertFalse(True)
        except TypeDatetimeError:
                self.assertTrue(True)
        
class DatePropertyTest(unittest.TestCase):
    
    def testAutoUTCToday(self):
        class TModel(Model):
            dtf_2 = properti.DateProperty("dtf2", auto_utctoday=True)
        tmodel = TModel()
        self.assertEqual(tmodel.dtf_2, properti.DateProperty.utctoday())

    def testValidate(self):
        class TModel(Model):
            dtf_2 = properti.DateProperty("dtf2")
        tmodel = TModel()
        try:
            tmodel.dtf_2 = "aaa"
            tmodel.put(1)
            self.assertFalse(True)
        except TypeDateError:
            self.assertTrue(True)

class BlobPropertyTest(unittest.TestCase):
    
    """To be added"""
