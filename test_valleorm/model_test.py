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
   puesto = models.ManyToManyField("Puesto")
   salario = models.OneToManyField("Salario")


class Salario(models.Model):
   mes = models.DateTimeField(auto_now_add=True)
   importe = models.DecimalField(max_digits=7, decimal_places=2)
   user = models.ForeignKey("User", delete=models.CASCADE)


class Puesto(models.Model):
    nombre = models.CharField(max_length=200)
    des = models.CharField(max_length=200)
    user = models.ManyToManyField(User)
