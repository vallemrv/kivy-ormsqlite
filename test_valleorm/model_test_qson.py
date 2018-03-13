# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Dec-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Feb-2018
# @License: Apache license vesion 2.0



import os
import sys
import names
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from valleorm import models, QSonSender, QSonHelper, QSonQH
# Create your models here.
class Users(models.Model):
   nombre = models.CharField(max_length=120)

   class Meta:
       db_table = "usuarios"
       ordering = ["-id", "nombre"]


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

#qson.all(on_success=on_success, models=(Puestos,), wait=True)

qsonqh = QSonQH(Users, )
qsonqh.append_child(QSonQH(Puestos,))
qson.filter(on_success=on_success, qsonqh=(qsonqh,), wait=True)


'''
puesto = Puestos(id=1,)

qhelper = QSonHelper(Puestos(id=1,))
qhelper.append_child(Users(id=17), 'user' )
qson.save(on_success=on_success, qsonhelper=(qhelper,), wait=True)
'''
