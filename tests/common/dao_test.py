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
from datetime import timedelta
import datetime
import time
import traceback
import unittest

from ssguan import config
from ssguan.commons import database, dao, typeutils
from ssguan.commons.dao import RequiredError, ChoiceError, IllegalWordError, \
    UniqueError, TypeBoolError, LengthValidator, RangeValidator, \
    CompareValidator, CompareError, TypeDatetimeError, TypeDateError, \
    TypeDictError, Model, LengthError, RangeError, BaseModel, BaseQuery, \
    TypeFloatError
from ssguan.commons.error import Error, ProgramError 
from ssguan.modules import sysprop


class StringPropertyTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
    
    def test_multiline(self):
        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_1 = dao.StringProperty("sf1")
            tmodel = TModel()
            tmodel.sf_1 = 'abc\ndef'
            self.assertTrue(True)
            tmodel.sf_1 = 'abcdef'
            tmodel.row_version = 1
            tmodel.created_by = -1
            tmodel.modified_by = -1
            tmodel.validate_props()
            self.assertTrue(True)
        except ProgramError, e:
            self.assertIn("sf_1 is not multi-line", str(e))
        
    def test_length(self):
        try: 
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_2 = dao.StringProperty("sf2", length=10)
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
        except Error, e:
            self.assertIsInstance(e, LengthError)
    
    def test_required(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "def test_"
            sf_3 = dao.StringProperty("sf3", required=True)
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
                sf_4 = dao.StringProperty("sf4", choices=['a', 'b', 'c'])
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
                sf_5 = dao.StringProperty("sf5", default='abcd')
        tmodel = TModel()
        self.assertEqual(tmodel.sf_5, 'abcd')
        self.assertNotEqual(tmodel.sf_5, 'abcf')
        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                sf_7 = dao.StringProperty("sf7", default='d', choices=['a', 'b', 'c'])
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
                sf_6 = dao.StringProperty("sf6", validator=dao.IllegalValidator())
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
                sf_6 = dao.StringProperty("sf6", validator=dao.UniqueValidator("sf_6"))
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
        database.drop_db(config.dbCFG.get_root_dbinfo())

class IntegerPropertyTest(unittest.TestCase):
        
    def test_length(self):
        try:
            class TModel(Model):
                @classmethod
                def meta_domain(cls):
                    return "test"
                if_1 = dao.IntegerProperty("if1", length=11)
                if_2 = dao.StringProperty("if2", length=8)
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
            bf_1 = dao.BooleanProperty("bf1")
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
            bf_1 = dao.BooleanProperty("bf1")
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
            bf_2 = dao.BooleanProperty("bf2", default=True)
        tmodel = TModel()
        self.assertEqual(tmodel.bf_2, True)
        class TModel2(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            bf_2 = dao.BooleanProperty("bf2", default=1)
        tmodel = TModel()
        self.assertTrue(isinstance(tmodel.bf_2, bool))
        self.assertEqual(tmodel.bf_2, True)
    
    def test_required(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            bf_1 = dao.BooleanProperty("bf1")
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
                bf_1 = dao.BooleanProperty("bf1", default=None)
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
            dtf_2 = dao.BooleanProperty("dtf2")
        tmodel = TModel()
        try:
            tmodel.dtf_2 = dao.DateTimeProperty.utcnow()
        except ProgramError, e:
            self.assertIn("must be a bool", str(e))
        
        try:
            tmodel.dtf_2 = 1
            tmodel.created_by = "-1"
            tmodel.modified_by = "-1"
            tmodel.validate_props()
            self.assertTrue(False)
        except Error, e:
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
            dtf_2 = dao.StringProperty("dtf2", validator=LengthValidator(minlength=2, maxlength=5))
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
            dtf_2 = dao.IntegerProperty("dtf2", validator=RangeValidator(minimum=2, maximum=5))
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
            dtf_2 = dao.FloatProperty("dtf2", validator=RangeValidator(minimum=2.0, maximum=5.0))
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
            dtf_2 = dao.DateProperty("dtf2", validator=RangeValidator(minimum=datetime.date(2014, 5, 6), maximum=datetime.date(2014, 8, 8)))
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
            dtf_1 = dao.IntegerProperty("dtf1", validator=CompareValidator("=", limit=2))
            dtf_2 = dao.IntegerProperty("dtf2", validator=CompareValidator(">=", limit=2))
            dtf_3 = dao.IntegerProperty("dtf3", validator=CompareValidator("<=", limit=2))
            dtf_4 = dao.IntegerProperty("dtf4", validator=CompareValidator(">", limit=2))
            dtf_5 = dao.IntegerProperty("dtf5", validator=CompareValidator("<", limit=2))
            
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
            dtf_1 = dao.DateProperty("dtf1", validator=CompareValidator("=", limit=datetime.date(2014, 2, 1)))
            dtf_2 = dao.DateProperty("dtf2", validator=CompareValidator(">=", limit=datetime.date(2014, 2, 1)))
            dtf_3 = dao.DateProperty("dtf3", validator=CompareValidator("<=", limit=datetime.date(2014, 2, 1)))
            dtf_4 = dao.DateProperty("dtf4", validator=CompareValidator(">", limit=datetime.date(2014, 2, 1)))
            dtf_5 = dao.DateProperty("dtf5", validator=CompareValidator("<", limit=datetime.date(2014, 2, 1)))
            
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
            dtf_1 = dao.DateProperty("dtf1", validator=CompareValidator(">=", property_name="dtf_2"))
            dtf_2 = dao.DateProperty("dtf2")
            
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
            dtf_2 = dao.DateTimeProperty("dtf2", auto_utcnow=True)
        tmodel = TModel()
        self.assertIsNotNone(tmodel.dtf_2)
    
    def test_validate(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = dao.DateTimeProperty("dtf2")
        tmodel = TModel()
        try:
            tmodel.dtf_2 = 123
            tmodel.create(1)
            self.assertFalse(True)
        except Error, e:
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
            dtf_2 = dao.DateProperty("dtf2", auto_utctoday=True)
        tmodel = TModel()
        self.assertEqual(tmodel.dtf_2, dao.DateProperty.utctoday())

    def test_validate(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_2 = dao.DateProperty("dtf2")
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
        dtf_11 = dao.DictProperty("dtf2")
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        cls.TModel66.create_schema()
       
    def test_value(self):
        tmodel = self.TModel66()
        tmodel.dtf_11 = {"aa":"bb"}
        tmodel2 = tmodel.create(1)
        key = tmodel2.key()
        self.assertIsInstance(tmodel2.dtf_11, dict)
        try:
            tmodel.dtf_11 = typeutils.utcnow()
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
        tm.dtf_11 = ['cc','ae']
        try:
            tm1 = tm.update(None)
            self.assertTrue(False)
        except TypeDictError:
            self.assertTrue(True)
        self.assertEqual(tm1.dtf_11, ['cc','ae'])
        
        
    def test_validate(self):
        class TModel67(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            dtf_11 = dao.DictProperty("dtf2", length=5)
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
        database.drop_db(config.dbCFG.get_root_dbinfo())
                        
class BaseModelTest(unittest.TestCase):
    
    class TModel(BaseModel):
        @classmethod
        def meta_domain(cls):
            return "test"
        f_str = dao.StringProperty("fStr")
        f_int = dao.IntegerProperty("fInt")
        f_bool = dao.BooleanProperty("fBool")
        f_float = dao.FloatProperty("fFloat")
        f_date = dao.DateProperty("fDate")
        f_datetime = dao.DateTimeProperty("fDatetime")
        f_v = dao.StringProperty("fV", length=8)
        f_str1 = dao.StringProperty("fStr1", persistent=False)
        f_json = dao.DictProperty("fObject")
        
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        cls.TModel.create_schema()
    
    def test_exist_property(self):
        tm = self.TModel().create()
        t = self.TModel.exist_property("f_str")
        self.assertTrue(t)
        t = self.TModel.exist_property("f_str1")
        self.assertFalse(t)
        tm.delete()
        
    def test_add_property(self):
        tm = self.TModel().create()
        t = self.TModel.add_property("f_str11", dao.StringProperty("str11"))
        self.assertTrue(t)
        t = self.TModel.add_property("f_str11", dao.StringProperty("str11"))
        self.assertFalse(t)
        tm.delete()
        
    def test_change_property(self):
        tm = self.TModel().create()
        self.TModel.add_property("f_str33344", dao.StringProperty("str33344"))
        t = self.TModel.exist_property("f_str33344")
        self.assertTrue(t)
        t = self.TModel.change_property("f_str33344", "f_str444", dao.StringProperty("str444", length=200))
        self.assertTrue(t)
        t = self.TModel.exist_property("f_str33344")
        self.assertFalse(t)
        t = self.TModel.exist_property("f_str444")
        self.assertTrue(t)
        tm.delete()
        
    def test_drop_property(self):
        tm = self.TModel().create()
        self.TModel.add_property("f_str555", dao.StringProperty("str555"))
        t = self.TModel.exist_property("f_str555")
        self.assertTrue(t)
        t = self.TModel.drop_property("f_str555")
        self.assertTrue(t)
        t = self.TModel.exist_property("f_str555")
        self.assertFalse(t)
        tm.delete()
    
    def test_create_and_get_by_key(self):
        tmodel = self.TModel()
        tmodel.f_str = "abcd"
        tmodel.f_int = 100
        tmodel.f_float = 1000.0
        tmodel.f_bool = False
        tmodel.f_date = dao.DateProperty.utctoday()
        utc = typeutils.utcnow()
        utc = utc.replace(microsecond=0)
        tmodel.f_datetime = utc
        tmodel.create()
        self.assertIsNotNone(tmodel.get_keyvalue())
        self.assertNotEqual(tmodel.get_keyvalue(), 0)
        tmodel2 = self.TModel.get_by_key(tmodel.get_keyvalue())
        self.assertEqual(tmodel.f_str, tmodel2.f_str)
        self.assertEqual(tmodel.f_int, tmodel2.f_int)
        self.assertEqual(tmodel.f_float, tmodel2.f_float)
        self.assertEqual(tmodel.f_bool, tmodel2.f_bool)
        self.assertEqual(utc, tmodel2.f_datetime)
        self.assertEqual(dao.DateProperty.utctoday(), tmodel2.f_date)
        
        tmodel = self.TModel()
        tmodel.f_str = "eeeffffee"
        tmodel.f_json = {'1':1}
        tmodel.create(key="33333")
        tm = tmodel.get_by_key("33333")
        self.assertEqual(tm.f_str, tmodel.f_str)
        self.assertEqual(tm.f_json, tmodel.f_json)
        tm.delete()
        
        
    def test_model_extproperties_sql_alias(self):
        query = self.TModel.all()
        query.what("_id", "u1")
        query.what("f_str", "s1")
        query.what("f_bool", "b1")
        tmodel = query.get()
        extprops = tmodel._extproperties
        if config.dbCFG.get_dbinfo(self.TModel).is_mongo():
            self.assertFalse(extprops.has_key('u1'))
            self.assertFalse(extprops.has_key('s1'))
            self.assertFalse(extprops.has_key('b1'))
            self.assertEqual(len(extprops.keys()), 0)
        else:
            self.assertTrue(extprops.has_key('u1'))
            self.assertTrue(extprops.has_key('s1'))
            self.assertTrue(extprops.has_key('b1'))
            self.assertEqual(len(extprops.keys()), 3)
        
    def test_model_properties(self):
        props = self.TModel.get_properties()
        self.assertTrue(props.has_key('f_str'))
        self.assertTrue(props.has_key('f_int'))
        self.assertTrue(props.has_key('f_bool'))
        self.assertTrue(props.has_key('f_float'))
        self.assertTrue(props.has_key('f_datetime'))
        self.assertTrue(props.has_key('f_date'))
        self.assertTrue(props.has_key('_id'))
        self.assertTrue(props.has_key('f_str1'))
        self.assertEqual(len(props.keys()), 10)
    
    def test_get_properties(self):
        props = self.TModel.get_properties(persistent=True)
        self.assertEqual(len(props.keys()), 9)
        props = self.TModel.get_properties(persistent=False)
        self.assertEqual(len(props.keys()), 1)
        
    def test_is_persistent(self):
        self.assertTrue(self.TModel.is_persistent("f_str"))
        self.assertFalse(self.TModel.is_persistent("f_str1"))
        self.assertTrue(self.TModel.is_persistent())
        
    def test_has_prop(self):
        tmodel = self.TModel(a="ccc")
        b = hasattr(tmodel, "a")
        self.assertTrue(b)
        b = hasattr(tmodel, "bbb")
        self.assertFalse(b)
    
    def test_model_init(self):
        utc = datetime.datetime.utcnow()
        utc = utc.replace(microsecond=0)
        tmodel = self.TModel(f_str="abcdef", f_bool=False, f_int=99909, f_datetime=utc, f_float=999.019, e_u1='风华', e_x2=192)
        self.assertEqual(tmodel.f_str, "abcdef")
        self.assertEqual(tmodel.f_int, 99909)
        self.assertEqual(tmodel.f_float, 999.019)
        self.assertEqual(tmodel.f_bool, False)
        self.assertEqual(tmodel.f_datetime, utc)
        self.assertEqual(tmodel.e_u1, '风华')
        self.assertEqual(tmodel.e_x2, 192)
        
    def test_model_all(self):
        q = self.TModel.all()
        self.assertTrue(isinstance(q, BaseQuery))
    
    def test_length_validate(self):
        try:
            tmodel = self.TModel()
            tmodel.create()
            tmodel.f_v = "1213456789"
            tmodel.create()
            self.assertTrue(False)
        except Error, e:
            self.assertIsInstance(e, LengthError)
            
    def test_basemodel(self):
        class TBModel(BaseModel):
            
            @classmethod
            def meta_domain(cls):
                return "test"
        
            aaa = dao.IntegerProperty("aaa", required=True)
            
        TBModel.create_schema()
        tmodel1 = TBModel()
        tmodel1.aaa = 2
        tmodel1.create()
        query = TBModel.all()
        self.assertTrue(query.count(), 1)
        tmodel2 = query.get()
        self.assertEqual(tmodel1.aaa, tmodel2.aaa)
    
    def test_delete(self):
        query = self.TModel.all()
        tmodel = query.get()
        key = tmodel.get_keyvalue()
        tmodel.delete()
        if config.dbCFG.get_dbinfo(self.TModel).is_mongo():
            query.clear()
            ql = {'_id':key}
            query.ql(ql)
            result = query.count()
            self.assertEqual(result, 0)  
        else:
            query.clear()
            sql = "select * from %s where _id = $uid" % tmodel.get_modelname()
            query.ql(sql, {'uid':key})
            result = query.count()
            self.assertEqual(result, 0)
                  
    
    def test_delete_schema(self):
        self.TModel.delete_schema()
        result = self.TModel.has_schema()
        self.assertFalse(result)
        self.TModel.create_schema()
        
    @classmethod
    def tearDownClass(cls):
        cls.TModel.delete_schema()     
        sysprop.uninstall_module()   
        database.drop_db(config.dbCFG.get_root_dbinfo())
    
class BaseQueryTest(unittest.TestCase):
    class TModel1(BaseModel):
        @classmethod
        def meta_domain(cls):
            return "test"
        f_str = dao.StringProperty("fStr")
        f_int = dao.IntegerProperty("fInt")
        f_bool = dao.BooleanProperty("fBool")
        f_float = dao.FloatProperty("fFloat")
        f_date = dao.DateProperty("fDate")
        f_datetime = dao.DateTimeProperty("fDatetime", auto_utcnow=True)
        f_str1 = dao.StringProperty("fStr1", persistent=False)
        f_json = dao.DictProperty("fjson1")
        
    class TSubModel1(BaseModel):

        @classmethod
        def meta_domain(cls):
            return "test"
        
        t_sub_name = dao.StringProperty("tSubName")
        t_sub_bool = dao.BooleanProperty("tSubBool", default=True)
        t_model_id = dao.StringProperty("tModelId")
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        cls.TModel1.create_schema()
        cls.TSubModel1.create_schema()
        
    def test_filter_ex(self):
        query = self.TModel1().all()
        t1 = self.TModel1(f_str="dddd").create()
        t2 = self.TModel1(f_str="dddd2").create()
        t3 = self.TModel1(f_str="dddd3").create()
        query.filter("ex ex", 1)
        query.filter("ex ex", "'a'='a'", wrapper=False)
        try:
            i = query.count()
            self.assertEqual(i, 3)
        except ProgramError, e:
            if config.dbCFG.get_dbinfo(self.TModel1).is_mongo():
                self.assertIn("comparison ex", str(e))
        t1.delete()
        t2.delete()
        t3.delete()  
        
        
    def test_filter_is(self):
        query = self.TModel1().all()
        query.filter("f_int is", None)
        i = query.count()
        self.assertEqual(i, 0)
    
    def test_filter_is_not(self):
        query = self.TModel1().all()
        query.filter("f_int is not", None)
        i = query.count()
        self.assertEqual(i, 3)
    
    def test_filter_equal(self):
        tm = self.TModel1(f_int=1, f_str="abcd", f_bool=False, f_float=2.5, f_datetime=typeutils.utcnow()).create()
        tm2 = self.TModel1(f_bool=True).create()
        query = self.TModel1().all()
        query.filter("f_int =", 1)
        i = query.count()
        self.assertEqual(i, 1)
        tmodel = query.get()
        self.assertEqual(tmodel.f_str, "abcd")
        self.assertEqual(tmodel.f_int, 1)
        self.assertEqual(tmodel.f_bool, False)
        self.assertEqual(tmodel.f_float, 2.5)
        self.assertIsNotNone(tmodel.f_datetime)
        query.clear()
        query.filter("f_bool =", True)
        i = query.count()
        self.assertEqual(i, 1)
        tm.delete()
        tm2.delete()
    
    def test_filter_less_equal(self):
        query = self.TModel1.all()
        query.delete()
        t1 = self.TModel1(f_int=1, f_datetime=typeutils.utcnow()).create()
        t2 = self.TModel1(f_int=2, f_datetime=typeutils.utcnow()).create()
        t3 = self.TModel1(f_int=3, f_datetime=typeutils.utcnow()).create()
        query = self.TModel1().all()
        query.filter("f_int <", 2)
        i = query.count()
        self.assertEqual(i, 1)        
        query.filter("f_int <=", 2, replace=True)        
        i = query.count()
        self.assertEqual(i, 2)
        query.clear()
        query.filter("f_datetime <=", typeutils.utcnow() + timedelta(minutes=1))
        i = query.count()
        self.assertEqual(i, 3)
        t1.delete()
        t2.delete()
        t3.delete()
    
    def test_filter_more_equal(self):
        query = self.TModel1().all()
        query.delete()
        self.TModel1(f_int=11).create()
        self.TModel1(f_int=2).create()
        self.TModel1(f_int=13).create()
        query = self.TModel1().all()
        query.filter("f_int >", 2)
        i = query.count()
        self.assertEqual(i, 2)
        query.filter("f_int >=", 1, replace=True)
        query.clear()
        i = query.count()
        self.assertEqual(i, 3)
        
    def test_filter_replace(self):
        query = self.TModel1().all()
        query.delete()
        tm1 = self.TModel1(f_str="adfadf1", f_int=1).create()
        tm2 = self.TModel1(f_str="adfadf2", f_int=2).create()
        tm3 = self.TModel1(f_str="adfadf3", f_int=3).create()
        query.filter("f_int <", 2)
        i = query.count()
        self.assertEqual(i, 1)
        query.clear()
        query.filter("f_int <", 2)
        query.filter("f_int <=", 2, replace=False)
        i = query.count()
        self.assertEqual(i, 1)
        query.clear()
        query.filter("f_int <", 2)
        query.filter("f_int <=", 2, replace=True)
        i = query.count()
        self.assertEqual(i, 2)
        tm1.delete()
        tm2.delete()
        tm3.delete()
        
    def test_filter_not_equal(self):
        query = self.TModel1().all()
        query.delete()
        self.TModel1(f_int=1).create()
        self.TModel1(f_int=2).create()
        self.TModel1(f_int=3).create()
        query = self.TModel1().all()
        query.filter("f_int !=", 1)
        query.filter("f_int !=", 2)
        i = query.count()
        self.assertEqual(i, 1)
    
    def test_filter_in(self):
        query = self.TModel1().all()
        query.delete()
        self.TModel1(f_int=1).create()
        self.TModel1(f_int=2).create()
        self.TModel1(f_int=3).create()
        query = self.TModel1().all()
        query.filter("f_int in", [1, 2])
        i = query.count()
        self.assertEqual(i, 2)
        
        query.clear()
        query.filter('f_int in', [1, 3], replace=True)
        i = query.count()
        self.assertEqual(i, 2)
        
            
    def test_filter_in_sql(self):
        if config.dbCFG.get_dbinfo(self.TModel1).is_mongo():
            return None
        query = self.TModel1().all()
        query.clear()
        query.filter("f_int in", " (select 4)", wrapper=False)
        i = query.count()
        self.assertEqual(i, 0)
        try:
            query.clear()
            query.filter("f_int in", " (select 4)")
            i = query.count()
            self.assertTrue(False)
        except ProgramError, e:
            self.assertIn("Argument", str(e))
        
    def test_filter_not_in(self):
        query = self.TModel1().all()
        query.delete()
        self.TModel1(f_int=4).create()
        self.TModel1(f_int=5).create()
        self.TModel1(f_int=6).create()
        query = self.TModel1().all()
        query.filter("f_int not in", [1, 2])
        i = query.count()
        self.assertEqual(i, 3)
        
        
    
    def test_filter_not_in_sql(self):
        if config.dbCFG.get_dbinfo(self.TModel1).is_mongo():
            return None        
        query = self.TModel1().all()
        query.delete()
        t1 = self.TModel1(f_int=2).create()
        t2 = self.TModel1(f_int=3).create()
        query.filter("f_int not in", " (select 4)", wrapper=False)
        i = query.count()
        self.assertEqual(i, 2)
        try:
            query.clear()
            query.filter("f_int not in", " (select 4)")
            i = query.count()
            self.assertTrue(False)
        except ProgramError, e:
            self.assertIn("Argument", str(e))
        t1.delete()
        t2.delete()
    
    def test_filter_like(self):
        query = self.TModel1().all()
        query.delete()
        self.TModel1(f_str="2xd1").create()
        self.TModel1(f_str="dzzz").create()
        self.TModel1(f_str="xxxx").create()
        self.TModel1(f_int=23).create()
        self.TModel1(f_int=33).create()
        query = self.TModel1().all()
        query.filter("f_str like", '%d%')
        i = query.count()
        self.assertEqual(i, 2)
        query.clear()
        query.filter("f_str like", 'd%', replace=True)
        i = query.count()
        self.assertEqual(i, 1)
        query.clear()
        query.filter("f_str like", '%d', replace=True)
        i = query.count()
        self.assertEqual(i, 0)
    
    def test_filter_type(self):
        query = self.TModel1().all()
        try:
            query.filter("f_int =", 'a')
            self.assertTrue(False)
        except ProgramError, e:
            self.assertIn('is not the type', str(e))
        try:
            query.filter("f_str =", 2)
            self.assertTrue(False)
        except ProgramError, e:
            self.assertIn('is not the type', str(e))
        
        try:
            query.filter("f_datetime =", 'a')
            self.assertTrue(False)
        except ProgramError, e:
            self.assertIn('is not the type', str(e))
        
        try:
            query.filter("f_bool =", 'a')
            self.assertTrue(False)
        except ProgramError, e:
            self.assertIn('is not the type', str(e))
        
        try:
            query.filter("f_bool =", 1)
            self.assertTrue(True)
        except ProgramError, e:
            self.assertTrue(False)
        
    def test_filter_logic(self):
        tm = self.TModel1(f_int=1).create()
        tm2 = self.TModel1(f_int=2).create()
        tm3 = self.TModel1(f_int=3).create()
        query = self.TModel1().all()
        try:
            query.filter("f_str =", "a", logic="ax")
        except ProgramError, e:
            self.assertIn('is not and AND or', str(e))
        
        query.filter('f_int =', 1)
        query.filter('f_int =', 2, logic="or")
        i = query.count()
        self.assertEqual(i, 2)
        tm.delete()
        tm2.delete()
        tm3.delete()
    
    def test_filter_parenthesis(self):
        query = self.TModel1().all()
        try:
            query.filter("f_str =", "a", logic="ax")
        except ProgramError, e:
            self.assertIn('is not and AND or', str(e))
        query.clear()
        query.filter('f_int =', 1)
        query.filter('f_str =', 'abced', parenthesis='(')
        query.filter('f_str =', 'xfg', logic="or", parenthesis=')')
        i = query.count()
        self.assertEqual(i, 0)
        query.clear()
        query.filter('f_int =', 1, parenthesis="(")
        query.filter('f_str =', 'abced', parenthesis='(')
        query.filter('f_str =', 'xfg', logic="or", parenthesis='))')
        i = query.count()
        self.assertEqual(i, 0)
        
    def test_filter_x(self):
        query = self.TModel1().all()
        filter1 = [{'property_op':'f_int', 'value':1}, {'property_op':'f_str', 'value':'abced', 'parenthesis':'('}, {'property_op':'f_str', 'value':'xfg', 'parenthesis':')', 'logic':'or'}]
        query.filter_x(filter1)
        i = query.count()
        self.assertEqual(i, 0)
        query.clear()
        query.filter("f_str =", "a")
        query.filter_x(filter1, logic="or", parenthesis_left="(", parenthesis_right=")")
        i = query.count()
        self.assertEqual(i, 0)
    
    def test_has_filter(self):
        query = self.TModel1().all()
        query.filter('f_int =', 1)
        b = query.has_filter('f_int')
        self.assertTrue(b)
        b = query.has_filter('f_int', operator='=')
        self.assertTrue(b)
        b = query.has_filter('f_int', operator='>')
        self.assertFalse(b)
        
    def test_filter_illegal(self):
        query = self.TModel1().all()
        try:
            query.filter("f_str -a", "abcd")
        except ProgramError, e:
            self.assertIn("includes the illegal operator", str(e))
        query = self.TModel1().all()
        try:
            query.filter("f_str1 =", "abcd")
            self.assertTrue(False)
        except ProgramError, e:
            self.assertIn("persistent", str(e))
    
    def test_filter_wrapper(self):
        query = self.TModel1.all(alias="a")
        query.filter("a._id =", "b.t_id")
        query.what("a._id", "uid")
        try:
            query.filter("a.f_str =", 'abcd', wrapper=False)
            query.clear()
            query.fetch()
        except Exception:
            self.assertIn("Unknown column 'abcd", traceback.format_exc())
        
        query = self.TModel1.all("a")
        query.filter("a.f_date  =", dao.DateProperty.utctoday())
        query.fetch(1)
        self.assertTrue(True)
        query.filter("a.f_datetime  =", dao.DateTimeProperty.utcnow())
        query.clear()
        query.fetch(1)
        self.assertTrue(True)
    
    def test_order(self):
        query = self.TModel1().all()
        query.delete()
        self.TModel1(f_int=1).create()
        self.TModel1(f_int=2).create()
        self.TModel1(f_int=3).create()
        query.order("f_int")
        tmodel = query.get()
        self.assertEqual(tmodel.f_int, 1)
        query = self.TModel1().all()
        query.order("-f_int")
        tmodel = query.get()
        self.assertEqual(tmodel.f_int, 3)
    
    def test_alias(self):
        tm = self.TModel1(f_int=1).create()
        query = self.TModel1.all(alias="a")
        query.filter("a.f_int =", 1)
        i = query.count()
        self.assertEqual(i, 1)
        query = self.TModel1.all()
        query.filter("f_int =", 1)
        i = query.count()
        self.assertEqual(i, 1)
        query = self.TModel1.all(alias="b")
        query.what("b._id")
        query.filter("b.f_int =", 1)
        i = query.count()
        self.assertEqual(i, 1)
        
        query.what("b.f_int", "cccc")
        m = query.get()
        if config.dbCFG.get_dbinfo(self.TModel1).is_mongo():
            self.assertEqual(m.f_int, 1)
        else:
            self.assertEqual(m.cccc, 1)
        tm.delete()
    
    def test_what(self):
        query = self.TModel1().all("a")
        query.delete()
        query = self.TModel1().all("a")
        self.TModel1(f_int=1, f_str="abcd").create()
        query.what("a.f_int")
        query.what("a.f_str")
        query.filter("a.f_int =", 1)
        result = query.get()
        self.assertEqual(result.f_int, 1)
        self.assertEqual(result.f_str, 'abcd')
        query = self.TModel1().all("a")
        query.what("a.f_int", 'fint')
        query.what("a.f_str", "fstr")
        query.filter("a.f_int =", 1)
        result = query.get()
        if config.dbCFG.get_dbinfo(self.TSubModel1).is_mongo():
            self.assertIsNotNone(result.f_int)
            self.assertIsNotNone(result.f_str)
            self.assertEqual(len(result._extproperties), 0)
        else:
            self.assertIsNone(result.f_int)
            self.assertIsNone(result.f_str)
            self.assertEqual(result.fstr, 'abcd')
            self.assertEqual(result.fint, 1)
            self.assertEqual(len(result._extproperties), 2)
    
    def test_distinct(self):
        """"""
        
    def test_group(self):
        query = self.TSubModel1.all()
        query.delete()
        t1 = self.TSubModel1(t_sub_name="_sub_xxx", t_model_id='2').create()
        t2 = self.TSubModel1(t_sub_name="_sub_yyy", t_model_id='1').create()
        if config.dbCFG.get_dbinfo(self.TSubModel1).is_mongo():
            query = self.TSubModel1.all()
            query.group([{ "$group": { "_id": None, "count": { "$sum": 1 } } }])
            result = query.count()
            self.assertEqual(result, 2)
        else:
            query = self.TSubModel1.all()
            query.what("t_model_id")
            query.what("count(*)", "num")
            query.group("t_model_id having num >= 0")
            query.order("-t_model_id")
            i = len(query.fetch())
            self.assertEqual(i, 2)
        t1.delete()
        t2.delete()
        
    def test_sql(self):
        if config.dbCFG.get_dbinfo(self.TModel1).is_mongo():
            return None
        query = self.TSubModel1.all("a")
        query.delete()
        t1 = self.TSubModel1(t_sub_name="a_sub_xy").create()
        t2 = self.TSubModel1(t_sub_name="c_sub_ccxy").create()
        t3 = self.TSubModel1(t_sub_name="a_subeexy").create()
        t4 = self.TSubModel1(t_sub_name="a_subbaxy").create()
        t5 = self.TSubModel1(t_sub_name="bba_swubbaxy").create()
        query.ql("select * from %s where t_sub_name like $tname" % self.TSubModel1.get_modelname(), {'tname':"%sub%"})
        i = query.count()
        self.assertEqual(i, 4)
        result = query.get()
        self.assertTrue(isinstance(result.t_sub_bool, bool))
        self.assertEqual(result.t_sub_bool, True)        
        query = self.TSubModel1.all()
        query.ql("select * from %s where t_sub_name like $tname" % self.TSubModel1.get_modelname(), {'tname':"%sub%"})
        result = query.get(metadata={"t_sub_bool":dao.BooleanProperty("tsubbool")})
        self.assertTrue(isinstance(result.t_sub_bool, bool))
        self.assertEqual(result.t_sub_bool, True)
        t1.delete()
        t2.delete()
        t3.delete()
        t4.delete()
        t5.delete()
    
    def test_delete(self):
        query = self.TSubModel1.all()
        query.delete()
        self.TSubModel1(t_sub_name="_sub_xxx").create()
        self.TSubModel1(t_sub_name="_sub_yyy").create()
        self.TSubModel1(t_sub_name="asee").create()
        query.filter("t_sub_name like", "%_sub_%")
        result = query.delete()
        self.assertEqual(result, 2)
        query.clear()
        if not config.dbCFG.get_dbinfo(self.TSubModel1).is_mongo():
            query.ql("delete from %s where t_sub_name = '_sub_'" % self.TSubModel1.get_modelname())
            query.delete()
        
    def test_update(self):
        tmodel = self.TModel1()
        tmodel.f_int = 10000
        tmodel.f_float = 1.0
        tmodel.f_str = "ccccupdate"
        tmodel.create()
        query = tmodel.all()
        try:
            query.set("f_float", "2a.0")
            self.assertTrue(False)
        except TypeFloatError:
            self.assertTrue(True)
        query.set("f_str", "dddupdate")
        query.set("f_datetime", datetime.datetime.utcnow())
        query.filter("f_int =", 10000)
        query.update()
        query = self.TModel1.all()
        query.filter("f_int =", 10000)
        tm = query.get()
        self.assertEqual(tm.f_str, "dddupdate")
        query = tmodel.all()
        query.set("f_int inc", 2)
        query.set("f_float mul", 3.0)
        query.set("f_str set", "setsetup")
        query.filter("f_int =", 10000)
        query.update()
        tm23 = self.TModel1.get_by_key(tm.key())
        self.assertEqual(tm23.f_int, 10002)
        self.assertEqual(tm23.f_float, 3.0)
        self.assertEqual(tm23.f_str, 'setsetup')
        
    
    def test_find_one_and_update(self):
        tmodel = self.TModel1()
        tmodel.f_int = 200000
        tmodel.f_float = 1.0
        tmodel.f_str = "ccccupdatccccce"
        tmodel.create().key()
        tmodel = self.TModel1()
        tmodel.f_int = 300000
        tmodel.f_float = 1.0
        tmodel.f_str = "32323dadsasddf23"
        query = self.TModel1.all()
        query.filter("f_int >=", 150000)
        query.order("f_int")
        query.set("f_str", "uuppa")
        m2 = query.find_one_and_update()
        self.assertEqual(m2.f_str, "ccccupdatccccce")
        query = self.TModel1.all()
        query.filter("f_int >=", 4450000)
        query.set("f_str", "uuppa")
        m2 = query.find_one_and_update()
        self.assertIsNone(m2, None)
        tmodel = self.TModel1()
        tmodel.f_int = 800000
        tmodel.f_float = 8.8
        tmodel.f_str = "aaa"
        key = tmodel.create().key()
        query = tmodel.all()
        query.set("f_int inc", 222)
        query.set("f_float mul", 3.0)
        query.set("f_str set", "ccaaedd")
        query.filter("f_int =", 800000)
        query.update()
        tm23 = self.TModel1.get_by_key(key)
        self.assertEqual(tm23.f_int, 800000 + 222)
        self.assertEqual(round(tm23.f_float, 1), round(8.8 * 3.0, 1))
        self.assertEqual(tm23.f_str, 'ccaaedd')
    
    def test_find_one_and_delete(self):
        tmodel = self.TModel1()
        tmodel.f_int = 300000
        tmodel.f_float = 1.0
        tmodel.f_str = "32323dadsasddf23"
        id3 = tmodel.create().key()
        query = self.TModel1.all()
        query.filter("f_int >=", 150000)        
        query.order("-f_int")
        m2 = query.find_one_and_delete()
        self.assertEqual(m2.f_str, "32323dadsasddf23")
        tm3 = self.TModel1.get_by_key(id3)
        self.assertIsNone(tm3, None)
        query = self.TModel1.all()
        query.filter("f_int >=", 1150000)
        query.set("f_str", "uuppccca")
        m21 = query.find_one_and_update()
        self.assertIsNone(m21, None)
        query.filter("f_int >=", 2150000)        
        m21 = query.find_one_and_delete()
        self.assertIsNone(m21, None)
        
        
        
    def test_mocallback(self):
        tmodel = self.TModel1()
        tmodel.f_str = "testmodelproc"
        tmodel.f_int = 8
        tmodel.create()
        query = self.TModel1().all()
        query.filter("f_str =", "testmodelproc")
        mp = "aaaabbbb"
        def mproc(tm):
            tm.mp = mp
        results = query.fetch(mocallback=mproc)
        self.assertEqual(results[0].mp, "aaaabbbb")
        query.clear()
        query.filter("f_str =", "testmodelproc")
        self.assertEqual(query.get(mocallback=mproc).mp, "aaaabbbb")
        query.delete()
        
    def test_model_to_dict(self):
        tmodel = self.TModel1()
        dic = tmodel.to_dict()
        self.assertEqual(type(dic), dict)
    
    @classmethod
    def tearDownClass(cls):
        cls.TModel1.delete_schema()
        cls.TSubModel1.delete_schema()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())

class ModelTest(unittest.TestCase):
    
    class TTTModel(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        f_str = dao.StringProperty("fStr")
        f_int = dao.IntegerProperty("fInt")
        f_bool = dao.BooleanProperty("fBool")
        f_float = dao.FloatProperty("fFloat")
        f_date = dao.DateProperty("fDate")
        f_datetime = dao.DateTimeProperty("fDatetime")
        f_v = dao.StringProperty("fV", length=8)
        f_str1 = dao.StringProperty("fStr1", persistent=False)
        f_str_logged = dao.StringProperty("fStrLogged", logged=True)
        f_float_logged = dao.FloatProperty("fFloatLogged", logged=True)
        f_json = dao.DictProperty("fJson")
        f_obj = dao.ObjectProperty("fObj")
    
    class TModel22(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        tstr = dao.StringProperty("tStr")
        
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        cls.TTTModel.create_schema()
        
        cls.TModel22.create_schema()
    def test_create(self):
        tmodel = self.TTTModel()
        try:
            tmodel.create()
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)
        tmodel.create('2')
        tmodel2 = self.TTTModel.get_by_key(tmodel.key())
        self.assertEqual(tmodel2.modified_by, '2')
        self.assertIsNotNone(tmodel2.modified_time)
        self.assertIsNotNone(tmodel2.created_time)
        
    def test_update(self):
        tmodel = self.TTTModel()
        tmodel.create(2)
        try:
            tmodel.update()
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)
        tmodel2 = self.TTTModel.get_by_key(tmodel.key())
        time.sleep(1)
        tmodel2.update(2)
        tmodel3 = self.TTTModel.get_by_key(tmodel.key())
        self.assertGreater(tmodel3.modified_time, tmodel.modified_time)
        
    def test_delete(self):
        tmodel = self.TTTModel()
        tmodel.create(2)
        try:
            tmodel.delete()
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)
        
        tmodel2 = self.TTTModel.get_by_key(tmodel.get_keyvalue())
        self.assertIsNotNone(tmodel2)
        tmodel.delete(2)
        
        tmodel2 = self.TTTModel.get_by_key(tmodel.get_keyvalue())
        self.assertIsNone(tmodel2)
        
    def test_get_by_key(self):
        tmodel = self.TModel22(tstr="eeee")
        tmodel.create(2)
        tmodel2 = tmodel.get_by_key(tmodel.key())
        self.assertEqual(tmodel.tstr, tmodel2.tstr)
        
    def test_find_one_and_update(self):
        modified_time = typeutils.utcnow() - timedelta(minutes=1)
        tmodel = self.TTTModel()
        tmodel.f_int = 200000
        tmodel.f_float = 1.0
        tmodel.f_str = "131ddd"
        id1 = tmodel.create("modifer11").key()
        query = self.TTTModel.all()
        query.filter("f_int >=", 150000)
        query.set("f_str", "caaee")
        query.set("f_json", {'a':1, 'b':'b'}) 
        m2 = query.find_one_and_update("modifer22")
        self.assertEqual(m2.f_str, "131ddd")
        self.assertEqual(m2.f_json, None)
        query.set("f_json", {'a':1, 'b':'8'})
        m3 = query.find_one_and_update("modifer23", new=True)
        self.assertEqual(m3.f_json, {'a':1, 'b':'8'}) 
        mnew = self.TTTModel().get_by_key(id1)
        self.assertEqual(mnew.modified_by, "modifer23")
        self.assertGreaterEqual(mnew.modified_time, modified_time)
    
    def test_save_objectproperty(self):
        tmodel = self.TTTModel()
        tmodel.f_obj= dao.RangeValidator(2,5)
        key = tmodel.create(None).key()
        t2 = self.TTTModel().get_by_key(key)
        self.assertIsInstance(t2.f_obj, dao.RangeValidator)
        try:
            t2.f_obj.validate(10,"zzz")
        except Exception,e:
            self.assertIsInstance(e, RangeError)
        
    
    @classmethod
    def tearDownClass(cls):
        cls.TTTModel.delete_schema()    
        cls.TModel22.delete_schema()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())
    
class QueryTest(unittest.TestCase):
    class TModelQT(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        f_str = dao.StringProperty("fStr", logged=True)
        f_str1 = dao.StringProperty("fStr1")
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        cls.TModelQT.create_schema();        
    
    def test_update(self):
        
        try:
            query = self.TModelQT.all()
            query.set("f_str", "ccc")
            query.update(2)
            self.assertTrue(False)
        except ProgramError:
            self.assertTrue(True)
        
        tm = self.TModelQT().create(3)
        query = self.TModelQT.all() 
        query.set("f_str1", "cccc")
        query.filter("_id =", tm.key())
        query.update(2)         
        query.filter("modified_by =", "2");
        query.filter("_id =", tm.key())
        self.assertEqual(query.count(), 1)
    
            
    def test_delete(self):
        query = self.TModelQT.all()
        query.delete(None)
            
    @classmethod
    def tearDownClass(cls):
        cls.TModelQT.delete_schema()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())
