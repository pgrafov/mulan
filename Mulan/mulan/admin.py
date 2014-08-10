from mulan.models import *
from django.contrib import admin

    
class TextAdmin(admin.ModelAdmin):
    list_display = ('order', 'rtype', 'header', 'text')
    list_display_links = ('rtype',)
    
class MenuCatAdmin(admin.ModelAdmin):
    list_display = ('order', 'name')
    list_display_links = ('name',)
    
class BLMenuCatAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'weight', 'name_singular')
    list_display_links = ('name',)
    
class MenuEntryAdmin(admin.ModelAdmin):
    list_display = ('order', 'code', 'name', 'chinese_name', 'contents', 'price', 'weight', 'menucat')
    list_filter = ('menucat',)
    list_display_links = ('name',)
    list_editable = ('price',)
    
class BLMenuEntryAdmin(admin.ModelAdmin):
    list_display = ('order', 'name',  'contents', 'price', 'stars', 'variant', 'blmenucat')  
    list_filter = ('variant',)
    list_display_links = ('name',)
    list_editable = ('price',)

class OrderAdmin (admin.ModelAdmin):
    list_display = ('created', 'phoneNo', 'sent_status', 'address', 'cardNo', 'orderItems', 'to_sms', 'to_email_plain')
 
class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact_detail',)
    
class SettingAdmin(admin.ModelAdmin):
    list_display = ('description', 'value')
    list_editable = ('value',)
    list_display_links = ('description', )
    
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('original_order_text', 'created', 'money')
    
       
admin.site.register( Text, TextAdmin )
admin.site.register( MenuCat, MenuCatAdmin )
admin.site.register( MenuEntry, MenuEntryAdmin)
admin.site.register( BLMenuCat, BLMenuCatAdmin )
admin.site.register( BLMenuEntry, BLMenuEntryAdmin)
admin.site.register( Order, OrderAdmin)
admin.site.register( Contact, ContactAdmin)
admin.site.register (Setting, SettingAdmin)
admin.site.register (Street)
admin.site.register (OrderHistory, OrderHistoryAdmin)

