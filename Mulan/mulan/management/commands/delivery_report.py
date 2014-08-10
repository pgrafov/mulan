# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from deliver import send_email
from mulan.models import Contact, OrderHistory, Setting
import datetime as dt
import re

import sms24x7

def pp (p):
    if type(p) is tuple:
        return unicode (p[0]) + u" (" +  unicode(p[1]) + u"%)"
    else:
        if p == 0:
            return u"-"
        else:
            return unicode(p)

def generate_delivery_report_plain(orders):
    return u"Ваш почтовый клиент не поддерживает HTML-форматирование! Смените его!"

def generate_delivery_report_html(orders, period):
    orders_menu = [order for order in orders if order.is_menu_order()]
    orders_bl = [order for order in orders if order.is_bl_order()]
    orders_combined = [order for order in orders if order.is_combined_order()]

    orders_count = orders.count()
    orders_menu_count = len(orders_menu)
    orders_bl_count = len(orders_bl)
    orders_combined_count = len(orders_combined)

    orders_regular_guests = 0
    orders_menu_regular_guests = 0
    orders_bl_regular_guests = 0
    orders_combined_regular_guests =0

    orders_occasional_visitors = 0
    orders_menu_occasional_visitors = 0
    orders_bl_occasional_visitors = 0
    orders_combined_occasional_visitors = 0

    orders_map = {}
    for order in orders:
        if order.is_menu_order():
            type_order = 'menu'
        elif order.is_bl_order():
            type_order = 'bl'
        else:
            type_order = 'combined'
        p = re.compile('[^+\d]')
        p2 = re.compile('^\+')
        guest_uid = p2.sub('8', p.sub('', order.original_order.phoneNo))
        if orders_map.has_key(guest_uid):
            val = orders_map[guest_uid]
        else:
            val = {'total':0, 'menu':0, 'bl':0, 'combined':0}
        val['total'] = val['total'] + 1
        val[type_order] = val[type_order] + 1
        orders_map[guest_uid] = val

    for guest_uid in orders_map.keys():
        if orders_map[guest_uid]['total'] > 1:
            orders_regular_guests += orders_map[guest_uid]['total']
        else:
            orders_occasional_visitors += orders_map[guest_uid]['total']

        if orders_map[guest_uid]['total'] > 1:
            orders_menu_regular_guests += orders_map[guest_uid]['menu']
        else:
            orders_menu_occasional_visitors += orders_map[guest_uid]['menu']

        if orders_map[guest_uid]['total'] > 1:
            orders_bl_regular_guests += orders_map[guest_uid]['bl']
        else:
            orders_bl_occasional_visitors += orders_map[guest_uid]['bl']

        if orders_map[guest_uid]['total'] > 1:
            orders_combined_regular_guests += orders_map[guest_uid]['combined']
        else:
            orders_combined_occasional_visitors += orders_map[guest_uid]['combined']

    if orders_regular_guests > 0:
        orders_regular_guests = (orders_regular_guests, int(round(float(orders_regular_guests) / orders_count * 100)))
    if orders_menu_regular_guests > 0:
        orders_menu_regular_guests = (orders_menu_regular_guests, int(round(float(orders_menu_regular_guests) / orders_menu_count * 100)))
    if orders_bl_regular_guests > 0:
        orders_bl_regular_guests = (orders_bl_regular_guests, int(round(float(orders_bl_regular_guests) / orders_bl_count * 100)))
    if orders_combined_regular_guests > 0:
        orders_combined_regular_guests = (orders_combined_regular_guests, int(round(float(orders_combined_regular_guests) / orders_combined_count * 100)))

    if orders_occasional_visitors > 0:
        orders_occasional_visitors = (orders_occasional_visitors, int(round(float(orders_occasional_visitors) / orders_count * 100)))
    if orders_menu_occasional_visitors > 0:
        orders_menu_occasional_visitors = (orders_menu_occasional_visitors, int(round(float(orders_menu_occasional_visitors) / orders_menu_count * 100)))
    if orders_bl_occasional_visitors > 0:
        orders_bl_occasional_visitors = (orders_bl_occasional_visitors, int(round(float(orders_bl_occasional_visitors) / orders_bl_count * 100)))
    if orders_combined_occasional_visitors > 0:
        orders_combined_occasional_visitors = (orders_combined_occasional_visitors, int(round(float(orders_combined_occasional_visitors) / orders_combined_count * 100)))


    orders_money = sum([o.money for o in orders])
    orders_menu_money = sum([o.money for o in orders_menu])
    orders_bl_money = sum([o.money for o in orders_bl])
    orders_combined_money = sum([o.money for o in orders_combined])

    orders_positions = sum([o.calc_positions() for o in orders])
    orders_menu_positions = sum([o.calc_positions() for o in orders_menu])
    orders_bl_positions = sum([o.calc_positions() for o in orders_bl])
    orders_combined_positions = sum([o.calc_positions() for o in orders_combined])


    orders_money_avg = int(round(float(orders_money) / orders_count)) if orders_count > 0 else 0
    orders_menu_money_avg = int(round(float(orders_menu_money) / orders_menu_count)) if orders_menu_count > 0 else 0
    orders_bl_money_avg = int(round(float(orders_bl_money) / orders_bl_count)) if orders_bl_count > 0 else 0
    orders_combined_money_avg = int(round(float(orders_combined_money) / orders_combined_count)) if orders_combined_count > 0 else 0

    orders_positions_avg = round(float(orders_positions) / orders_count, 2) if orders_count > 0 else 0
    orders_menu_positions_avg = round(float(orders_menu_positions) / orders_menu_count, 2) if orders_menu_count > 0 else 0
    orders_bl_positions_avg = round(float(orders_bl_positions) / orders_bl_count, 2) if orders_bl_count > 0 else 0
    orders_combined_positions_avg = round(float(orders_combined_positions) / orders_combined_count, 2) if orders_combined_count > 0 else 0

    period_start = period[0]
    period_end = period[1]
    days = (period_end - period_start).days + 1



    orders_avg_per_day = round(float(orders_count) / days, 2)
    orders_menu_avg_per_day = round(float(orders_menu_count) / days, 2)
    orders_bl_avg_per_day = round(float(orders_bl_count) / days, 2)
    orders_combined_avg_per_day = round(float(orders_combined_count) / days, 2)


    orders_max_per_day = 0
    orders_menu_max_per_day = 0
    orders_bl_max_per_day = 0
    orders_combined_max_per_day = 0

    orders_map = {}
    for order in orders:
        if order.is_menu_order():
            type_order = 'menu'
        elif order.is_bl_order():
            type_order = 'bl'
        else:
            type_order = 'combined'

        uid = order.created.date()
        if orders_map.has_key(uid):
            val = orders_map[uid]
        else:
            val = {'total':0, 'menu':0, 'bl':0, 'combined':0}
        val['total'] = val['total'] + 1
        val[type_order] = val[type_order] + 1
        orders_map[uid] = val
    for uid in orders_map.keys():
        if orders_map[uid]['total'] > orders_max_per_day:
            orders_max_per_day = orders_map[uid]['total']
        if orders_map[uid]['menu'] > orders_menu_max_per_day:
            orders_menu_max_per_day = orders_map[uid]['menu']
        if orders_map[uid]['bl'] > orders_bl_max_per_day:
            orders_bl_max_per_day = orders_map[uid]['bl']
        if orders_map[uid]['combined'] > orders_combined_max_per_day:
            orders_combined_max_per_day = orders_map[uid]['combined']

    days_correct_ending = u"дней"
    if (days % 10) == 1 and not days == 11:
        days_correct_ending = u"день"
    if (days % 10) in [2, 3, 4] and not days in [12, 13, 14]:
        days_correct_ending = u"дня"
    preface = (u"<h3> Уважаемый господин/уважаемая госпожа, </h3>" +
               u"<p>вот отчёт о работе доставки с сайта за период с <b>" +
               unicode (period_start) + u'</b> по <b>' + unicode (period_end) + u'</b> ('+ unicode(days) + u' ' + days_correct_ending + u'):</p>')


    table_style =  u'style="border: 1px solid;padding: 5px;"'
    balance = None
    try:
        smsapi = sms24x7.smsapi(Setting.objects.get (key = 'email_address').value.encode('utf-8'),
                                Setting.objects.get (key = 'sms24x7_password').value.encode('utf-8'))
        smsapi.login()
        balance = smsapi.balance()
    except Exception as e:
        pass
    return preface + (u"<table %table_style%>" +
            u'<thead>' +
            u'<tr>' +
            u'<th %table_style%></th>' +
            u'<th %table_style%>Все заказы</th>' +
            u'<th %table_style%>Заказы по меню</th>' +
            u'<th %table_style%>Заказы <nobr>бизнес-ланчей</nobr></th>' +
            u'<th %table_style%>Заказы комбинированные</th>' +
            u'</tr>'+
            u'</thead>' +
            u'<tbody>' +

            u'<tr>' +
            u'<td %table_style%><b>Количество заказов:</b></td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_count) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_menu_count) + '</td>'
            u'<td %table_style%'+ u' align="center">' + pp(orders_bl_count) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_combined_count) + '</td>' +
            u'</tr>'+

            u'<tr>' +
            u'<td %table_style%><b>Количество заказов от постоянных гостей (% от всех заказов):</b></td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_regular_guests) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp( orders_menu_regular_guests) + '</td>'
            u'<td %table_style%'+ u' align="center">' + pp(orders_bl_regular_guests) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_combined_regular_guests) + '</td>' +
            u'</tr>'+



            u'<tr>' +
            u'<td %table_style%><b>Количество заказов от случайных посетителей (% от всех заказов:</b></td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_occasional_visitors) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_menu_occasional_visitors) + '</td>'
            u'<td %table_style%'+ u' align="center">' + pp(orders_bl_occasional_visitors) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_combined_occasional_visitors) + '</td>' +
            u'</tr>'+


            u'<tr>' +
            u'<td %table_style%><b>Получено денег от клиентов:</b></td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_money ) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_menu_money) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_bl_money) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_combined_money) + '</td>' +
            u'</tr>'+


            u'<tr>' +
            u'<td %table_style%><b>Средняя стоимость заказа:</b></td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_money_avg) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_menu_money_avg) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_bl_money_avg) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_combined_money_avg) + '</td>' +
            u'</tr>'+



            u'<tr>' +
            u'<td %table_style%><b>Среднее количество позиций в заказе:</b></td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_positions_avg) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_menu_positions_avg) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_bl_positions_avg) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_combined_positions_avg) + '</td>' +
            u'</tr>'+

            u'<tr>' +
            u'<td %table_style%><b>Среднее число заказов в день:</b></td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_avg_per_day) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_menu_avg_per_day) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_bl_avg_per_day) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_combined_avg_per_day) + '</td>' +
            u'</tr>'+

            u'<tr>' +
            u'<td %table_style%><b>Максимальное число заказов в день:</b></td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_max_per_day) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_menu_max_per_day) + '</td>' +
            u'<td %table_style%'+ u' align="center">' +  pp(orders_bl_max_per_day) + '</td>' +
            u'<td %table_style%'+ u' align="center">' + pp(orders_combined_max_per_day) + '</td>' +
            u'</tr>'+


            u'<tbody>' +
            u"</table>" +
            (u"<p>Также сообщаем,что в настоящее время ваш баланс на сайте sms24x7.ru составляет <b>" + balance + u'</b></p>' if balance else '')
            ).replace (u'%table_style%', table_style)

