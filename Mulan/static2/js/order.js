function onQuantityChanged ()
{
 
 generate_order_table();
 $.cookie('order', JSON.stringify(saved_to_cookies_order), { expires: 7, path: '/' });
 
}

function addOneItem (itemId)
{
  var row_index = jQuery('#tr-'+itemId).index ('#your_order_table tr') - 1;
  var oldval = parseInt(jQuery('#td-'+itemId+'-quantity').html());
  if (oldval != 10)
  {
    jQuery('#td-'+itemId+'-quantity').html(oldval + 1);
    jQuery('#td-'+itemId+'-price').html(parseInt(jQuery('#td-'+itemId+'-price').html()) + saved_to_cookies_order[row_index]['price']);
    saved_to_cookies_order[row_index]['quantity'] = saved_to_cookies_order[row_index]['quantity'] + 1;
  }
  onQuantityChanged ();
  return false;
}
function delOneItem (itemId)
{
  var row_index = jQuery('#tr-'+itemId).index ('#your_order_table tr') - 1;
  var oldval = parseInt(jQuery('#td-'+itemId+'-quantity').html());
  if (oldval != 1)
  {
    jQuery('#td-'+itemId+'-quantity').html( oldval - 1);
    jQuery('#td-'+itemId+'-price').html(parseInt(jQuery('#td-'+itemId+'-price').html()) - saved_to_cookies_order[row_index]['price']);
    saved_to_cookies_order[row_index]['quantity'] = saved_to_cookies_order[row_index]['quantity'] - 1;
    onQuantityChanged ();
  }
  else
    delRow (itemId);
  
  return false;
}
function delRow (itemId)
{
  var row_index = jQuery('#tr-'+itemId).index ('#your_order_table tr') - 1;
  jQuery('#tr-'+itemId).remove();
  saved_to_cookies_order.splice(row_index, 1);
  onQuantityChanged ();
  return false;
}

function addToOrder (eid, name, code, price )
{	
    var found = false;
    for (var i = 0; i < saved_to_cookies_order.length; i++)
    {  
       if (saved_to_cookies_order[i]['id'] == eid)
       {
          saved_to_cookies_order[i]['quantity'] += parseInt($("#quantity_for_" +eid).val());
          found = true;
       }
    } 
	if (!found)
		saved_to_cookies_order.push ({'price':price, 'name': name, 'code':code, 'id': eid, 'quantity': parseInt($("#quantity_for_" +eid).val())});
	$("#quantity_for_" +eid).val(1);
	onQuantityChanged ();	
}

function your_order_are_all_business_lunches ()
{
    for(var i =0; i < saved_to_cookies_order.length; i++)
        if (saved_to_cookies_order[i]['code'].substring(0, 2) != ('bl'))
            return false;
    return true;
}

