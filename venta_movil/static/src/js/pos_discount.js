odoo.define('pos_discount.andes',function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;
    var loan = 0
    models.Order = models.Order.extend({
        initialize: function (){
            _super_order.initialize.apply(this,arguments);
            this.loan = 0;
        },
        export_as_JSON: function (){
            var json = _super_order.export_as_JSON.apply(this,arguments);
            console.log(json)
            var order = this.pos.get_order();
            if(json.lines){
                console.log(typeof(json.lines))
                json.lines.loan = 5
            }
            return json;
        }
    })
    var discount_button = screens.ActionButtonWidget.extend({
        template : 'BtnDiscount',
        button_click : function (){
            var order = this.pos.get_order();
            if (order.selected_orderline){
                this.loan = 5
            }
        },

    })
    screens.define_action_button({
        'name':'discount_btn',
        'widget': discount_button
    });
});