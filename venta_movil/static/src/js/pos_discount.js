odoo.define('pos_discount.andes', function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;
    var discount_button = screens.ActionButtonWidget.extend({
        template: 'BtnDiscount',
        button_click: function () {
            var self = this
            var order = this.pos.get_order();
            if (order) {
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
                                self.pos['loan'] = loan;
                                self.pos['selected_product'] = order.selected_orderline.product.id
                                order.selected_orderline['loan'] = loan
                            }
                        }
                    })
                } else {
                    self.pos.gui.show_popup('error', {
                        title: ('Sin Producto'),
                        body: ('Debe seleccionar un producto para realizar prestamo')
                    })
                }
            }
        },
    });
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var data = _super_order.export_as_JSON.apply(this, arguments);
            if (data != null) {
                var order = this.pos.get_order();
                if (order != null) {
                    for (var lines of order.orderlines.models) {
                        if (lines.loan != null) {
                            if(data.lines.filter(element => element[2].id == lines.id)[0] != null){
                                data.lines.filter(element => element[2].id == lines.id)[0][2]['loan'] = lines.loan;
                            }
                        }
                    }
                }
            }
            return data;
        }
    })
    screens.define_action_button({
        'name': 'discount_btn',
        'widget': discount_button,

    });
});