function generate_order_table()
{

  $('#your_order_table').find ('.order_item').remove();
  $('#delivery').hide();
  $('#lunch_boxes').hide();
  $('#tr-total').remove();

  var price_total = 0;
  var lunch_boxes = 0;
  var lunch_boxes_price = 0;
  var lunch_boxes_2 = 0;
  var lunch_boxes_price_2 = 0;
  var delivery = 0;
  var delivery_price = 0;
  var delivery_2 = 0;
  var delivery_price_2 = 0;
  var discount = 0;
  for(var i =0; i < saved_to_cookies_order.length; i++)
  {

    var eid = saved_to_cookies_order[i]['id']; 
    var quantity = saved_to_cookies_order[i]['quantity'];
    var ename =  saved_to_cookies_order[i]['name'];
    var price = saved_to_cookies_order[i]['price'] * quantity;
    var ecode;
    if (saved_to_cookies_order[i]['code'] != undefined && saved_to_cookies_order[i]['code'].substring(0, 2) != ('bl') )
    {
        ecode = saved_to_cookies_order[i]['code'];
        lunch_boxes += 1 * saved_to_cookies_order[i]['quantity'];
        lunch_boxes_price += const_menu_lunch_box * saved_to_cookies_order[i]['quantity'];
        delivery += 1 * saved_to_cookies_order[i]['quantity'];
        delivery_price += const_menu_delivery * saved_to_cookies_order[i]['quantity'];
        discount += price * (const_menu_discount / 100);
    }
    else if (eid.substring(0, 3)==('bl_'))
    {
        ecode=  ('Доп. блюдо к бизнес-ланчу');
    }
    else 
    {
        ecode = "Бизнес-ланч";
        lunch_boxes_2 += 2 * saved_to_cookies_order[i]['quantity'];
        lunch_boxes_price_2 += const_bl_lunch_box * saved_to_cookies_order[i]['quantity'];
        delivery_2 += 1 * saved_to_cookies_order[i]['quantity'];
        delivery_price_2 += const_bl_delivery * saved_to_cookies_order[i]['quantity'];
        discount += price * (const_bl_discount / 100);
    } 
    
    price_total += price;
    var tdbuttons = '<td>' + 
      '<a href="#" onclick="return addOneItem(\''+ eid +'\');"><img src="/static/plus.png"></a>' + 
      '<a href="#" onclick="return delOneItem(\''+ eid +'\');"><img src="/static/minus.png"></a>' +
      '<a href="#" onclick="return delRow(\''+ eid +'\');"><img src="/static/del.png"></a></td>';
    var new_tr = '<tr class="order_item" id="tr-'+eid+'"><td>' + ecode + '. ' + ename + '</td><td align="center" id="td-'+eid+'-quantity">' + quantity + 
                 '</td>'+ tdbuttons + '<td align="right" id="td-'+eid+'-price">'+ price +'</td></tr>'      
    $('#lunch_boxes').before (new_tr);
  }
  
  if (delivery_price > 0)
  {
    jQuery ("#delivery" + " td:eq(1)").html(delivery);
    jQuery ("#delivery" + " td:eq(3)").html(delivery_price);
    jQuery ("#delivery").show();
  }
  if (lunch_boxes_price > 0)
  {
    jQuery ("#lunch_boxes" + " td:eq(1)").html(lunch_boxes);
    jQuery ("#lunch_boxes" + " td:eq(3)").html(lunch_boxes_price);
    jQuery ("#lunch_boxes").show();
  }  
  if (delivery_price_2 > 0)
  {
    jQuery ("#delivery_2" + " td:eq(1)").html(delivery_2);
    jQuery ("#delivery_2" + " td:eq(3)").html(delivery_price_2);
    jQuery ("#delivery_2").show();
  }
  if (lunch_boxes_price_2 > 0)
  {
    jQuery ("#lunch_boxes_2" + " td:eq(1)").html(lunch_boxes_2);
    jQuery ("#lunch_boxes_2" + " td:eq(3)").html(lunch_boxes_price_2);
    jQuery ("#lunch_boxes_2").show();
  }  
  
  if (discount > 0)
  {
    if (!(const_bl_discount > 0 && const_menu_discount > 0))
    {
        var discount_value = (const_bl_discount == 0) ? const_menu_discount : const_bl_discount;
        jQuery('#discount_value').html("(" + discount_value + "%)");
    }
    /*discount = (discount);*/
    jQuery ("#discount" + " td:eq(3)").html('<b>-' + discount.toFixed(2) + '<b>');
    jQuery ("#discount").show();
  }
  price_total += (delivery_price + lunch_boxes_price + delivery_price_2 + lunch_boxes_price_2 - discount);
  var summary_tr = '<tr id="tr-total"><td colspan="3" align="right"><b>Итого:</b></td><td id="td-total" align="right">'+ price_total.toFixed(2) +'</td></tr>'
  $('#your_order_table').append (summary_tr);
  $("#td-total").removeClass('highlighted-cell');
  var min_order = (your_order_are_all_business_lunches () ? const_bl_min_order: const_menu_min_order);
  $('#min_order_price').html (min_order);
  if (saved_to_cookies_order.length > 0)
  {
    
    $("#your_order_empty").hide();
    $("#your_order_table").show();
  }
  else
  {
    if ($('#your_order_empty_what_to_do').length == 0)
    {
        $("#your_order_empty").show();
        $("#your_order_table").hide();
     }
     else
     {
        $('#your_order_empty_what_to_do').show();
        $('#basket').hide();
     }
  }
  if (price_total < min_order )
  {
    if (price_total > 0)
    {
        $("#td-total").addClass('highlighted-cell');
        $('#invalid_total').show();
        $('#link_to_order_more').attr ('href', (your_order_are_all_business_lunches()? '/business+' : '/menu'))
    }
    else
       $('#invalid_total').hide(); 
    $("#finalize_order").hide();
  }
  else
  {
    $("#td-total").removeClass('highlighted-cell');
    $('#invalid_total').hide();
    $("#finalize_order").show();  
  }
}
