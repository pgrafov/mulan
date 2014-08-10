# coding=utf-8
from django.http import  HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
from models import *
from forms import *
from xlsgenerator import generate_stats_xls
import os, re

from PIL import Image

mymenu = [{"href":'/',
                 "text": u"Главная"
                },
                {"href": "#",
                 "text": u"Меню",
                 'children': [{"href": "/static/menu.pdf", "text":u"Меню блюд"},
                              {"href": "/static/bar.pdf", "text":u"Барная карта"},
                              {"href": "/business", "text":u"Меню бизнес-ланча"}]
                },

                {"href":"/contacts",
                 "text": u"Контакты"
                },
                {"href":"/vacancies",
                 "text": u"Вакансии"
                },
                {"href":"/menu",
                 "text":u"Доставка",
                 'children': [{"href": "/delivery", "text": u"Условия доставки"},
                              {"href": "/menu", "text":u"Доставка блюд меню"},
                              {"href": "/business+", "text":u"Доставка бизнес-ланча"}
                              ]
                }]
class TreeNode():
    def __init__ (self, val):
        self.val  = val
        self.children = []

    def addChild(self, val):
        self.children.append (TreeNode(val))
        return self.children[-1]

class Tree():
    def __init__(self, val, showRoot = False):
        self.root = TreeNode(val)

    def getRoot (self):
        return self.root

    def addChild (self, val):
        return self.root.addChild(val)

class MainMenuGenerator ():
    def __init__ (self, menulst = None):
        self.tree = Tree({}, False)
        if not menulst is None:
            self.populate_menu_with(menulst)

    def render_menu(self, node = None, level = 0):
        if node is None:
            node = self.tree.getRoot()
        children = "".join([self.render_menu(n, level + 1) for n in node.children ])
        if level != 0:
            return ('<li >' +
                    '<a  href="' + node.val['href'] + '">' +
                    node.val['text'] + '</a>'  +
                    ('<ul>' + children + '</ul>' if children else '') +
                    '</li>')
        else:
            return '<ul id = "jsddm">' + children + "</ul>"




    def populate_menu_with(self,  menulst, node = None):
        if node is None:
            node = self.tree.getRoot()
        for m in menulst:
            nodeNext = node.addChild ({'href' : m['href'], 'text' : m ['text']})
            if m.has_key ('children'):
                self.populate_menu_with(m['children'], nodeNext)






def populate_template_values (request, url, rtype, atype = u"Акция"):
    template_values = {}
    template_values.update(csrf(request))
    template_values['menu_generator'] = MainMenuGenerator (mymenu)
    template_values['bl_discount'] = Setting.objects.get(key='bl_discount').value
    template_values['menu_discount'] = Setting.objects.get(key='menu_discount').value
    template_values['bl_min_order'] = Setting.objects.get(key='bl_min_order').value
    template_values['menu_min_order'] = Setting.objects.get(key='menu_min_order').value
    template_values['bl_lunch_box'] = Setting.objects.get(key='bl_lunch_box').value
    template_values['menu_lunch_box'] = Setting.objects.get(key='menu_lunch_box').value
    template_values['bl_delivery'] = Setting.objects.get(key='bl_delivery').value
    template_values['menu_delivery'] = Setting.objects.get(key='menu_delivery').value
    template_values["req_url"] = url
    template_values['records'] = Text.objects.filter (rtype = rtype).order_by('order')
    template_values['siderecords'] = Text.objects.filter (rtype = atype).order_by('order')
    template_values['topleftrecords'] = Text.objects.filter (rtype = u"Сверху слева").order_by('order')
    template_values['toprightrecords'] = Text.objects.filter (rtype = u"Сверху справа").order_by('order')
    menu_generator = MainMenuGenerator(mymenu)
    template_values['menu_generated'] = menu_generator.render_menu()
    return template_values


def MainPage (request):
    return render_to_response ("index.html", populate_template_values (request, "main", u"О нас"))

def MainPageRedirect (request):
    return HttpResponseRedirect ("/")

def Contacts (request):
    return render_to_response ("base.html", populate_template_values (request, "contacts", u"Карта", u'Контакты'))

def Vacancies (request):
    return render_to_response ("base.html", populate_template_values (request, "vacancies", u"Вакансии"))

