odoo.define('pos_discount.andes', function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    screens.ProductListWidget.include({
        render_product: function(product){
            var current_pricelist = this._get_active_pricelist();
            var cache_key = this.calculate_cache_key(product, current_pricelist);
            var cached = this.product_cache.get_node(cache_key);
            if(!cached){
                var image_url = this.get_product_image_url(product);
                var product_html = QWeb.render('Product',{ 
                        widget:  this, 
                        product: product,
                        pricelist: current_pricelist,
                        image_url: this.get_product_image_url(product),
                    });
                console.log(product)
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(cache_key,product_node);
                return product_node;
            }
            return cached;
        }
    });
    var _super_order = models.Order.prototype;
    var loan = 0
    models.Order = models.Order.extend({
        initialize: function () {
            _super_order.initialize.apply(this, arguments);
        },
        export_as_JSON: function () {
            var self = this;
            var json = _super_order.export_as_JSON.apply(this, arguments);
            if (json.lines) {
                json.lines.forEach(function (e) {
                    if (self.pos.loan) {
                        json.is_loan = true;
                    }
                    e.forEach(function (a) {
                        if (a.product_id === self.pos.selected_product) {
                            a.loan = self.pos.loan
                        }
                    })
                })
            }
            console.log('POS')
            console.log(this.pos)
            console.log('POS.GUI')
            console.log(this.pos.gui)
            console.log('POS.GUI.CURRENT_SCREEN')
            console.log(this.pos.gui.pos.gui.current_screen)
            return json;
        }
    })
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