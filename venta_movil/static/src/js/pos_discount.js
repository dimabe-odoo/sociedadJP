odoo.define('pos_discount.andes',function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;
    var loan = 0
    var order = this.pos.get_order();
    models.Order = models.Order.extend({
        initialize: function (){
            _super_order.initialize.apply(this,arguments);
            this.loan = 0;
        },
        export_as_JSON: function (){
            var json = _super_order.export_as_JSON.apply(this,arguments);
            console.log(json)
            if(json.lines){
                json.lines.forEach(function (e){
                    e.forEach(function (a) {
                        console.log(this.order);
                        console.log(a)
                    })
                })
            }
            return json;
        }
    })
    var discount_button = screens.ActionButtonWidget.extend({
        template : 'BtnDiscount',
        button_click : function (){
            var self = this
            var order = this.pos.get_order();
            if (order.selected_orderline){
                self.loan = 5
            }
        },

    })
    screens.define_action_button({
        'name':'discount_btn',
        'widget': discount_button
    });
});