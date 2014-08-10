#!/usr/bin/python
# -*- coding: utf-8 -*-

from PIL import Image, ImageFont, ImageDraw

left_menupics = {
#u"ФИРМЕННЫЕ БЛЮДА" :"1.png",
#u"ХОЛОДНЫЕ БЛЮДА" :"2.png",
#u"СУПЫ" :"3.png",
#u"ГОРЯЧЕЕ ИЗ ОВОЩЕЙ" :"4.png",
#u"ГОРЯЧЕЕ ИЗ СВИНИНЫ" :"5.png",
#u"ГОВЯДИНА И БАРАНИНА" :"6.png",
#u"ГОРЯЧЕЕ ИЗ ПТИЦЫ" :"7.png",
#u"РЫБА И МОРЕПРОДУКТЫ" :"8.png",
#u"БЛЮДА В ГОРШОЧКЕ" :"9.png",
#u"БЛЮДА В ХОГО" :"10.png",
#u"БЛЮДА НА ПЛИТКЕ" :"11.png",
#u"ГАРНИРЫ" :"12.png",
u"ДЕСЕРТЫ"  :"13.png"
#u"БИЗНЕС-ЛАНЧ": "14.png",
#u"КИТАЙСКОЕ МЕНЮ": "15.png"
}

upper_menupics = {
#u"О нас": ("onas.png", (73,35) ),
#u"Меню": ("menu.png",(88,35) ),
#u"Бизнес-ланч": ("business.png", (155,35) ),
#u"Контакты": ("kontakty.png", (130,35) ),
#u"Вакансии": ("vakansii.png", (121,35) ),
#u"Доставка": ("dostavka.png", (160,35) ),
}
menufont =  "bonzai.ttf"
big_font_size = 44
small_font_size = 34 

menufont =  "chinacyr.ttf"
big_font_size = 25
small_font_size = 17 

for m in left_menupics.keys():
    text_pos = (0,0)
    size = (360, 45) 
    font_size = big_font_size 
    
    im = Image.new('RGB', size) 
    draw = ImageDraw.Draw(im)
    im.putalpha (0)   
                               
    black = (0,0,0, 255)   
   
    font = ImageFont.truetype(menufont, font_size)
    draw.text(text_pos, m, font=font, fill = black)
    im.save(left_menupics[m], 'PNG')
 
    im = Image.new('RGB', size) 
    draw = ImageDraw.Draw(im)
    im.putalpha (0)   
                               
    grey = (123,123,123, 255)   

    font = ImageFont.truetype(menufont, font_size)
    draw.text(text_pos, m, font=font, fill = grey)
    new_name = left_menupics[m].split(".")[0] + "o." + left_menupics[m].split(".")[1]
    im.save(new_name, 'PNG')

for m in upper_menupics.keys():
    text_pos = (0,14)
   
    size = upper_menupics[m][1] 
    font_size = small_font_size            
    

    im = Image.new('RGB', size) 
    draw = ImageDraw.Draw(im)
    im.putalpha (0)   
                               
    black = (0,0,0, 255)   
    
    font = ImageFont.truetype(menufont, font_size)
    draw.text(text_pos , m, font=font, fill = black)
    im.save(upper_menupics[m][0], 'PNG')


          
    
    im = Image.new('RGB', size) 
    draw = ImageDraw.Draw(im)
    im.putalpha (0)   
                               
    grey = (123,123,123, 255)   
    
    font = ImageFont.truetype(menufont, font_size)
    draw.text(text_pos , m, font=font, fill = grey)
    new_name = upper_menupics[m][0].split(".")[0] + "o." + upper_menupics[m][0].split(".")[1]
    im.save(new_name, 'PNG')
    

   
