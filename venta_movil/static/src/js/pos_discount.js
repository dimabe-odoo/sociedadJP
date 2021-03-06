odoo.define('pos_discount.andes', function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
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
                            this.pos['loan'] = loan;

                            this.pos['selected_product'] = order.selected_orderline.product.id
                        }
                    }
                })
            } else {
                self.pos.gui.show_popup('error', {
                    title: ('Sin Producto'),
                    body: ('Debe seleccionar un producto para realizar prestamo')
                })
            }
        },

    })
    screens.define_action_button({
        'name': 'discount_btn',
        'widget': discount_button,

    });
});