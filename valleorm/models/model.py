# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <vallemrv>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 23-Dec-2017
# @License: Apache license vesion 2.0

from datetime import date, datetime
import sqlite3
import json
import base64

from constant import constant
from fields import *
from relatedfields import *



class Model(object):
    def __init__(self, dbName="db.sqlite3", **options):
        self.lstCampos = []
        self.foreingKeys = []
        self.id = -1
        self.table_name = self.__class__.__name__.lower()
        self.dbName = dbName
        if self.table_name != "model":
            self.__init_campos__()

        for k, v in options.items():
            if k not in self.lstCampos + ['id']:
                raise AttributeError("Este modelo no contine %s" % k)
            if k == 'id':
                self.load_by_pk(v)
            setattr(self, k, v)

    def __setattr__(self, attr, value):
        es_dato_simple = type(value) in (str, int, bool, float, unicode, date, datetime)
        es_dato_simple = es_dato_simple and hasattr(self, 'lstCampos') and attr in self.lstCampos
        if es_dato_simple or value == None:
            field = super(Model, self).__getattribute__(attr)
            field.set_dato(value)
        else:
            super(Model, self).__setattr__(attr, value)


    def __getattribute__(self, attr):
        value = super(Model, self).__getattribute__(attr)
        if hasattr(value, 'tipo_class') and value.tipo_class == constant.TIPO_CAMPO:
            return value.get_dato()

        return value


    #Introspection of the inherited class
    def __init_campos__(self):
        for key in dir(self):
            field =  super(Model, self).__getattribute__(key)
            tipo_class = ""
            if hasattr(field, 'tipo_class'):
                tipo_class = field.tipo_class
            if tipo_class == constant.TIPO_CAMPO:
                setattr(self, key, field.__class__(**field.get_serialize_data(key)))
                self.lstCampos.append(key)
            elif tipo_class == constant.TIPO_RELATION:
                setattr(self, key, field.__class__(othermodel=field.related_name,
                                                   on_delete=field.on_delete,
                                                   main_class=self,
                                                   field_related_name=field.field_related_name,
                                                   field_related_id=field.field_related_id))

                if field.class_name in "ForeignKey":
                    setattr(self, field.field_name_id, IntegerField())
                    self.lstCampos.append(field.field_name_id)
                    self.foreingKeys.append(field.get_sql_pk())

                if field.class_name == "ManyToManyField":
                    rel = getattr(self, key)
                    table_nexo = self.__find_db_nexo__(rel.tb_name_main, rel.tb_name_related)
                    if table_nexo == None:
                        self.__crear_tb_nexo__(rel)
                    else:
                        rel.tb_nexo_name = table_nexo

        self.__create_if_not_exists__()



    def __find_db_nexo__(self, tb1, tb2):
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        condition = u" AND (name='{0}' OR name='{1}')".format(tb1+"_"+tb2, tb2+"_"+tb1)
        sql = u"SELECT name FROM sqlite_master WHERE type='table' %s;" % condition
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        if reg:
            find = True
            return reg[0]
        return None


    def __create_if_not_exists__(self):
        fields = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for key in self.lstCampos:
            field  = super(Model, self).__getattribute__(key)
            fields.append(u"'{0}' {1}".format(key, field.toQuery()))

        frgKey = "" if len(self.foreingKeys)==0 else u", {0}".format(", ".join(self.foreingKeys))

        values = ", ".join(fields)
        sql = u"CREATE TABLE IF NOT EXISTS {1} ({0}{2});".format(values,
                                                            self.table_name,
                                                            frgKey)
        self.execute(sql)

    def __crear_tb_nexo__(self, relation):
        sql = relation.get_sql_tb_nexo()
        self.execute(sql)


    def __cargar_datos__(self, **datos):
        for k, v in datos.items():
            if k not in self.lstCampos + ['id']:
                raise AttributeError("El atributo %s no esta en el modelo"% k)
            elif k=="id":
                self.id = v
            else:
                setattr(self, k, v)


    def save(self, **kargs):
        self.__cargar_datos__(**kargs)
        self.id = -1 if self.id == None else self.id

        keys =[]
        vals = []
        for key in self.lstCampos:
            val = super(Model, self).__getattribute__(key)
            keys.append(key)
            vals.append(str(val.get_pack_dato(val)))

        if self.id > 0:
            keys.append("id")
            vals.append(str(self.id))
        cols = ", ".join(keys)
        values = ", ".join(vals)
        sql = u"INSERT OR REPLACE INTO {0} ({1}) VALUES ({2});".format(self.table_name,
                                                           cols, values);
        print sql
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        if self.id == -1:
            self.id = cursor.lastrowid
        db.commit()
        db.close()

    def delete(self):
        self.id = -1 if self.id == None else self.id
        sql = u"DELETE FROM {0} WHERE id={1};".format(self.table_name, self.id)
        self.execute(sql)
        self.id = -1


    def empty(self):
        self.id = -1;
        self.execute("DELETE FROM %s;" % self.table_name)


    def execute(self, query):
        if sqlite3.complete_statement(query):
            db = sqlite3.connect(self.dbName)
            cursor= db.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(query)
            db.commit()
            db.close()


    def load_by_pk(self, pk):
        sql = u"SELECT * FROM {0} WHERE id={1};".format(self.table_name, pk)
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        d = cursor.description
        db.commit()
        db.close()
        if reg:
            res = dict({k[0]: v for k, v in list(zip(d, reg))})
            self.__cargar_datos__(**res)

    def toJSON(self):
        js = self.toDICT()
        return json.dumps(js, ensure_ascii=False)

    def toDICT(self):
        if self.id > 0:
            js = {"id": self.id}
        else:
            js = {}
        for key in self.lstCampos:
            v =  getattr(self, key)
            if not (v == "None" or v is None):
                js[key] = v

        return js

    @classmethod
    def empty(cls, dbName="db.sqlite3"):
        sql = "DELETE FROM %s;" % cls.__name__.lower()
        db = sqlite3.connect(self.dbName)
        cursor= db.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(sql)
        db.commit()
        db.close()

    @classmethod
    def select(cls, sql, dbName="db.sqlite3"):
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        print sql
        cursor.execute(sql)
        reg = cursor.fetchall()
        d = cursor.description
        db.commit()
        db.close()
        registros = []

        for r in reg:
            res = dict({k[0]: v for k, v in list(zip(d, r))})
            obj = cls(dbName=dbName, **res)
            registros.append(obj)

        return registros

    @classmethod
    def filter(cls, dbName="db.sqlite3", **condition):
        table_name = cls.__name__.lower()
        columns = "*"
        order, query, limit,  offset, joins, group = ("", )*6
        for k, v in condition.items():
            if k == 'columns':
                columns = ", ".join(v)
            elif k == 'order':
                order = "ORDER BY %s" % unicode(v)
            elif k =='query':
                query =  "WHERE %s" % unicode(v)
            elif k == 'limit':
                limit = "LIMIT %s" % v
            elif k == 'offset':
                offset = "OFFSET %s" % v
            elif k == 'joins':
                joins = cls.getenerate_joins(v)
            elif k == 'group':
                group = "GROUP BY %s" % v


        sql = u"SELECT {0} FROM {1} {2} {3} {4} {5} {6} {7};".format(columns, table_name,
                                                         joins, query, order, group, limit, offset)
        print (sql)
        return cls.select(sql, dbName)


    @staticmethod
    def getenerate_joins(joins):
        strJoins = []
        for j in joins:
            sql = j if j.startswith("INNER") else "INNER JOIN "+j
            strJoins.append(sql)

        return "" if len(strJoins) <=0 else ", ".join(strJoins)

    @staticmethod
    def to_array_dict(registros):
        lista = []
        for r in registros:
            reg = r.toDICT()
            lista.append(reg)

        return lista

    @staticmethod
    def remove_rows(registros):
        lista = []
        for r in registros:
            lista.append({'id': r.id, 'success': True})
            r.remove()
        return lista

    @staticmethod
    def serialize(registros):
        lista = []
        for r in registros:
            reg = {}
            reg["table_name"] = r.table_name
            reg["dbName"] = r.dbName
            reg["datos"] = r.toDICT()
            lista.append(reg)

        return json.dumps(lista)

    @staticmethod
    def deserialize(dbJSON):
        lista = json.loads(dbJSON)
        registros = []
        for l in lista:
            obj = Model(table_name=l["table_name"], dbName=l["dbName"])
            obj.__cargar_datos__(**l["datos"])
            registros.append(obj)

        return registros

    @staticmethod
    def drop_db(dbName):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%sqlite%';"
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchall()
        for r in reg:
            cursor.execute("DROP TABLE %s" % r)
        db.commit()
        db.close()

    @staticmethod
    def exits_table(table_name, dbName='db.sqlite3'):
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
        sql = sql % table_name
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        reg = cursor.fetchone()
        db.commit()
        db.close()
        return reg != None


    @staticmethod
    def alter_constraint(table_name, colum_name, parent, dbName='db.sqlite3', delete=constant.CASCADE):
        sql = u"ALTER TABLE {0} ADD COLUMN {1} INTEGER REFERENCES {2}(id) {3};"
        sql = sql.format(table_name, colum_name, parent, delete)
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()

    @staticmethod
    def alter(field, dbName='db.sqlite3'):
        sql = u"ALTER TABLE {0} ADD COLUMN {1} {2};"
        sql = sql.format(field.table_name, field.field_name, field.toQuery())
        db = sqlite3.connect(dbName)
        cursor= db.cursor()
        cursor.execute(sql)
        db.commit()
        db.close()