def get_prev_month_end (date):
    this_month = date.month
    while this_month == date.month:
        date = date - dt.timedelta (days = 1)
    return date

def get_this_month_start(date):
    return date.replace (day = 1 )

def get_this_year_start(date):
    return date.replace (month = 1, day = 1 )

class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args)!= 1 or args[0].upper() not in ['Y', 'M']:
            raise CommandError ("You must specify type of report: Y or M")
        period_end =  get_prev_month_end (dt.date.today())
        if args[0].upper() == 'Y':
            period_start = get_this_year_start (period_end)
        else:
            period_start = get_this_month_start (period_end)
        #print period_start, period_end
        orders = OrderHistory.objects.filter (created__gte = period_start).filter(created__lte = period_end).order_by ('created')
        if orders.count() > 0 and orders[0].created.date() > period_start and args[0].upper() == 'Y':
            period_start = orders[0].created.date()
        for contact in Contact.objects.all():
                if '@' in contact.contact_detail:
                    report_plain = generate_delivery_report_plain(orders)
                    report_html = generate_delivery_report_html(orders, [period_start, period_end])
                    send_email(u'Отчёт о работе доставки с сайта за период с ' + unicode (period_start) + u' по ' + unicode (period_end) + u'.',
                               report_plain,
                               report_html,
                               contact.contact_detail)
