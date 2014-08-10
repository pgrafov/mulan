# coding=utf-8
from django.forms import ModelForm, CharField, HiddenInput, ModelChoiceField
from models import Order, Street
def qqq ( **x):
    return Street.objects.get (pk = x['pk']) 

def my_special_sql_for_vasilyevsky_island_streets ():
    return u"""
    (SELECT * FROM mulan_street WHERE (name<'линия' AND (type!='линия' OR (type='линия' AND (LENGTH(name)>4))))  ORDER BY name)
    UNION ALL
    (SELECT * FROM mulan_street WHERE type='линия' AND LENGTH(name)=3 ORDER BY name)
    UNION ALL
    (SELECT * FROM mulan_street WHERE type='линия' AND LENGTH(name)=4 ORDER BY name)
    UNION ALL
    (SELECT * FROM mulan_street WHERE (name>'линия' AND (type!='линия' OR (type='линия' AND  (LENGTH(name)>4))))  ORDER BY name)
    """


class OrderForm(ModelForm):
    order_contents = CharField(label="", widget=HiddenInput(), required=False)
    q0 = (Street.objects.raw(my_special_sql_for_vasilyevsky_island_streets()))
    q0.all = q0.__iter__
    q0.get = lambda **x: qqq( **x)
    street = ModelChoiceField (queryset = q0, label="Улица")
   
    
    class Meta:
        model = Order
        exclude = ('processed',)