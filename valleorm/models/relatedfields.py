# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <vallemrv>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 23-Dec-2017
# @License: Apache license vesion 2.0

import sys
import inspect
import importlib
from constant import constant

class RelationShip(object):

    def __init__(self, othermodel, **options):
        self.tipo_class = constant.TIPO_RELATION
        self.class_name = "ForeignKey"
        self.related_class = None
        self.main_class = None
        self.field_related_name = None
        self.field_related_id = None
        self.on_delete = constant.CASCADE
        if type(othermodel) in (str, unicode):
            self.related_name = othermodel
        else:
            self.related_name = othermodel.__name__
            self.related_class = othermodel

        for k, v in options.items():
            setattr(self, k, v)


    def get_id_field_name(self):
        if self.field_related_name == None:
            return self.related_name.lower() + "_id"
        return self.field_related_name

    def set_id_field_name(self, value):
        self.field_related_name = value

    def get(self, **condition):
        pass

    field_name_id = property(get_id_field_name, set_id_field_name)

class OneToManyField(RelationShip):
    def __init__(self, othermodel, **kargs):
        super(OneToManyField, self).__init__(othermodel, **kargs)
        self.class_name = "OneToManyField"
        if self.field_related_name == None and self.main_class != None:
            self.field_related_name = self.main_class.table_name+"_id"

    def get(self, **condition):
        if self.related_class == None:
            self.related_class = create_class_related(self.main_class.__module__, self.related_name)
        query = u"{0}={1}".format(self.field_name_id, self.main_class.id)

        if 'query' in condition:
            condition['query'] += " AND " + query
        else:
            condition['query'] = query
        return self.related_class.filter(**condition)


    def add(self, child):
        if self.main_class.id == -1:
            self.main_class.save()
        setattr(child, self.field_name_id, self.main_class.id)
        child.save()

class ForeignKey(RelationShip):
    def __init__(self, othermodel, delete=constant.CASCADE, **kargs):
        super(ForeignKey, self).__init__(othermodel, **kargs)
        self.class_name = "ForeignKey"
        self.on_delete = delete

    def get_choices(self, **condition):
        return self.related_class.getAll(**condition)

    def get_sql_pk(self):
        sql = u"FOREIGN KEY({0}) REFERENCES {1}(id) %s" % self.on_delete
        sql = sql.format(self.field_name_id, self.related_name)
        return sql

    def get(self):
        if self.related_class == None:
            self.related_class = create_class_related(self.main_class.__module__, self.related_name)
        reg = self.related_class(dbName=self.main_class.dbName)
        reg.load_by_pk(getattr(self.main_class, self.field_name_id))
        return reg

class ManyToManyField(RelationShip):

    def __init__(self, othermodel, delete=constant.CASCADE, **kargs):
        super(ManyToManyField, self).__init__(othermodel, **kargs)
        self.class_name = "ManyToManyField"

        if self.main_class != None:
            self.tb_name_main = self.main_class.__class__.__name__.lower()
            self.tb_name_related = self.related_name.lower()
            self.tb_nexo_name = self.tb_name_main+"_"+self.tb_name_related
            if self.field_related_id == None:
                self.field_name_id = self.tb_name_main + "_id"
                self.field_related_id = self.tb_name_related + "_id"


    def get_sql_tb_nexo(self):
        key = "PRIMARY KEY ({0}, {1})".format(self.field_name_id, self.field_related_id)
        frgKey = u"FOREIGN KEY({0}) REFERENCES {1}(id) ON DELETE CASCADE, "
        frgKey = frgKey.format(self.field_name_id, self.tb_name_main)
        frgKey += u"FOREIGN KEY({0}) REFERENCES {1}(id) ON DELETE CASCADE"
        frgKey = frgKey.format(self.field_related_id, self.tb_name_related)
        sql = u"CREATE TABLE IF NOT EXISTS {0} ({1}, {2} ,{3}, {4});"
        sql = sql.format(self.tb_nexo_name, self.field_name_id+" INTEGER NOT NULL",
                         self.field_related_id+" INTEGER NOT NULL ",key, frgKey)


        return sql


    def get(self, **condition):
        condition["columns"] = [self.tb_name_related+".*"]

        condition["joins"] = [(self.tb_nexo_name + " ON "+ \
                             self.tb_nexo_name+"."+self.field_related_id+\
                             "="+self.tb_name_related+".id")]
        query = self.field_name_id+"="+str(self.main_class.id)
        if 'query' in condition:
            condition["query"] += " AND " + query
        else:
            condition["query"] = query

        if self.related_class == None:
            self.related_class = create_class_related(self.main_class.__module__, self.related_name)

        return self.related_class.filter(**condition)


    def add(self, *childs):
        for child in childs:
            child.save()
            cols = [self.field_name_id, self.field_related_id]
            values = [str(self.main_class.id), str(child.id)]
            sql = u"INSERT OR REPLACE INTO {0} ({1}) VALUES ({2});".format(self.tb_nexo_name,
                                                               ", ".join(cols), ", ".join(values));
            print sql
            self.main_class.execute(sql)

    def delete(self, child):
        sql = u"DELETE FROM {0} WHERE {1}={2}  AND {3}={4};".format(self.tb_nexo_name,
                                                                    self.field_name_id,
                                                                    child.id,
                                                                    self.field_related_id,
                                                                    self.main_class.id)
        print sql
        self.main_class.execute(sql)



def create_class_related(module, class_name):
    modulo = importlib.import_module(module)
    nclass = getattr(modulo,  class_name)
    return nclass
