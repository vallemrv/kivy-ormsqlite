# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Dec-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 01-Jan-2018
# @License: Apache license vesion 2.0



import os
import sys
import names
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm import models, QSonSender, QSonHelper

# Create your models here.
class Users(models.Model):
   nombre = models.CharField(max_length=120)
   puesto = models.ManyToManyField("Puestos")

   class Meta:
       db_table = "usuarios"
       ordering = ["id DESC"]


class Salario(models.Model):
   mes = models.DateTimeField(auto_now_add=True)
   importe = models.DecimalField(max_digits=7, decimal_places=2)
   user = models.ForeignKey("Users", on_delete=models.CASCADE)


class Puestos(models.Model):
    nombre = models.CharField(max_length=200)
    des = models.CharField(max_length=200)
    user = models.ManyToManyField(Users)



class ClasesQson(QSonSender):
    url = "http://localhost:8000/qson_django/"
    token = "holamanoloooolkdkdoos"
    db_name = "clases"


salir = False
def on_success(req, result):
    print result

qson = ClasesQson()
qson.send_get(on_success, wait=True, qsonhelper=(wrap,))