def new_price_print_or_update(price_delta, update = False):
    txt_file_content = ""
    for menucat in MenuCat.objects.all().order_by('order'):
        if MenuEntry.objects.filter (menucat = menucat).count():
            txt_file_content += "=== " + menucat.name.encode('utf-8') + " ===" + "\n"
        menuentries = MenuEntry.objects.filter (menucat = menucat).order_by('order')
        for menuentry in menuentries:
            old_price = menuentry.price
            new_price = int(round(old_price * (100.0 + price_delta) / 100.0))
            if update:
                menuentry.price = new_price
                menuentry.save()
            txt_file_content += menuentry.code.encode('utf-8') + ". " + menuentry.name.encode('utf-8') + " - " + str(new_price) + " (" + str(old_price) +  ")" + "\n"
    return txt_file_content

def PriceIncrease(request):
    if request.user and request.user.is_staff and request.method == 'POST':
        new_price_print_or_update(int(request.POST['price_percent']), True)
    return HttpResponseRedirect(reverse('admin:index'))

def xls_to_response(xls, fname):
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % fname
    xls.save(response)
    return response


def StatsXls (request):
    if request.user and request.user.is_staff and request.method == 'GET':
        orderitems = OrderItem.objects.all()
        lines = []
        items_dict = {}
        cats_dict = {}
        for orderitem in orderitems:
            if orderitem.item:
                if not orderitem.item in items_dict:
                    items_dict[orderitem.item] = 0
                if not orderitem.item.menucat in cats_dict:
                    cats_dict[orderitem.item.menucat] = 0
                items_dict[orderitem.item] += 1
                cats_dict[orderitem.item.menucat] += 1
        for menucat in  MenuCat.objects.all().order_by('order') :
            if menucat.is_empty():
                continue
            lines.append ([u'', menucat.name , (cats_dict[menucat] if menucat in cats_dict else 0) ])
            for menuentry in MenuEntry.objects.filter (menucat = menucat).order_by('order'):
                lines.append ([menuentry.code, menuentry.name, (items_dict[menuentry] if menuentry in items_dict else 0)])
        xls = generate_stats_xls (lines)
        return xls_to_response(xls,'stats.xls')

def NewPricesTxt (request, price_delta_percent):
    if request.user and request.user.is_staff and request.method == 'GET':
        return HttpResponse (new_price_print_or_update(int(price_delta_percent), False),
                         content_type="text/plain; charset=utf-8")
    return HttpResponseRedirect(reverse('admin:index'))

def Upload (request):
    location = None
    basepath  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if request.user and request.user.is_staff and request.method == 'POST':
        if len (request.FILES) == 1 and 'pictype' in request.POST:
            request_file = request.FILES['file']
            name = request_file.name.lower()
            pictype = request.POST['pictype']
            try:
                if pictype == "menupic":
                    correct_name = (re.match ('^[a-z]\d{1,2}$', name.split(".")[0])) and (name.split(".")[1] == "png")
                    stream = request_file.file
                    image = Image.open(stream)
                    if correct_name: # ignore image size
                        location = "static2/pics"
                        name = name.split(".")[0].upper() + "." + name.split(".")[1]
                        image.thumbnail((128, 128), Image.ANTIALIAS)
                        outfile = os.path.join(basepath, location, name.split(".")[0] + ".thumbnail." + name.split(".")[1])
                        image.save(outfile, "PNG")

                elif pictype == "gallerypic":
                        correct_name = (0 < int(name.split(".")[0]) < 20) and (name.split(".")[1] == "jpg")
                        stream = request_file.file
                        image = Image.open(stream)
                        size_x, size_y =  image.size
                        if correct_name and size_y == 510 and (680 <= size_x <= 770 ):
                            location = "static2/photogallery"

                elif pictype == "menupdf":
                    if name == "bar.pdf" or name == "menu.pdf":
                        location = "static2/"
            except Exception as inst:
                pass
            if not location is None:
                with open(os.path.join(basepath, location, name), 'wb+') as destination:
                    for chunk in request_file.chunks():
                        destination.write(chunk)
        if location is None:
            pass#print "Failure!"
    return HttpResponseRedirect(reverse('admin:index'))

