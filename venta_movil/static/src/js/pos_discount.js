odoo.define('pos_discount.andes',function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var _super_Order = models.Order.prototype;
    var discount_button = screens.ActionButtonWidget.extend({
        template : 'BtnDiscount',
        button_click : function (){
            var order = this.pos.get_order();
            models.Order = models.Order.extend({
                export_as_JSON : function (){
                    var json = _super_Order.export_as_JSON.apply(this,arguments);
                    console.log(json)
                }
            })
            order.selected_orderline['loan'] = 5
            if (order.selected_orderline){
                console.log(order.orderlines.filter(a => a.cid == order.selected_orderline.cid));
            }
        }
    })
    screens.define_action_button({
        'name':'discount_btn',
        'widget': discount_button
    });
});