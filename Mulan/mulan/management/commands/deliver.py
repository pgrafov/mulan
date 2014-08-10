# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from mulan.models import Contact, Order, OrderSentToContactResult, Setting

import smtplib, re
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import sms24x7

def send_email(subject, text, html,  email_address): 
    try:
        gmailUser = Setting.objects.get (key = 'email_address').value
        gmailPassword = Setting.objects.get (key = 'email_password').value
        recipient = email_address
        msg = MIMEMultipart('alternative')
        msg['From'] = gmailUser
        msg['To'] = recipient
        msg['Subject'] = subject   

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text.encode('utf-8'), 'plain', _charset = 'utf-8')
        part2 = MIMEText(html.encode('utf-8'), 'html', _charset = 'utf-8')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
    
        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, recipient, msg.as_string())
        mailServer.close()
        return True
    except Exception, e:
        #raise e
        return False
    
    
def send_sms (order, phoneNo):
    print 'entering send_sms'
    try:
        smsapi = sms24x7.smsapi(Setting.objects.get (key = 'email_address').value.encode('utf-8'), 
                                Setting.objects.get (key = 'sms24x7_password').value.encode('utf-8'))
        smsapi.push_msg(order.to_sms(), phoneNo, nologin = True)
        return True
    except Exception, e:
        """
        print  e
        print  Setting.objects.get (key = 'email_address').value
        print  Setting.objects.get (key = 'sms24x7_password').value
        """
        return False
 
    

class Command(BaseCommand):
    def handle(self, *args, **options):
        orders = Order.objects.filter (processed = False)
        testing_pattern = re.compile (u'^тестирую.*', re.I + re.U)
        for order in orders:
            for contact in Contact.objects.all():
                if '@' in contact.contact_detail:
                    res = send_email(u'Заказ № ' + str (order.id), order.to_email_plain(), order.to_email_html(), contact.contact_detail)
                elif re.match ('\d{7}', contact.contact_detail): 
                    if not testing_pattern.match(order.comment):
                        res = (send_sms (order, contact.contact_detail))
                    else:
                        continue
                else:
                    res = False
                ostcr = OrderSentToContactResult (order = order, contact = contact, res = res)
                ostcr.save() 
            order.processed = True
            order.save()
