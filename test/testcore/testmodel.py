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
import time
import traceback
import unittest

from core import properti
from core.db import dbutil
from core.error import CoreError, TypeFloatError
from core.model import Uid, BaseModel, BaseQuery, stdModel, Model, MCLog, \
    MCLogDetail


class ModelTestSuit(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self)
        
        modeltestsuit = unittest.makeSuite(UidTest, 'test')
        self.addTest(modeltestsuit)
        modeltestsuit = unittest.makeSuite(BaseModelTest, 'test')
        self.addTest(modeltestsuit)
        basequerytestsuit = unittest.makeSuite(BaseQueryTest, 'test')
        self.addTest(basequerytestsuit)
        modeltestsuit = unittest.makeSuite(ModelTest, 'test')
        self.addTest(modeltestsuit)
        querytestsuit = unittest.makeSuite(QueryTest, 'test')
        self.addTest(querytestsuit)
        
        
        
        
        

class UidTest(unittest.TestCase):

    def test01Key(self):
        class TModel(BaseModel):
            MODULE = "test"
            f_str = properti.StringProperty("fstr")
        uid = Uid.new_id(TModel)
        self.assertIsNotNone(uid)
        
class BaseModelTest(unittest.TestCase):
    
    class TModel(BaseModel):
        MODULE = "test"
        f_str = properti.StringProperty("fStr")
        f_int = properti.IntegerProperty("fInt")
        f_bool = properti.BooleanProperty("fBool")
        f_float = properti.FloatProperty("fFloat")
        f_date = properti.DateProperty("fDate")
        f_datetime = properti.DateTimeProperty("fDatetime")
        f_blob = properti.BlobProperty("fBlob")
        f_v = properti.StringProperty("fV", length=8)
        f_str1 = properti.StringProperty("fStr1", persistent=False)
        
    @classmethod
    def setUpClass(cls):
        cls.TModel().create_table()
    
    def test01CreateAndGetById(self):
        tmodel = self.TModel()
        tmodel.f_str = "abcd"
        tmodel.f_int = 100
        tmodel.f_float = 1000.0
        tmodel.f_bool = False
        tmodel.f_date = properti.DateProperty.utctoday()
        utc = datetime.datetime.utcnow()
        utc = utc.replace(microsecond=0)
        tmodel.f_datetime = utc
        tmodel.create()
        self.assertIsNotNone(tmodel.get_keyvalue())
        self.assertNotEqual(tmodel.get_keyvalue(), 0)
        sql = "select uid from core_uid where model_name = $mn"
        result = dbutil.get_dbconn().query(sql, vars={'mn':tmodel.get_modelname()})
        self.assertEqual(result[0].uid, tmodel.get_keyvalue())
        tmodel2 = self.TModel.get_by_key(tmodel.get_keyvalue())
        self.assertEqual(tmodel.f_str, tmodel2.f_str)
        self.assertEqual(tmodel.f_int, tmodel2.f_int)
        self.assertEqual(tmodel.f_float, tmodel2.f_float)
        self.assertEqual(tmodel.f_bool, tmodel2.f_bool)
        self.assertEqual(utc, tmodel2.f_datetime)
        self.assertEqual(properti.DateProperty.utctoday(), tmodel2.f_date)
        
    def test04ModelExtProperties(self):
        query = self.TModel.all()
        query.what("uid", "u1")
        query.what("f_str", "s1")
        query.what("f_bool", "b1")
        tmodel = query.get()
        extprops = tmodel._extproperties
        self.assertTrue(extprops.has_key('u1'))
        self.assertTrue(extprops.has_key('s1'))
        self.assertTrue(extprops.has_key('b1'))
        self.assertEqual(len(extprops.keys()), 3)
        
    def test05ModelProperties(self):
        props = self.TModel.get_properties()
        self.assertTrue(props.has_key('f_str'))
        self.assertTrue(props.has_key('f_int'))
        self.assertTrue(props.has_key('f_bool'))
        self.assertTrue(props.has_key('f_float'))
        self.assertTrue(props.has_key('f_datetime'))
        self.assertTrue(props.has_key('f_date'))
        self.assertTrue(props.has_key('uid'))
        self.assertTrue(props.has_key('f_blob'))
        self.assertTrue(props.has_key('f_str1'))
        self.assertEqual(len(props.keys()), 10)
    
    def test06GetProperties(self):
        props = self.TModel.get_properties(persistent=True)
        self.assertEqual(len(props.keys()), 9)
        props = self.TModel.get_properties(persistent=False)
        self.assertEqual(len(props.keys()), 1)
        
    def test07IsPersistent(self):
        self.assertTrue(self.TModel.is_persistent("f_str"))
        self.assertFalse(self.TModel.is_persistent("f_str1"))
        self.assertTrue(self.TModel.is_persistent())
        
    def test08HasProp(self):
        tmodel = self.TModel(a="ccc")
        b = hasattr(tmodel, "a")
        self.assertTrue(b)
        b = hasattr(tmodel, "bbb")
        self.assertFalse(b)
    
    def testModelInit(self):
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
        
    def testModelAll(self):
        q = self.TModel.all()
        self.assertTrue(isinstance(q, BaseQuery))
    
    def test07ModelStd(self):
        tmodel = self.TModel()
        tmodel.f_str = "abcd"
        tmodel.f_int = 100
        tmodel.f_float = 1000.0
        tmodel.f_bool = False
        utc = datetime.datetime.utcnow()
        utc = utc.replace(microsecond=0)
        tmodel.f_datetime = utc
        tmodel.f_date = datetime.date(utc.year, utc.month, utc.day)
        tmodel.put()
        query = stdModel.all()
        query.model(self.TModel.get_modelname(), "a")
        try:
            query.filter("uid =", tmodel.get_keyvalue())
            self.assertFalse(True)
        except CoreError, e:
            self.assertIn("alias name", str(e))
        
        query.filter("a.uid =", tmodel.get_keyvalue())
        try:
            tmodel = query.get()
            self.assertFalse(True)
        except CoreError, e:
            self.assertIn("what", str(e))
        
        query.what("a.uid")
        tmodel = query.get()
        self.assertTrue(isinstance(tmodel, stdModel))
    
    
            
    def test97LengthValidate(self):
        try:
            tmodel = self.TModel()
            tmodel.put()
            tmodel.f_v = "1213456789"
            tmodel.put()
            self.assertTrue(False)
        except CoreError:
            self.assertTrue(True)
            
    def testBaseModel(self):
        class TBModel(BaseModel):
            MODULE = "test"
            KEYMETA = ("aaa", False)
            aaa = properti.IntegerProperty("aaa", required=True)
            
        TBModel.create_table()
        tmodel1 = TBModel()
        tmodel1.aaa = 2
        tmodel1.create()
        query = TBModel.all()
        self.assertTrue(query.count(), 1)
        tmodel2 = query.get()
        self.assertEqual(tmodel1.aaa, tmodel2.aaa)
    
    def test98ModelDelete(self):
        tmodel = self.TModel.all().get()
        key = tmodel.get_keyvalue()
        tmodel.delete()
        sql = "select * from %s where uid = $uid" % tmodel.get_modelname()
        result = dbutil.get_dbconn().query(sql, vars={'uid':key})
        self.assertEqual(len(result), 0)            
    
    def test99ModelDelete(self):
        self.TModel.delete_table()
        sql = "SHOW TABLES LIKE '%s'" % self.TModel.get_modelname()
        result = dbutil.get_dbconn().query(sql)
        self.assertEqual(len(result), 0)
        
        

