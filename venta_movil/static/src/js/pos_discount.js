odoo.define('pos_discount.andes',function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;
    var loan = 0

    var discount_button = screens.ActionButtonWidget.extend({
        template : 'BtnDiscount',
        button_click : function (){
            var self = this
            var order = this.pos.get_order();
            console.log(order)
        },

    })
    screens.define_action_button({
        'name':'discount_btn',
        'widget': discount_button
    });
});