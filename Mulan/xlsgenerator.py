import xlwt

def generate_stats_xls (lines):
    font_menucat = xlwt.Font()
    font_menuentry = xlwt.Font()
    font_menucat.bold = True
    font_menuentry.bold = False
    
    style_menucat = xlwt.XFStyle()
    style_menucat.font = font_menucat
    style_menuentry = xlwt.XFStyle()
    style_menuentry.font = font_menuentry
    
    wb = xlwt.Workbook()
    ws = wb.add_sheet(u'\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430')
    
    widths = [0,0,0]
    cur_index = 0
    for line in lines:
        if line[1].upper () == line[1]:
            style = style_menucat
        else:
            style = style_menuentry
        for i in xrange(len(line)):
            if len (unicode(line[i])) > widths[i]:
                widths[i] = len(unicode(line[i]))
            assert (isinstance(line[i], unicode) or isinstance(line[i], int)), line[i]
            ws.write(cur_index, i, (line[i] if i!=2 else int(line[i])), style)
        cur_index += 1
        
    # adjusting widths
    for i in xrange(len(widths)):
        col = ws.col(i)
        col.width = 256 * widths[i] + 200   
    
    return wb