class BaseQueryTest(unittest.TestCase):
    class TModel(BaseModel):
        MODULE = "test"
        f_str = properti.StringProperty("fStr")
        f_int = properti.IntegerProperty("fInt")
        f_bool = properti.BooleanProperty("fBool")
        f_float = properti.FloatProperty("fFloat")
        f_date = properti.DateProperty("fDate")
        f_datetime = properti.DateTimeProperty("fDatetime", auto_utcnow=True)
        f_str1 = properti.StringProperty("fStr1", persistent=False)
        
    class TSubModel(BaseModel):
        MODULE = "test"
        t_id = properti.IntegerProperty("tId")
        t_sub_name = properti.StringProperty("tSubName")
        t_sub_bool = properti.BooleanProperty("tSubBool", default=True)
        t_model_id = properti.IntegerProperty("tModelId")
    
    @classmethod
    def setUpClass(cls):
        
        cls.TModel.create_table()
        cls.TSubModel.create_table()
        tmodel_1 = cls.TModel(f_str="abcd", f_int=1, f_bool=False, f_float=2.5)
        tmodel_2 = cls.TModel(f_str="efghd", f_int=2, f_bool=False, f_float=3.5)
        tmodel_1.put()
        for i in range(0, 5):
            tsub = cls.TSubModel(t_id=tmodel_1.get_keyvalue(), t_sub_name="1_sub_%d" % i)
            tsub.put()
        tmodel_2.put()
        for i in range(0, 2):
            tsub = cls.TSubModel(t_id=tmodel_2.get_keyvalue(), t_sub_name="2_sub_%d" % i)
            tsub.put()
        tmodel_3 = cls.TModel(f_str="xfg", f_int=5, f_bool=True, f_float=5.5)
        tmodel_3.put()
        
    def testFilterEx(self):
        query = self.TModel().all()
        query.filter("ex ex", 1)
        query.filter("ex ex", "'a'='a'", wrapper=False)
        i = query.count()
        self.assertEqual(i, 3)
        
    def testFilterIs(self):
        query = self.TModel().all()
        query.filter("f_int is", None, wrapper=False)
        i = query.count()
        self.assertEqual(i, 0)
    
    def testFilterEqual(self):
        query = self.TModel().all()
        query.filter("f_int =", 1)
        i = query.count()
        self.assertEqual(i, 1)
        tmodel = query.get()
        self.assertEqual(tmodel.f_str, "abcd")
        self.assertEqual(tmodel.f_int, 1)
        self.assertEqual(tmodel.f_bool, False)
        self.assertEqual(tmodel.f_float, 2.5)
        self.assertIsNotNone(tmodel.f_datetime)
    
    def testFilterLessEqual(self):
        query = self.TModel().all()
        query.filter("f_int <", 2)
        i = query.count()
        self.assertEqual(i, 1)
        query.filter("f_int <=", 2, replace=True)
        query.clear()
        i = query.count()
        self.assertEqual(i, 3)
        query.clear()
        query.filter("f_datetime <=", datetime.datetime.utcnow())
        i = query.count()
        self.assertEqual(i, 3)
    
    def testFilterMoreEqual(self):
        query = self.TModel().all()
        query.filter("f_int >", 2)
        i = query.count()
        self.assertEqual(i, 1)
        query.filter("f_int >=", 1, replace=True)
        query.clear()
        i = query.count()
        self.assertEqual(i, 3)
        
    def testFilterReplace(self):
        query = self.TModel().all()
        query.filter("f_int <", 2)
        i = query.count()
        self.assertEqual(i, 1)
        query.filter("f_int <=", 2, replace=False)
        query.clear()
        i = query.count()
        self.assertEqual(i, 3)
        
    def testFilterNotEqual(self):
        query = self.TModel().all()
        query.filter("f_int !=", 1)
        query.filter("f_int !=", 2)
        i = query.count()
        self.assertEqual(i, 1)
    
    def testFilterIn(self):
        query = self.TModel().all()
        query.filter("f_int in", [1, 2])
        i = query.count()
        self.assertEqual(i, 2)
        
        query.clear()
        query.filter('f_int in', [1, 3], replace=True)
        i = query.count()
        self.assertEqual(i, 1)
        
        query.clear()
        query.filter("f_int in", " (select 4)", wrapper=False)
        i = query.count()
        self.assertEqual(i, 0)
        try:
            query.clear()
            query.filter("f_int in", " (select 4)")
            i = query.count()
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn("Argument", str(e))
        
    def testFilterNotIn(self):
        query = self.TModel().all()
        query.filter("f_int not in", [1, 2])
        i = query.count()
        self.assertEqual(i, 1)
        
        query.clear()
        query.filter("f_int not in", " (select 4)", wrapper=False)
        i = query.count()
        self.assertEqual(i, 3)
        try:
            query.clear()
            query.filter("f_int not in", " (select 4)")
            i = query.count()
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn("Argument", str(e))
        
    def testFilterLike(self):
        query = self.TModel().all()
        query.filter("f_str like", '%d%')
        i = query.count()
        self.assertEqual(i, 2)
        query.clear()
        query.filter("f_str like", 'd%', replace=True)
        i = query.count()
        self.assertEqual(i, 0)
        query.clear()
        query.filter("f_str like", '%d', replace=True)
        i = query.count()
        self.assertEqual(i, 2)
    
    def testFilterType(self):
        query = self.TModel().all()
        try:
            query.filter("f_int =", 'a')
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn('is not the type', str(e))
        try:
            query.filter("f_str =", 2)
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn('is not the type', str(e))
        
        try:
            query.filter("f_datetime =", 'a')
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn('is not the type', str(e))
        
        try:
            query.filter("f_bool =", 'a')
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn('is not the type', str(e))
        
        try:
            query.filter("f_bool =", 1)
            self.assertTrue(True)
        except CoreError, e:
            self.assertTrue(False)
        
    def testFilterLogic(self):
        query = self.TModel().all()
        try:
            query.filter("f_str =", "a", logic="ax")
        except CoreError, e:
            self.assertIn('is not and AND or', str(e))
        
        query.filter('f_int =', 1)
        query.filter('f_int =', 2, logic="or")
        i = query.count()
        self.assertEqual(i, 2)
    
    def testFilterParenthesis(self):
        query = self.TModel().all()
        try:
            query.filter("f_str =", "a", logic="ax")
        except CoreError, e:
            self.assertIn('is not and AND or', str(e))
        
        query.filter('f_int =', 1)
        query.filter('f_str =', 'abced', parenthesis='(')
        query.filter('f_str =', 'xfg', logic="or", parenthesis=')')
        i = query.count()
        self.assertEqual(i, 0)
        
    def testHasFilter(self):
        query = self.TModel().all()
        query.filter('f_int =', 1)
        b = query.has_filter('f_int')
        self.assertTrue(b)
        b = query.has_filter('f_int', operator='=')
        self.assertTrue(b)
        b = query.has_filter('f_int', operator='>')
        self.assertFalse(b)
        
    def testFilterIllegal(self):
        query = self.TModel().all()
        try:
            query.filter("f_str -a", "abcd")
        except CoreError, e:
            self.assertIn("includes the illegal operator", str(e))
        query = self.TModel().all()
        try:
            query.filter("f_str1 =", "abcd")
            self.assertTrue(False)
        except CoreError, e:
            self.assertIn("persistent", str(e))
    
        
    def testFilterWrapper(self):
        query = stdModel().all()
        query.model(self.TModel.get_modelname(), 'a')
        query.model(self.TSubModel.get_modelname(), 'b')
        query.filter("a.uid =", "b.t_id")
        query.what("a.uid", "uid")
        i = query.count()
        self.assertEqual(i, 0)
        query.filter("a.uid =", 'b.t_id', wrapper=False, replace=True)
        query.clear()
        i = query.count()
        self.assertEqual(i, 21)
        try:
            query.filter("a.f_str =", 'abcd', wrapper=False)
            query.clear()
            query.fetch()
        except Exception:
            self.assertIn("Unknown column 'abcd", traceback.format_exc())
        
        query = self.TModel.all("a")
        query.filter("a.f_date  =", properti.DateProperty.utctoday())
        query.fetch(1)
        self.assertTrue(True)
        query.filter("a.f_datetime  =", properti.DateTimeProperty.utcnow())
        query.clear()
        query.fetch(1)
        self.assertTrue(True)
    
    def testOrder(self):
        query = self.TModel().all()
        query.order("f_int")
        tmodel = query.get()
        self.assertEqual(tmodel.f_int, 1)
        query = self.TModel().all()
        query.order("-f_int")
        tmodel = query.get()
        self.assertEqual(tmodel.f_int, 5)
    
    def testAlias(self):
        query = self.TModel.all(alias="a")
        query.filter("a.f_int =", 1)
        i = query.count()
        self.assertEqual(i, 1)
        query = self.TModel.all()
        query.filter("f_int =", 1)
        i = query.count()
        self.assertEqual(i, 1)
        query = stdModel.all()
        query.what("b.uid")
        query.model(self.TModel.get_modelname(), 'b')
        query.filter("b.f_int =", 1)
        i = query.count()
        self.assertEqual(i, 1)
        
        query.what("b.f_int", "cccc")
        m = query.get()
        self.assertEqual(m.cccc, 1)
    
    def testWhat(self):
        query = stdModel.all()
        query.model(self.TModel.get_modelname(), 'a')
        query.what("a.f_int")
        query.what("a.f_str")
        query.filter("a.f_int =", 1)
        result = query.get()
        self.assertEqual(len(result._extproperties), 2)
        self.assertIn("f_int", result._extproperties)
        self.assertIn("f_str", result._extproperties)
        query = self.TModel().all("a")
        query.what("a.f_int")
        query.what("a.f_str")
        query.filter("a.f_int =", 1)
        result = query.get()
        self.assertEqual(result.f_int, 1)
        self.assertEqual(result.f_str, 'abcd')
        query = self.TModel().all("a")
        query.what("a.f_int", 'fint')
        query.what("a.f_str", "fstr")
        query.filter("a.f_int =", 1)
        result = query.get()
        self.assertIsNone(result.f_int, None)
        self.assertIsNone(result.f_str, None)
        self.assertEqual(result.fstr, 'abcd')
        self.assertEqual(result.fint, 1)
        self.assertEqual(len(result._extproperties), 2)
        
        
    def testGroup(self):
        query = self.TSubModel.all()
        query.what("t_id")
        query.what("count(*)", "num")
        query.group("t_id")
        query.order("-t_id")
        i = len(query.fetch())
        self.assertEqual(i, 2)
        result = query.get()
        self.assertEqual(result.num, 2)
        
    def testJoin(self):
        query = self.TModel.all(alias="a")
        query.model(self.TSubModel.get_modelname(), "b")
        query.filter("a.uid = ", "b.t_model_id", wrapper=False)
        results = query.fetch()
        self.assertEqual(len(results), 0)
        query = self.TModel.all("a")
        query.model(self.TSubModel.get_modelname(), "b")
        query.filter("a.uid = ", "b.t_model_id", wrapper=False)
        results = query.fetch()
        self.assertEqual(len(results), 0)
        
    def testModel(self):
        query = self.TModel.all("a")
        try:
            query.model(self.TSubModel.get_modelname(), "b", join="l", on="")
            self.assertTrue(False)
        except:
            self.assertTrue(True)
        query.model(self.TSubModel.get_modelname(), "b", join="left", on="")
        self.assertTrue(True)
        
    def testGetModelAlias(self):
        query = self.TModel.all("a")
        query.model(self.TSubModel.get_modelname(), "b", join="left", on="")
        alias = query.get_model_alias(self.TSubModel.get_modelname())
        self.assertEqual(alias, "b")
        query = self.TModel.all("a")
        alias = query.get_model_alias(self.TModel.get_modelname())
        self.assertEqual(alias, "a")
    
    def testSQL(self):
        query = self.TSubModel.all("a")
        query.sql("select * from %s where t_sub_name like $tname" % self.TSubModel.get_modelname(), sql_vars={'tname':"%_sub_%"})
        i = query.count()
        self.assertEqual(i, 7)
        result = query.get()
        self.assertTrue(isinstance(result.t_sub_bool, bool))
        self.assertEqual(result.t_sub_bool, True)
        query = stdModel.all()
        query.sql("select * from %s where t_sub_name like $tname" % self.TSubModel.get_modelname(), sql_vars={'tname':"%_sub_%"})
        self.assertEqual(i, 7)
        result = query.get()
        self.assertFalse(isinstance(result.t_sub_bool, bool))
        self.assertEqual(result.t_sub_bool, True)
        query = stdModel.all()
        query.sql("select * from %s where t_sub_name like $tname" % self.TSubModel.get_modelname(), sql_vars={'tname':"%_sub_%"})
        result = query.get(metadata={"t_sub_bool":properti.BooleanProperty("tsubbool")})
        self.assertTrue(isinstance(result.t_sub_bool, bool))
        self.assertEqual(result.t_sub_bool, True)
    
    
    def testZZZDelete(self):
        query = self.TSubModel.all()
        query.filter("t_sub_name like", "%_sub_%")
        result = query.delete()
        self.assertEqual(result, 7)
        
    def testUpdate(self):
        tmodel = self.TModel()
        tmodel.f_int = 10000
        tmodel.f_float = 1.0
        tmodel.f_str = "ccccupdate"
        tmodel.put()
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
        query = self.TModel.all()
        query.filter("f_int =", 10000)
        tm = query.get()
        self.assertEqual(tm.f_str, "dddupdate")
    
    def testModelProc(self):
        tmodel = self.TModel()
        tmodel.f_str = "testmodelproc"
        tmodel.put()
        query = self.TModel().all()
        query.filter("f_str =", "testmodelproc")
        mp = "aaaabbbb"
        def mproc(tm):
            tm.mp = mp
        results = query.fetch(model_proc=mproc)
        self.assertEqual(results[0].mp, "aaaabbbb")
        query.clear()
        query.filter("f_str =", "testmodelproc")
        self.assertEqual(query.get(model_proc=mproc).mp, "aaaabbbb")
        query.delete()
    
    @classmethod
    def tearDownClass(cls):
        cls.TModel.delete_table()

