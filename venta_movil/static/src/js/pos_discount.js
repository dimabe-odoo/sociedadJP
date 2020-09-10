odoo.define('pos_discount.andes', function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;
    var loan = 0
    var discount_button = screens.ActionButtonWidget.extend({
        template: 'BtnDiscount',
        button_click: function () {
            var self = this
            var order = this.pos.get_order();
            if (order.selected_orderline) {
                self.pos.gui.show_popup('number', {
                    title: 'Cantidad de cilindros a prestar',
                    confirm: function () {
                        let loan = parseInt(document.getElementsByClassName('popup-input value active')[0].innerHTML);
                        if (loan > order.selected_orderline.quantity) {
                            self.pos.gui.show_popup('error', {
                                title: 'Error',
                                body: 'Cantidad a prestar no puede ser mayor a la cantidad a comprar'
                            })
                        } else {
                            let _super_order_2 = models.Order.prototype;
                            models.Order = models.Order.extend({
                                initialize: function () {
                                    _super_order_2.initialize.apply(this, arguments);
                                },
                                export_as_JSON: function () {
                                    var json = _super_order_2.export_as_JSON.apply(this, arguments);
                                    console.log(json)
                                    if (json.lines) {
                                        json.lines.forEach(function (e) {
                                            e.forEach(function (a) {
                                                a.loan = loan
                                            })
                                        })
                                    }
                                    return json;
                                }
                            })
                        }
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
        'widget': discount_button,

    });
});