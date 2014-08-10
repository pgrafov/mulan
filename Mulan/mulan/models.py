# coding=utf-8
from django.db.models import *
from django.core.exceptions import ValidationError
from pytils import translit
import re, math


def pretty_float (f):
    return unicode(('%.2f' % f).replace('.00', '' ))

def remove_short_numbers (text):
    return re.sub ('(?<!\d)(\d{1})(\d{3})(?!\d)', r'\1 \2', text)

def validate_code(value):
    if len(value.split("-")) != 2 or not value.split("-")[1].isdigit() or not re.match("[A-Z]",value.split("-")[0]): 
        raise ValidationError(u'%s некорректный код' % value)

class Text (Model):
    header = CharField(null = True, blank = True, max_length = 200)
    text = TextField(null = False)
    order = IntegerField (null = False)
    rtype = CharField(null = False, max_length = 20)
    
    class Meta:
        verbose_name = u"Текст"
        verbose_name_plural = u"Тексты"
        
    def __unicode__ (self):
        return self.header if self.header else u"Текст без заголовка"


class MenuCat (Model):
    name = CharField(null = False,  max_length = 50)
    order = IntegerField (null = False)
    pic = CharField (null = True, blank = True, max_length = 30) 
    picover = CharField (null = True, blank = True, max_length = 30) 
    
    def is_empty(self):
        return (MenuEntry.objects.filter (menucat = self).count() == 0)
    
    def code (self):
        return (MenuEntry.objects.filter (menucat = self)[0].code[0] if MenuEntry.objects.filter (menucat = self).count() else '')
    
    class Meta:
        verbose_name = u"Категория основного меню"
        verbose_name_plural = u"Категории основного меню"
    
    def __unicode__ (self):
        return self.name   
    
class MenuEntry (Model):
    name = CharField(null = False,  max_length = 200, verbose_name = u'Название')
    order   = IntegerField (null = False, verbose_name = u'Порядок в меню', editable = False) 
    menucat = ForeignKey(MenuCat, null = False, verbose_name = u'Категория меню') 
    price = IntegerField (null = False, verbose_name = u'Цена')
    code = CharField(null = False,  max_length = 10, verbose_name = u' Код_', validators=[validate_code])
    
    chinese_name = CharField(max_length = 10, blank = True, verbose_name = u'Название по-китайски')
    contents = CharField( max_length = 200, blank = True, verbose_name = u'Ингридиенты')
    weight = IntegerField (null = True, verbose_name = u'Вес')
    
    def __unicode__ (self):
        return self.name 
    
    class Meta:
        verbose_name = u"Блюдо основного меню"
        verbose_name_plural = u"Блюда основного меню"

    def picture (self):
        return self.code.replace ("-", "") + (".png")
    
    def thumbnail (self):
        return self.picture().split(".")[0] + ".thumbnail." +  self.picture().split(".")[1]
    
    def save(self, *args, **kwargs):
        self.order = int(self.code.split("-")[1]) - 1
        super(MenuEntry, self).save(*args, **kwargs) # Call the "real" save() method.
        
class BLMenuCat (Model):
    name = CharField(null = False,  max_length = 50)
    order = IntegerField (null = False)
    weight = IntegerField (null = True)
    name_singular = CharField (null = False, max_length = 200)
    
    class Meta:
        verbose_name = u"Категория меню бизнес-ланча"
        verbose_name_plural = u"Категории меню бизнес-ланча"
 
    def __unicode__ (self):
        return self.name 
    
class BLMenuEntry (Model):
    name = CharField(null = False,  max_length = 200)
    order   = IntegerField (null = False) 
    blmenucat = ForeignKey(BLMenuCat, null = False) 
    stars = IntegerField (null = False)
    contents = CharField(max_length = 200, blank = True)
    price = IntegerField ()
    variant = IntegerField(null = True)  

    def __unicode__ (self):
        return self.name 
    
    class Meta:
        verbose_name = u"Блюдо меню бизнес-ланча"
        verbose_name_plural = u"Блюда меню бизнес-ланча"

class Street (Model):
    name = CharField (max_length = 25)
    type = CharField (max_length = 10)

    def __unicode__ (self):
        return self.name + " " + self.type
    
    class Meta:
        verbose_name = u"Улица"
        verbose_name_plural = u"Улицы"
    

      
        