def DeliverySuccess (request):
    template_values = populate_template_values (request, "delivery", u"Доставка")
    return render_to_response ("delivery_success.html", template_values)

def Delivery (request):
    template_values = populate_template_values (request, "delivery", u"Доставка")
    template_values['order_created'] = False


    if request.method != 'POST':
        template_values['order_form'] = OrderForm()
    else:
        form = OrderForm(request.POST) # A form bound to the POST data
        if not form.is_valid():
            # give it one more chance
            data = request.POST.copy()
            data['appartment_no'] = u''
            form = OrderForm(data=data)
        if form.is_valid():
            order_contents =  form.cleaned_data['order_contents'].split(",")
            order = form.save()
            for item_quantity in order_contents:
                item_or_code = item_quantity.split(":")[0]
                if item_or_code.startswith ('bl'):
                    code = item_or_code
                    item = None
                else:
                    item = MenuEntry.objects.get(pk = int(item_or_code))
                    code = None
                quantity = int(item_quantity.split(":")[1])
                order_item =  OrderItem(item = item, order = order, quantity = quantity, code = code)
                order_item.save()
            order.processed = False
            order.save()
            order_history = OrderHistory(   original_order = order,
                                            created = order.created,
                                            money = order.calc_order_total())
            order_history.save()
            return HttpResponseRedirect ("delivery_success")

        else:
            template_values['order_creation_failed'] = True
    return render_to_response ("delivery.html", template_values)

def Menu (request, submenu_index):
    submeny_index = 0 if (submenu_index is None) else int(submenu_index)
    if submeny_index == -1:
        return HttpResponseRedirect ("/business+")
    menucats = MenuCat.objects.all().order_by('order')
    cur_menucat = MenuCat.objects.filter(order = submeny_index).get()
    cur_menuentries = MenuEntry.objects.filter (menucat = cur_menucat).order_by('order')
    template_values = {"menucats":menucats, "cur_menucat":cur_menucat , "entries": cur_menuentries}
    template_values.update(populate_template_values(request, "menu", ""))
    template_values.update ({"show_bl": True})
    template_values['preorder'] = True
    template_values['bl_min_order'] = Setting.objects.get(key='bl_min_order').value
    template_values['menu_min_order'] = Setting.objects.get(key='menu_min_order').value
    template_values['bl_lunch_box'] = Setting.objects.get(key='bl_lunch_box').value
    template_values['bl_delivery'] = Setting.objects.get(key='bl_delivery').value
    template_values['menu_lunch_box'] = Setting.objects.get(key='menu_lunch_box').value
    template_values['menu_delivery'] = Setting.objects.get(key='menu_delivery').value
    return render_to_response ("menu.html", template_values)


def BusinessLunch (request, delivery):
    delivery = (False if delivery is None else True)
    preorder = (True if delivery else False)
    template_values = populate_template_values (request, "business", u"Бизнес-ланч")
    if delivery:
        template_values['records'] = template_values['records'][2:]
    else:
        template_values['records'] = template_values['records'][:2]
    cat_entry_dicts = []
    blvariantno = Setting.objects.get (key = 'cur_bl_variant').value
    blvariantno = int(blvariantno)
    cats = BLMenuCat.objects.all().order_by ('order')
    if (delivery):
        cats = cats.exclude (name = u"Напитки")
    for cat in cats:
        entries = BLMenuEntry.objects.filter(blmenucat = cat).filter(Q(variant = blvariantno) | Q(variant = 2) ).order_by ('order')
        cat_entry_dicts.append ({"cat":cat, "entries":entries})
    template_values ["cat_entry_dicts"] = cat_entry_dicts
    template_values ['preorder'] = preorder
    template_values ['show_order_box'] = delivery
    template_values ['bl_cats'] = [cat.name_singular for cat in cats]
    template_values ['blprice1'] = Setting.objects.get (key = 'blprice1').value
    template_values ['blprice2'] = Setting.objects.get (key = 'blprice2').value
    template_values ['blprice3'] = Setting.objects.get (key = 'blprice3').value
    template_values ['blprice4'] = Setting.objects.get (key = 'blprice4').value
    template_values ['delivery'] = delivery
    return render_to_response ("business.html", template_values)
