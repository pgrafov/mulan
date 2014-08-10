# coding=utf-8
import math
from django.core.management.base import BaseCommand, CommandError
from mulan.models import  MenuCat, MenuEntry
class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args)!= 1:
            raise CommandError ("You must specify price delta (%), e.g. new_price 10")
        price_delta = int(args[0])
        for menucat in MenuCat.objects.all().order_by('order'):
            if MenuEntry.objects.filter (menucat = menucat).count():
                print "=== " + menucat.name.encode('utf-8') + " ===" 
            menuentries = MenuEntry.objects.filter (menucat = menucat).order_by('order')
            for menuentry in menuentries:
                old_price = menuentry.price
                new_price = int(round(old_price * (100.0 + price_delta) / 100.0))
                menuentry.price = new_price
                menuentry.save()
                print menuentry.code.encode('utf-8') + ". " + menuentry.name.encode('utf-8') + " - " + str(new_price) + " (" + str(old_price) +  ")"
                
            
        