class Order (Model):
    created = DateTimeField (auto_now_add = True, verbose_name=u"Создан когда")
    processed =  BooleanField (default = True, verbose_name=u"Передан в доставку")
    
    street = ForeignKey (Street, null = False, verbose_name=u"Улица")
    house_no = CharField (max_length = 7, verbose_name=u"Дом")
    appartment_no = IntegerField (blank = True, null = True, verbose_name=u"Квартира")
    
    phoneNo = CharField (max_length = 20, verbose_name=u"Телефон")    
    cardNo = CharField (blank = True, null = True, max_length = 10, verbose_name=u"№ карты гостя")
    name = CharField(blank = True, null = True, max_length = 20, verbose_name=u"Ваше имя")
    comment = TextField(blank = True, null = True, max_length = 100, verbose_name=u"Комментарий")
   
    
  
    class Meta:
        verbose_name = u"Заказ на доставку"
        verbose_name_plural = u"Заказы на доставку"
    
    def sent_status (self):
        if not self.processed:
            return u"Ещё не послан"
        else:
            retStr = u"Послан: "
            for ostcr in OrderSentToContactResult.objects.filter(order = self).order_by ('contact'):
                retStr += ostcr.contact.contact_detail + u" - " + [u"неудача", u"успех"][ostcr.res]+ ", "
            return retStr[:-2]
    
    sent_status.short_description = u'Результат отправки по контактам' 
        
    def address (self):
        appartment_no_str = (u" кв. " + unicode(self.appartment_no) if not self.appartment_no is None else u'')
        return  unicode(self.street) + u" д. " + self.house_no +  appartment_no_str
    
    address.short_description = u'Адрес'
  
    def to_email_plain (self):
        return  ((u"Адрес: " + self.address() + "\n" if self.address else '') + 
                (u"Телефон: " + self.phoneNo + "\n" if self.phoneNo else '') +
                (u"№ карты гостя: " + self.cardNo + "\n" if self.cardNo else '') +
                (u'Содержимое заказа и стоимость: ' + self.orderItems(compact = False) + "\n") +
                (u"Имя гостя: " + self.name +"\n" if self.name else '') +
                (u"Комментарий: " + self.comment +"\n" if self.comment else ''))
    
    to_email_plain.short_description = u'Содержимое письма'
    
    def to_email_html(self):
        return  (
                  u'<p>' + (u"<b>Адрес: </b>" + self.address()  if self.address else '')  + '</p>' + 
                  u'<p>' + (u"<b>Телефон: </b>" + self.phoneNo  if self.phoneNo else '') + '</p>' +
                  u'<p>' + (u"<b>№ карты гостя: </b>" + self.cardNo  if self.cardNo else '') + '</p>'  +
                  u'<p>' + (u'<b>Содержимое заказа и стоимость: </b>' + '</p>' ) + 
                   self.orderItemsHtml()  +
                  u'<p>' + (u"<b>Имя гостя: </b>" +   self.name +"\n" if self.name else '') + '</p>'
                  u'<p>' + (u"<b>Комментарий: </b>" + self.comment +"\n" if self.comment else '')+ '</p>'
                 )
    
    def to_sms (self):
        addr_part  = remove_short_numbers (translit.translify(u"Addr:" + self.address()))
        tel_part = remove_short_numbers (translit.translify(u"Tel:" + self.phoneNo))
        order_part = remove_short_numbers (translit.translify(u'Zakaz:' + self.orderItems()))
        name_part = remove_short_numbers (translit.translify(u"Imya:" + self.name if self.name else u''))
        comment = remove_short_numbers (translit.translify (u"Komment:" + self.comment if self.comment else u''))
        zakaz = " ".join ([addr_part, tel_part, order_part])    
        if (name_part) and (len(zakaz) + len(" ")+ len(name_part))  <= 160:
            zakaz += " " + name_part
        if (comment) and (len(zakaz) + len(" ")+ len(comment))  <= 160:
            zakaz += " " + comment
        if len(zakaz) <= 160:
            return zakaz
        else:
            return u"Shlishkom dlinnyi zakaz! Smotrite na sayte ili na pochte!"
        
    to_sms.short_description = u'Содержимое смс сообщения'
    
    def blitems_from_code (self, item_code):
        blitems = []
        if "-" in item_code:
            blitem_ids = [int(i) for i in item_code.split("-")[1:]]
            blitems = [BLMenuEntry.objects.get(pk = blitem_id) for blitem_id in blitem_ids]
        else:
            blitem_id = int(item_code[3:])
            blitems = [BLMenuEntry.objects.get(pk = blitem_id)]
        return blitems 
        
    def item_to_string (self, item, compact):
        retStr = u""
        if (item.item):
            if compact:
                retStr +=  item.item.code.replace(u"-", u"") 
            else:
                retStr += (item.item.code.replace(u"-", u"") + u"-" +  item.item.name)      
        else:
            
            blitems =  self.blitems_from_code (item.code)            
            
            
            if compact:
                retStr += u'BL'
                if len(blitems) > 1:
                    for blitem in blitems:
                        retStr += unicode(blitem.order)
                else:
                    blitem = blitems[0]
                    for blmenucat in BLMenuCat.objects.order_by('order'):
                        if blmenucat != blitem.blmenucat:
                            retStr += u'0'
                        else:
                            retStr += unicode (blitem.order)
            else:
                retStr += (u"Бизнес-ланч" if len(blitems) > 1 else u"Доп. блюдо к бизнес-ланчу") + u". "  
                for i in xrange (len(blitems)):
                    blitem = blitems [i]
                    retStr += blitem.blmenucat.name_singular + u"-" + unicode(blitem.order)
                    if i != len(blitems) - 1:
                        retStr += u", "
                
        return retStr
    
    def calc_order_total (self):
        total = 0
        items = OrderItem.objects.filter(order = self)
        for item in items:
            total += self.calc_item_total(item)
        total += self.calc_delivery_total(items)[1]
        total += self.calc_lunchboxes_total(items)[1]
        total -= self.calc_discount_total(items)[1]
        return total
            
            
    
    def calc_blitem_price (self, item):
        min_bl_price = int(Setting.objects.get(key = 'blprice2').value)
        max_price = 0
        assert (item.code)
        blitems =  self.blitems_from_code (item.code)
        if len(blitems) > 1:
            max_price = 0
            for blitem in blitems:
                cur_price = int(Setting.objects.get(key = 'blprice' + str(blitem.stars)).value)
                if cur_price < min_bl_price:
                    cur_price = min_bl_price
                if cur_price > max_price:
                    max_price = cur_price
            return max_price
        else:
            return blitems[0].price
       
    def calc_item_total (self, item):
        if (item.item):
            return (item.item.price ) * item.quantity
        else:
            return (self.calc_blitem_price (item) ) * item.quantity
    
    def calc_delivery_total_menu (self, items):
        return self.calc_delivery_total([item for item in items if (item.item)])

    def calc_delivery_total_bl (self, items):
        return self.calc_delivery_total([item for item in items if not (item.item)])

    def calc_lunchboxes_total_menu (self, items):
        return self.calc_lunchboxes_total([item for item in items if (item.item)])

    def calc_lunchboxes_total_bl (self, items):
        return self.calc_lunchboxes_total([item for item in items if not (item.item)])


    def calc_delivery_total (self, items):
        delivery_total = 0
        delivery_total_price = 0
        for item in items:
            if (item.item):
                delivery_total_price += (int(Setting.objects.get(key='menu_delivery').value)) * item.quantity
            else:
                delivery_total_price += int(Setting.objects.get(key='bl_delivery').value) * item.quantity
            delivery_total += 1 * item.quantity
        return (delivery_total, delivery_total_price)
            
    def calc_lunchboxes_total (self, items):
        lunchboxes_total = 0
        lunchboxes_total_price = 0
        for item in items:
            if (item.item):
                lunchboxes_total_price += int(Setting.objects.get(key='menu_lunch_box').value) * item.quantity
                lunchboxes_total += 1 * item.quantity
            else:
                lunchboxes_total_price += int(Setting.objects.get(key='bl_lunch_box').value) * item.quantity
                lunchboxes_total += 2 * item.quantity
        return (lunchboxes_total, lunchboxes_total_price)
    
    def calc_discount_total (self, items):
        discount_total = 0
        discount_total_price = 0
        for item in items:
            if (item.item):
                discount_percent = int(Setting.objects.get(key='menu_discount').value) 
                if discount_percent > 0:
                    discount_total_price += item.item.price * (discount_percent / 100.0) * item.quantity
                    discount_total += 1 * item.quantity
            else:
                discount_percent = int(Setting.objects.get(key='bl_discount').value)
                if discount_percent > 0:
                    discount_total_price +=  self.calc_blitem_price (item) * (discount_percent / 100.0) * item.quantity
                    discount_total += 1 * item.quantity
        #discount_total_price = (discount_total_price)
        return (discount_total, discount_total_price)
    
    def orderItems(self, compact = True, with_total = True):
        items = OrderItem.objects.filter(order = self)
        retStr = u""
        total = 0
        for i in xrange (len(items)):
            if not compact:
                retStr += u"\n" + str(i+1) + u". " 
            retStr += self.item_to_string (items[i], compact) + (u"\t\t\t" if not compact else u"") +(u"x" + unicode(items[i].quantity) if items[i].quantity > 1 else u"")
            total += self.calc_item_total(items[i])
            if compact:
                if (i != len(items) - 1):
                    retStr += u", "
        total += self.calc_delivery_total(items)[1]
        total += self.calc_lunchboxes_total(items)[1]
        total -= self.calc_discount_total(items)[1]
        if with_total:
            retStr += (u" - " if compact else u'\nИтoго: ') + pretty_float (total) + u" руб."
        return retStr
    
    orderItems.short_description = u'Содержимое заказа и стоимость'
    
    def orderItemsHtml(self):
        table_style =  u'style="border: 1px solid;padding: 5px;"'
        table_contents = u"""<thead>
        <tr>
        <th %table_style%>№.</th>
        <th %table_style%>Блюдо</th>
        <th %table_style%>Кол-во</th>
        <th %table_style%>Сумма</th>
        </tr>
        </thead>
        <tbody>""".replace (u'%table_style%', table_style) 
        items = OrderItem.objects.filter(order = self)
        items_total_price = 0
        tr_count = 0
        for item in items:
            items_total_price += self.calc_item_total(item)
            table_contents += (u'<tr>' +
            u'<td ' + table_style + u' align="center">' + unicode (tr_count + 1) + u'.' +  u'</td>' +                                
            u'<td ' + table_style + u'>'+  self.item_to_string (item, False)+ u'</td>' + 
            u'<td ' + table_style + u' align="center" >'+ unicode(item.quantity) + u'</td>' +
            u'<td ' + table_style + u' align="right" >'+ unicode (self.calc_item_total(item))+ u'</td></tr>')
            tr_count += 1
        
        lunchboxes_total_menu, lunchboxes_total_price_menu = self.calc_lunchboxes_total_menu(items) 
        if lunchboxes_total_price_menu > 0:
            table_contents += (u'<tr>' +
            u'<td ' + table_style + u' align="center">' + unicode (tr_count + 1) +  u'.' + u'</td>' +     
            u'<td ' + table_style + u'>'+  u'Ланч-боксы (меню)' + u'</td>' + 
            u'<td ' + table_style + u' align="center" >'+ unicode(lunchboxes_total_menu) + u'</td>' +
            u'<td ' + table_style + u' align="right" >'+ unicode (lunchboxes_total_price_menu)+ u'</td></tr>')
            tr_count += 1

        lunchboxes_total_bl, lunchboxes_total_price_bl = self.calc_lunchboxes_total_bl(items) 
        if lunchboxes_total_price_bl > 0:
            table_contents += (u'<tr>' +
            u'<td ' + table_style + u' align="center">' + unicode (tr_count + 1) +  u'.' + u'</td>' +     
            u'<td ' + table_style + u'>'+  u'Ланч-боксы (бизнес-ланч)' + u'</td>' + 
            u'<td ' + table_style + u' align="center" >'+ unicode(lunchboxes_total_bl) + u'</td>' +
            u'<td ' + table_style + u' align="right" >'+ unicode (lunchboxes_total_price_bl)+ u'</td></tr>')
            tr_count += 1
        
        delivery_total_menu, delivery_total_price_menu = self.calc_delivery_total_menu(items)
        if delivery_total_price_menu > 0:
            table_contents += (u'<tr>' +
            u'<td ' + table_style + u' align="center">' + unicode (tr_count + 1) +  u'.' +  u'</td>' +     
            u'<td ' + table_style + u'>'+  u'Доставка (меню)' + u'</td>' + 
            u'<td ' + table_style + u' align="center" >'+ unicode(delivery_total_menu) + u'</td>' +
            u'<td ' + table_style + u' align="right" >'+ unicode (delivery_total_price_menu)+ u'</td></tr>')
            tr_count += 1

        delivery_total_bl, delivery_total_price_bl = self.calc_delivery_total_bl(items)
        if delivery_total_price_bl > 0:
            table_contents += (u'<tr>' +
            u'<td ' + table_style + u' align="center">' + unicode (tr_count + 1) +  u'.' +  u'</td>' +     
            u'<td ' + table_style + u'>'+  u'Доставка (бизнес-ланч)' + u'</td>' + 
            u'<td ' + table_style + u' align="center" >'+ unicode(delivery_total_bl) + u'</td>' +
            u'<td ' + table_style + u' align="right" >'+ unicode (delivery_total_price_bl)+ u'</td></tr>')
            tr_count += 1
        
        discount_total, discount_total_price = self.calc_discount_total (items)
        if discount_total_price > 0:
            table_contents += (u'<tr>' +
            u'<td ' + table_style + u' align="center">' + unicode (tr_count + 1) +  u'.' +  u'</td>' +     
            u'<td ' + table_style + u'>'+  u'Скидка' + u'</td>' + 
            u'<td ' + table_style + u' align="center" >'+ unicode(discount_total) + u'</td>' +
            u'<td ' + table_style + u' align="right" >'+ pretty_float (discount_total_price)+ u'</td></tr>')
            tr_count += 1
        delivery_total_price = delivery_total_price_menu + delivery_total_price_bl
        lunchboxes_total_price = lunchboxes_total_price_menu + lunchboxes_total_price_bl
        total = delivery_total_price + lunchboxes_total_price + items_total_price - discount_total_price
        table_contents +=  (u'<tr>' +
            u'<td ' + table_style + u' colspan="3" align="right">'+  u'<b>Итого:</b>' + u'</td>' + 
            u'<td ' + table_style + u' align="right" ><b>'+ pretty_float (total)+ u'</b></td></tr>')      
        return (u'<table ' + table_style + u'>' +
                 table_contents
                + u'</table>') 
       
