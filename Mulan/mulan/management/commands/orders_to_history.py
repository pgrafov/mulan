# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from mulan.models import Order, OrderHistory

class Command(BaseCommand):
    def handle(self, *args, **options):
        if OrderHistory.objects.count() == 0:
            for order in Order.objects.all():
                order_history = OrderHistory(   original_order = order,
                                                created = order.created,
                                                money = order.calc_order_total()) 
                order_history.save()