class ModelTest(unittest.TestCase):
    
    class TModel(Model):
        MODULE = "test"
        f_str = properti.StringProperty("fStr")
        f_int = properti.IntegerProperty("fInt")
        f_bool = properti.BooleanProperty("fBool")
        f_float = properti.FloatProperty("fFloat")
        f_date = properti.DateProperty("fDate")
        f_datetime = properti.DateTimeProperty("fDatetime")
        f_blob = properti.BlobProperty("fBlob")
        f_v = properti.StringProperty("fV", length=8)
        f_str1 = properti.StringProperty("fStr1", persistent=False)
        f_str_logged = properti.StringProperty("fStrLogged", logged=True)
        f_float_logged = properti.FloatProperty("fFloatLogged", logged=True)
        
    @classmethod
    def setUpClass(cls):
        cls.TModel().create_table()
        
    def testCreate(self):
        tmodel = self.TModel()
        try:
            tmodel.create()
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)
        tmodel.create(2)
        tmodel2 = self.TModel.get_by_key(tmodel.key())
        self.assertEqual(tmodel2.modifier_id, 2)
        self.assertIsNotNone(tmodel2.modified_time)
        self.assertIsNotNone(tmodel2.created_time)
        
    def testUpdate(self):
        tmodel = self.TModel()
        tmodel.create(2)
        try:
            tmodel.update()
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)
        tmodel2 = self.TModel.get_by_key(tmodel.key())
        time.sleep(1)
        tmodel2.update(2)
        tmodel3 = self.TModel.get_by_key(tmodel.key())
        self.assertGreater(tmodel3.modified_time, tmodel.modified_time)
        
    def testAddMCLog(self):
        tmodel = self.TModel()
        tmodel.f_str = "abcd"
        tmodel.f_int = 100
        tmodel.f_float = 1000.0
        tmodel.f_bool = False
        tmodel.f_float_logged = 1.0
        tmodel.f_str_logged = "1234"
        tmodel.create(2)
        tmodel.f_str = 'abcd1'
        tmodel.f_float = 1001.0
        tmodel.f_float_logged = 2.0
        tmodel.f_str_logged = "123456"
        tmodel.put(2)
        query = MCLog.all()
        self.assertEqual(query.count(), 1)
        query = MCLogDetail.all()
        self.assertEqual(query.count(), 2)
    
    def testPut(self):
        tmodel = self.TModel()
        try:
            tmodel.put()
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)
            
    def testDelete(self):
        tmodel = self.TModel()
        tmodel.create(2)
        try:
            tmodel.delete()
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)
        
        tmodel2 = self.TModel.get_by_key(tmodel.get_keyvalue())
        self.assertIsNotNone(tmodel2)
        tmodel.delete(2)
        
        tmodel2 = self.TModel.get_by_key(tmodel.get_keyvalue())
        self.assertIsNone(tmodel2)
    
class QueryTest(unittest.TestCase):
    class TModelQT(Model):
        MODULE = "test"
        f_str = properti.StringProperty("fStr", logged=True)
        f_str1 = properti.StringProperty("fStr1")
    
    @classmethod
    def setUpClass(cls):
        cls.TModelQT.create_table();
    
    def testUpdate(self):
        
        try:
            query = self.TModelQT.all()
            query.set("f_str", "ccc")
            query.update(2)
            self.assertTrue(False)
        except CoreError:
            self.assertTrue(True)
        
        tm = self.TModelQT().put(3)
        query = self.TModelQT.all() 
        query.set("f_str1", "cccc")
        query.filter("uid =", tm.key())
        query.update(2)         
        query.filter("modifier_id =", 2);
        query.filter("uid =", tm.key())
        self.assertEqual(query.count(), 1)
    
            
    def testDelete(self):
        
        try:
            query = self.TModelQT.all()
            query.delete(None)
            self.assertTrue(False)
        except CoreError:
            self.assertTrue(True)
            
    @classmethod
    def tearDownClass(cls):
        cls.TModelQT.delete_table()       
