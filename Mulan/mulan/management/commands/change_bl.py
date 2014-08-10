# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from mulan.models import Setting
import datetime as dt

from mulan.management.commands.deliver import send_email

def generate_success_message (s1, s2, old_cur_bl_variant, old_next_bl_variant_change):
    return  (u"Смена варианта меню бизнес-ланча прошла успешно.\n" + 
            s1.description + u": было " + unicode (old_cur_bl_variant) + u', стало ' + unicode (s1.value) + u"\n" + 
            s2.description + u": было " + unicode (old_next_bl_variant_change.strftime ("%d.%m.%Y")) + 
                             u', стало ' + unicode (s2.value) + u"\n") 


def generate_failure_message (s1, s2, s3):
    return u"Произошла какая-то ошибка! Проверьте внимательно настройки!"

class Command(BaseCommand):
    def handle(self, *args, **options):
        msg_to_send = None
        failure = False
        try:
            
            s1 = Setting.objects.get (key = 'cur_bl_variant')
            s2 = Setting.objects.get (key = 'next_bl_variant_change')
            s3 = Setting.objects.get (key = 'bl_variant_change_period')
            old_cur_bl_variant = int(s1.value)
            old_next_bl_variant_change = dt.datetime.strptime (s2.value, "%d.%m.%Y").date()
            bl_variant_change_period = int(s3.value)
            
            if dt.date.today() >= old_next_bl_variant_change:
                new_cur_bl_variant = (old_cur_bl_variant + 1) % 2
                new_next_bl_variant_change = old_next_bl_variant_change + dt.timedelta (days = bl_variant_change_period)
                s1.value = str (new_cur_bl_variant)
                s2.value =  new_next_bl_variant_change.strftime ("%d.%m.%Y")
                s1.save()
                s2.save()
                msg_to_send = generate_success_message (s1, s2, old_cur_bl_variant, old_next_bl_variant_change)
        except ValueError:
            msg_to_send = generate_failure_message (s1, s2, s3)
            failure = True
        if msg_to_send:
            subj = u"Смена варианта меню бизнес-ланча: " + (u"ошибка!" if failure else u"успешно")
            send_email (subj, msg_to_send, msg_to_send, Setting.objects.get (key = 'admin_email').value)   
