# -*- coding: utf-8 -*-
#
# @Author: Manuel Rodriguez <valle>
# @Date:   29-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: field.py
# @Last modified by:   valle
# @Last modified time: 22-Dec-2017
# @License: Apache license vesion 2.0

import importlib
import uuid
from exceptions import ValueError
from constant import constant
from decimal import *
from datetime import date, datetime


class Field(object):
    def __init__(self, null=False, default=None, unique=False, **options):
        self.tipo_class = constant.TIPO_CAMPO
        self.field_name = None
        self.default = default
        self.null = null
        self.tipo = 'TEXT'
        self.dato = self.default
        self.unique = unique
        for k, v in options.items():
            setattr(self, k, v)


    def get_pack_dato(self, key):
        dato = self.get_dato()
        if self.null == True and dato == None:
            return 'NULL'
        elif self.tipo in  ["TEXT", "VARCHAR"]:
            return u'"{0}"'.format(unicode(dato))
        elif self.tipo is "DATETIME":
            return   u'"{0}"'.format(unicode(dato.strftime("%Y/%m/%d-%H:%M:%S.%f")))
        elif self.tipo == "DATE":
            return   u'"{0}"'.format(unicode(dato.strftime("%Y/%m/%d")))
        elif self.tipo == "BOOL":
            return 1 if self.dato == 1 or self.dato == True else 0
        else:
            return dato

    def get_pack_default(self):
        if self.tipo in  ["TEXT", "VARCHAR"]:
            return u'"{0}"'.format(unicode(self.default))
        else:
            return self.default


    def get_dato(self):
        if self.dato == None and self.null == False:
            raise ValueError("%s no puede conterner valor null" % self.field_name)
        elif self.dato == 'NULL':
            self.dato = None
        return self.dato

    def set_dato(self, value):
        self.dato = value


    def get_serialize_data(self, key):
        obj_return = self.__dict__
        obj_return['field_name'] = key
        self.field_name = key
        return  obj_return

    def getStrTipo(self):
        return self.tipo

    def toQuery(self):
        strnull = "" if self.null == True else ' NOT NULL '
        strdefault = "" if self.default == None else " DEFAULT %s" % self.get_pack_default()
        strunique = "" if self.unique == False else " UNIQUE "
        return u"{0} {1} {2} {3}".format(self.getStrTipo(), strnull, strdefault, strunique)

class CharField(Field):
    def __init__(self, max_length, null=False, default=None, unique=False, **options):
        super(CharField, self).__init__(null=null, default=default, unique=unique, **options)
        self.tipo="VARCHAR"
        self.class_name = "CharField"
        self.max_length=max_length

    def set_dato(self, value):
        if value != None:
            how_long = len(value)
            if how_long > self.max_length:
                self.dato = value[:self.max_length-how_long]
            else:
                self.dato = value


    def getStrTipo(self):
        return "VARCHAR(%s)" % self.max_length

class EmailField(CharField):
    def __init__(self, max_length=254, null=False, default=None, unique=False, **options):
        super(EmailField, self).__init__(max_length, null=null, default=default, unique=unique, **options)
        self.class_name = 'EmailField'

    def set_dato(self, value):
        if value != None and not  ("@" in value and "." in value):
            raise ValueError('Formato email no valido')
        self.dato = value


class DecimalField(Field):
    def __init__(self, max_digits, decimal_places, null=False, default=None, unique=False, **options):
        super(DecimalField, self).__init__(null=null, default=default, unique=unique, **options)
        self.max_digits=max_digits
        self.decimal_places=decimal_places
        self.class_name = "DecimalField"

    def set_dato(self, value):
        super(DecimalField, self).set_dato(value)
        if type(value) in (unicode, str):
            self.dato = float(value.replace(",", "."))
        else:
            self.dato = value

    def get_dato(self):
        self.dato = super(DecimalField, self).get_dato()
        if type(self.dato) in [float, int]:
            dato = "%."+str(self.decimal_places)+"f"
            dato = dato % self.dato
            return str(dato)

    def getStrTipo(self):
        return u"DECIMAL({0},{1})".format(self.max_digits, self.decimal_places)


class DateField(Field):
    def __init__(self, auto_now=False, auto_now_add=True, null=False, default=None, unique=False, **options):
        super(DateField, self).__init__(null=null, default=default, unique=unique, **options)
        self.tipo="DATE"
        self.class_name = "DateField"
        self.auto_now=auto_now
        self.auto_now_add=auto_now_add


    def get_dato(self):
        if self.auto_now:
            self.dato = date.today()
        elif self.auto_now_add and self.dato == None:
            self.dato = date.today()
        return super(DateField, self).get_dato()

    def set_dato(self, value):
        if type(value) == date:
            self.dato = date
        else:
            self.dato = date(*value.split("/"))



class DateTimeField(Field):
    def __init__(self, auto_now=False, auto_now_add=False, null=False, default=None, unique=False, **options):
        super(DateTimeField, self).__init__(null=null, default=default, unique=unique, **options)
        self.tipo="DATETIME"
        self.class_name = "DateTimeField"
        self.auto_now=auto_now
        self.auto_now_add=auto_now_add

    def get_dato(self):
        if self.auto_now:
            self.dato = datetime.now()
        elif self.auto_now_add and self.dato == None:
            self.dato = datetime.now()
        return super(DateTimeField, self).get_dato()

    def set_dato(self, value):
        if type(value) == datetime:
            self.dato = value
        else:
            self.dato = datetime.strptime(value,"%Y/%m/%d-%H:%M:%S.%f")



class BooleanField(Field):
    def __init__(self, **options):
        super(BooleanField, self).__init__(**options)
        self.tipo="BOOL"
        self.class_name = "BooleanField"

    def get_dato(self):
        return True if self.dato == 1 or self.dato == True else False

    def set_dato(self, value):
        self.dato = True if value == True or value == 1 else False



class IntegerField(Field):
    def __init__(self, null=False, default=None, unique=False, **options):
        super(IntegerField, self).__init__(null=null, default=default, unique=unique, **options)
        self.tipo="INTEGER"
        self.class_name = "IntegerField"


class FloatField(Field):
    def __init__(self, **options):
        super(FloatField, self).__init__(null=null, default=default, unique=unique, **options)
        self.tipo="REAL"
        self.class_name = "FloatField"


class TextField(Field):
    def __init__(self, **options):
        super(TextField, self).__init__(null=null, default=default, unique=unique, **options)
        self.tipo="TEXT"
        self.class_name = "TextField"


class UUIDField(Field):
    def __init__(self, **options):
        super(UUIDField, self).__init__(null=null, default=default, unique=unique, **options)
        self.class_name = "UUIDField"
        self.tipo="TEXT"
        self.unique = True

    def get_dato(self):
        return str(uuid.uuid4())
