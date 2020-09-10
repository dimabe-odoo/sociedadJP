odoo.define('pos_discount.andes', function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;
    var loan = 0
    models.Order = models.Order.extend({
        initialize: function () {
            _super_order.initialize.apply(this, arguments);
        },
        export_as_JSON: function () {
            var self = this;
            var json = _super_order.export_as_JSON.apply(this, arguments);
            console.log(json)
            if (json.lines) {
                json.lines.forEach(function (e) {
                    e.forEach(function (a) {
                        if (a.loan > a.qty) {
                            self.pos.gui.show_popup('error', {
                                title: ('Cantidad de prestamo'),
                                body: ('La cantidad de prestamo no puede ser mayor a la cantidad a comprar')
                            })
                        }
                    })
                })
            }
            return json;
        }
    })
    var discount_button = screens.ActionButtonWidget.extend({
        template: 'BtnDiscount',
        button_click: function () {
            var self = this
            var order = this.pos.get_order();
            console.log(order)
            if (order.selected_orderline) {
                self.pos.gui.show_popup('number',{
                    title : 'Cantidad de cilindros a prestar',
                    confirm : function () {
                        self['loan'] = document.getElementsByClassName('popup-input value active')[0].innerHTML;
                        console.log(order.selected_orderline)
                    }
                })
            } else {
                self.pos.gui.show_popup('error', {
                    title: ('Sin Producto'),
                    body: ('Debe seleccionar un producto para realizar prestamo')
                })
            }
            console.log(self)
        },

    })
    screens.define_action_button({
        'name': 'discount_btn',
        'widget': discount_button
    });
});