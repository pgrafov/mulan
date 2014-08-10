from django.conf.urls.defaults import *

urlpatterns = patterns('mulan.views',
    (r'^contacts', 'Contacts'),
    (r'^menu(?:/(-?\d+))?', 'Menu'),
    (r'^business(\+)?', 'BusinessLunch'),
    (r'^vacancies', 'Vacancies'),
    (r'^delivery_success', 'DeliverySuccess'),
    (r'^delivery', 'Delivery'),
    (r'^upload', 'Upload'),
    (r'^new_prices([+-]?\d+).txt', 'NewPricesTxt'),
    (r'^price_increase', 'PriceIncrease'),
    (r'^stats/xls', 'StatsXls'),
    (r'^$', 'MainPage'),
    (r'^.*$', 'MainPageRedirect'),
)


