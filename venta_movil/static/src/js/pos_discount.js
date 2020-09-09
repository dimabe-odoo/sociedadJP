odoo.define('pos_discount.andes',function (require) {
    var screens = require('point_of_sale.screens');
    var discount_button = screens.ActionButtonWidget.extend({
        template : 'BtnDiscount',
        button_click : function (){
            var order = this.pos.get_order();
            if (order.selected_orderline){
                console.log(order.selected_orderline);
            }
        }
    })
    screens.define_action_button({
        'name':'discount_btn',
        'widget': discount_button
    });
});