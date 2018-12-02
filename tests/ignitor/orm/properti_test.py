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

from ssguan.ignitor.base.error import Error, ProgramError 
from ssguan.ignitor.base.error import RequiredError, ChoiceError, TypeBoolError, CompareError, TypeDatetimeError, TypeDateError, \
    TypeDictError, LengthError, RangeError
from ssguan.ignitor.orm import  config as orm_config
from ssguan.ignitor.orm import dbpool, properti, config as dbconfig
from ssguan.ignitor.orm.error import IllegalWordError, UniqueError
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.orm.validator import LengthValidator, RangeValidator, CompareValidator, \
    IllegalValidator, UniqueValidator
from ssguan.ignitor.utility import kind


class StringPropertyTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
    
    def test_multiline(self):
        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_1 = properti.StringProperty()
            tmodel = TModel()
            tmodel.sf_1 = 'abc\ndef'
            self.assertTrue(True)
            tmodel.sf_1 = 'abcdef'
            tmodel.row_version = 1
            tmodel.created_by = -1
            tmodel.modified_by = -1
            tmodel.validate_props()
            self.assertTrue(True)
        except ProgramError as e:
            self.assertIn("sf_1 is not multi-line", str(e))
        
    def test_length(self):
        try: 
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_2 = properti.StringProperty(length=10)
            tmodel = TModel()
            tmodel.sf_2 = "12345678901"
            tmodel.created_by = "-1"
            tmodel.modified_by = "-1"
            tmodel.validate_props()
            self.assertTrue(False)
            tmodel.sf_2 = "abcdefgh"
            tmodel.row_version = 1
            tmodel.created_by = "-1"
            tmodel.modified_by = "-1"
            tmodel.validate_props()
            self.assertTrue(True)
        except Error as e:
            self.assertIsInstance(e, LengthError)
    
    def test_required(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "def test_"
            sf_3 = properti.StringProperty(required=True)
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
    
    def test_choices(self):
        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_4 = properti.StringProperty(choices=['a', 'b', 'c'])
            tmodel = TModel()
            tmodel.sf_4 = 'd'
            tmodel.create(1)
            self.assertTrue(False)
            tmodel.sf_4 = 'c'
            self.assertTrue(True)
        except ChoiceError:
            self.assertTrue(True)
    
    def test_default(self):
        class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_5 = properti.StringProperty(default='abcd')
        tmodel = TModel()
        self.assertEqual(tmodel.sf_5, 'abcd')
        self.assertNotEqual(tmodel.sf_5, 'abcf')
        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_7 = properti.StringProperty(default='d', choices=['a', 'b', 'c'])
            TModel(created_by="-1", modified_by="-1").validate_props()
            self.assertTrue(False)               
        except ChoiceError:
            self.assertTrue(True)
    
    def test_illeagalvalidator(self):
        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_6 = properti.StringProperty(validator=IllegalValidator())
            tmodel = TModel()
            tmodel.sf_6 = "abcdef"
            self.assertTrue(True)
            tmodel.sf_6 = u"江泽民"
            tmodel.create(1)
            self.assertTrue(False)
            tmodel.sf_6 = u"骚女"
            tmodel.update(1)
            self.assertTrue(False)
            tmodel.sf_6 = u"2005年十大欠抽人"
            tmodel.update(1)
            self.assertTrue(False)
            tmodel.sf_6 = u"2005语录排行"
            tmodel.update(1)
            self.assertTrue(False)
        except IllegalWordError:
            self.assertTrue(True)
            
    def test_uniquevalidator(self):
        try:
            class TModelVal(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"   
                sf_6 = properti.StringProperty(validator=UniqueValidator("sf_6"))
            TModelVal.create_schema()
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
        tmodel.create(1)
        self.assertTrue(True)
                
        try:
            query = TModelVal.all()
            tm = query.get()
            tmodel = TModelVal()
            tmodel.sf_6 = tm.sf_6    
            tmodel.create(1)
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        
        TModelVal.delete_schema()
    
    @classmethod
    def tearDownClass(cls):         
        dbpool.drop_db(orm_config.get_default_dbinfo())
        
    
class IntegerPropertyTest(unittest.TestCase):
        
    def test_length(self):
        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                if_1 = properti.IntegerProperty(length=11)
                if_2 = properti.StringProperty(length=8)
            tmodel = TModel()
            tmodel.created_by = "-1"
            tmodel.modified_by = "-1"
            tmodel.if_1 = 0x8fffffffffffffff
            tmodel.validate_props()
            self.assertTrue(False)
        except LengthError:
            self.assertTrue(True)

class BooleanPropertyTest(unittest.TestCase):
        
    def test_type(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            bf_1 = properti.BooleanProperty()
        tmodel = TModel(entityinst=True)
        tmodel.bf_1 = 1
        self.assertTrue(isinstance(tmodel.bf_1, bool))
        self.assertEqual(tmodel.bf_1, True)
        tmodel.bf_1 = False
        self.assertTrue(isinstance(tmodel.bf_1, bool))
        self.assertEqual(tmodel.bf_1, False)
    
    def test_int(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            bf_1 = properti.BooleanProperty()
        tmodel = TModel(entityinst=True, bf_1=1)
        self.assertTrue(isinstance(tmodel.bf_1, bool))
        self.assertEqual(tmodel.bf_1, True)
        tmodel = TModel(entityinst=True, bf_1=0)
        self.assertTrue(isinstance(tmodel.bf_1, bool))
        self.assertEqual(tmodel.bf_1, False)
        
    def test_default(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            bf_2 = properti.BooleanProperty(default=True)
        tmodel = TModel()
        self.assertEqual(tmodel.bf_2, True)
        class TModel2(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            bf_2 = properti.BooleanProperty(default=1)
        tmodel = TModel()
        self.assertTrue(isinstance(tmodel.bf_2, bool))
        self.assertEqual(tmodel.bf_2, True)
    
    def test_required(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            bf_1 = properti.BooleanProperty()
        try:
            tmodel = TModel()
            tmodel.bf_1 = None
            tmodel.validate_props()
            self.assertTrue(False)
        except RequiredError:
            self.assertTrue(True)

        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                bf_1 = properti.BooleanProperty(default=None)
            tmodel = TModel()
            tmodel.validate_props()
            self.assertTrue(False)
        except RequiredError:
            self.assertTrue(True)
    
    def test_validate(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.BooleanProperty()
        tmodel = TModel()
        try:
            tmodel.dtf_2 = properti.DateTimeProperty.utcnow()
        except ProgramError as e:
            self.assertIn("must be a bool", str(e))
        
        try:
            tmodel.dtf_2 = 1
            tmodel.created_by = "-1"
            tmodel.modified_by = "-1"
            tmodel.validate_props()
            self.assertTrue(False)
        except Error as e:
            self.assertIsInstance(e, TypeBoolError)
        
        tmodel = TModel(entityinst=True)
        tmodel.dtf_2 = 1
        self.assertTrue(isinstance(tmodel.dtf_2, bool))
        self.assertTrue(tmodel.dtf_2)
        
    def test_length(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.StringProperty(validator=LengthValidator(minlength=2, maxlength=5))
        tmodel = TModel()
        try:
            tmodel.dtf_2 = "a"
            tmodel.created_by = "1"
            tmodel.modified_by = "1"
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
    
    def test_range_int(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.IntegerProperty(validator=RangeValidator(minimum=2, maximum=5))
        tmodel = TModel()
        try:
            tmodel.dtf_2 = 1
            tmodel.created_by = "-1"
            tmodel.modified_by = "-1"
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
            
    def test_range_float(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.FloatProperty(validator=RangeValidator(minimum=2.0, maximum=5.0))
        tmodel = TModel()
        tmodel.created_by = "-1"
        tmodel.modified_by = "-1"
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
    
    def test_range_date(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.DateProperty(validator=RangeValidator(minimum=datetime.date(2014, 5, 6), maximum=datetime.date(2014, 8, 8)))
        tmodel = TModel()
        try:
            tmodel.dtf_2 = datetime.date(2014, 5, 5)
            tmodel.create(1)
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
            
    def test_compare_int(self):
        
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_1 = properti.IntegerProperty(validator=CompareValidator("=", limit=2))
            dtf_2 = properti.IntegerProperty(validator=CompareValidator(">=", limit=2))
            dtf_3 = properti.IntegerProperty(validator=CompareValidator("<=", limit=2))
            dtf_4 = properti.IntegerProperty(validator=CompareValidator(">", limit=2))
            dtf_5 = properti.IntegerProperty(validator=CompareValidator("<", limit=2))
            
        tmodel = TModel()            
        try:
            tmodel.dtf_1 = 3
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
        
        tmodel = TModel()            
        try:
            tmodel.dtf_2 = 1
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_3 = 4
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_4 = 0
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_5 = 7
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
    
    def test_compare_date(self):
        
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_1 = properti.DateProperty(validator=CompareValidator("=", limit=datetime.date(2014, 2, 1)))
            dtf_2 = properti.DateProperty(validator=CompareValidator(">=", limit=datetime.date(2014, 2, 1)))
            dtf_3 = properti.DateProperty(validator=CompareValidator("<=", limit=datetime.date(2014, 2, 1)))
            dtf_4 = properti.DateProperty(validator=CompareValidator(">", limit=datetime.date(2014, 2, 1)))
            dtf_5 = properti.DateProperty(validator=CompareValidator("<", limit=datetime.date(2014, 2, 1)))
            
        tmodel = TModel()            
        try:
            tmodel.dtf_1 = datetime.date(2014, 3, 1)
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
        
        tmodel = TModel()            
        try:
            tmodel.dtf_2 = datetime.date(2014, 1, 1)
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_3 = datetime.date(2014, 3, 1)
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_4 = datetime.date(2014, 2, 1)
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
        tmodel = TModel()            
        try:
            tmodel.dtf_5 = datetime.date(2014, 6, 1)
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
       
    def test_compare_between_prop(self):
        
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_1 = properti.DateProperty(validator=CompareValidator(">=", property_name="dtf_2"))
            dtf_2 = properti.DateProperty()
            
        tmodel = TModel()            
        try:
            tmodel.dtf_1 = datetime.date(2014, 1, 1)
            tmodel.dtf_2 = datetime.date(2014, 2, 1)
            tmodel.create(1)
            self.assertTrue(False)
        except CompareError:
            self.assertTrue(True)
            
            
class DateTimePropertyTest(unittest.TestCase):
    
    def test_auto_utcnow(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.DateTimeProperty(auto_utcnow=True)
        tmodel = TModel()
        self.assertIsNotNone(tmodel.dtf_2)
    
    def test_validate(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.DateTimeProperty()
        tmodel = TModel()
        try:
            tmodel.dtf_2 = 123
            tmodel.create(1)
            self.assertFalse(True)
        except Error as e:
                self.assertIsInstance(e, TypeDatetimeError)
        
        tmodel = TModel()
        try:
            tmodel.dtf_2 = "fafafa"
            tmodel.create(1)
            self.assertFalse(True)
        except TypeDatetimeError:
                self.assertTrue(True)
        
class DatePropertyTest(unittest.TestCase):
    
    def test_auto_utctoday(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.DateProperty(auto_utctoday=True)
        tmodel = TModel()
        self.assertEqual(tmodel.dtf_2, properti.DateProperty.utctoday())

    def test_validate(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = properti.DateProperty()
        tmodel = TModel()
        try:
            tmodel.dtf_2 = "aaa"
            tmodel.create(1)
            self.assertFalse(True)
        except TypeDateError:
            self.assertTrue(True)

class DictPropertyTest(unittest.TestCase):
    
    class TModel66(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        dtf_11 = properti.DictProperty()
    
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(dbconfig.get_default_dbinfo(), dropped=True)
        cls.TModel66.create_schema()
       
    def test_value(self):
        tmodel = self.TModel66()
        tmodel.dtf_11 = {"aa":"bb"}
        tmodel2 = tmodel.create(1)
        key = tmodel2.key()
        self.assertIsInstance(tmodel2.dtf_11, dict)
        try:
            tmodel.dtf_11 = kind.utcnow()
            tmodel2 = tmodel.create(1)
            self.assertTrue(False)
        except TypeDictError:
            self.assertTrue(True)
        self.assertIsInstance(tmodel2.dtf_11, datetime.datetime)
        tm = self.TModel66.get_by_key(key)
        self.assertIsInstance(tm.dtf_11, dict)
        tm.dtf_11 = {'cc':'ae'}
        tm1 = tm.update(None)
        self.assertEqual(tm1.dtf_11, {'cc':'ae'})
        tm.dtf_11 = ['cc', 'ae']
        try:
            tm1 = tm.update(None)
            self.assertTrue(False)
        except TypeDictError:
            self.assertTrue(True)
        self.assertEqual(tm1.dtf_11, ['cc', 'ae'])
        
        
    def test_validate(self):
        class TModel67(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_11 = properti.DictProperty(length=5)
        tmodel = TModel67()
        try:
            tmodel.dtf_11 = {"aa":"bb"}
            tmodel.create(1)
            self.assertFalse(True)
        except LengthError:
            self.assertTrue(True)
            
    @classmethod
    def tearDownClass(cls):
        cls.TModel66.delete_schema()
        dbpool.drop_db(dbconfig.get_default_dbinfo())
                        