class OrderItem (Model):
    item = ForeignKey(MenuEntry, null = True) 
    code = CharField (blank = True, null = True, max_length = 20)
    order = ForeignKey (Order, null = False)
    quantity = IntegerField (null = False, default = 1) 
 
class OrderHistory(Model):
    original_order = ForeignKey(Order, null = False)
    created = DateTimeField (null = False, verbose_name=u"Создан когда")
    money =  FloatField (verbose_name = u"К оплате клиентом")
    
    def original_order_text (self):
        return self.original_order.orderItems(with_total = False)
    original_order_text.short_description = u'Содержимое заказа и стоимость'
    
    def calc_positions (self):
        pos_count = 0
        items = OrderItem.objects.filter(order = self.original_order)
        for item in items:
            pos_count += item.quantity
        return pos_count
    
    def is_menu_order(self):
        items = OrderItem.objects.filter(order = self.original_order)
        for item in items:
            if (item.code):
                return False
        return True
    
    def is_bl_order(self):
        items = OrderItem.objects.filter(order = self.original_order)
        for item in items:
            if not (item.code):
                return False
        return True
    
    def is_combined_order(self):
        return not(self.is_menu_order() or self.is_bl_order())
        
    class Meta:
        verbose_name = u"Заказ (кратко)"
        verbose_name_plural = u"Заказы (кратко)" 
    
class Contact (Model):
    contact_detail = CharField (max_length = 50, verbose_name=u"Детали")
    class Meta:
        verbose_name = u"Контакт"
        verbose_name_plural = u"Контакты"
        
class OrderSentToContactResult(Model):
    res = BooleanField()
    contact = ForeignKey (Contact)
    order = ForeignKey (Order)
    
class Setting (Model):
    class Meta:
        verbose_name = u"Настройка"
        verbose_name_plural = u"Настройки"
   
    key = CharField (max_length = 30)
    value = CharField (max_length = 30)
    description = CharField (blank = True, null = True, max_length = 100)
