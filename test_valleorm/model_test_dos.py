# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Dec-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 23-Dec-2017
# @License: Apache license vesion 2.0



import os
import sys
import names
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm import models

class User(models.Model):
   nombre = models.CharField(max_length=120)
   apellidos = models.CharField(max_length=120)
   direcciones = models.OneToManyField("Direcciones", field_related_name="usuarios")


class Direcciones(models.Model):
    direccion = models.CharField(max_length=120)
    codigo_postal = models.IntegerField()
    user = models.ForeignKey(User, field_related_name="usuarios")



d = Direcciones()
