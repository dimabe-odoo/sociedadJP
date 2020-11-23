odoo.define('pos_discount.andes', function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    screens.ProductListWidget.extend({
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
            this.model = options.model;
            this.productwidgets = [];
            this.weight = options.weight || 0;
            this.show_scale = options.show_scale || false;
            this.next_screen = options.next_screen || false;
            this.search_word = false;

            this.click_product_handler = function () {
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                options.click_product_action(product);
            };

            this.keypress_product_handler = function (ev) {
                // React only to SPACE to avoid interfering with warcode scanner which sends ENTER
                if (ev.which != 32) {
                    return;
                }
                ev.preventDefault();
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                options.click_product_action(product);
            };

            this.product_list = options.product_list || [];
            this.product_cache = new DomCache();

            this.pos.get('orders').bind('add remove change', function () {
                self.renderElement();
            }, this);

            this.pos.bind('change:selectedOrder', function () {
                this.renderElement();
            }, this);
        },
    });
    var _super_order = models.Order.prototype;
    var loan = 0
    models.OrderLine = models.Orderline.extend({
        get_base_price:    function(){
            var rounding = this.pos.currency.rounding;
            console.log(rounding)
            return round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount()/100), rounding);

        },
        get_display_price_one: function(){
            var rounding = this.pos.currency.rounding;
            var price_unit = this.get_unit_price();
            if (this.pos.config.iface_tax_included !== 'total') {
                return round_pr(price_unit * (1.0 - (this.get_discount() / 100.0)), rounding);
            } else {
                var product =  this.get_product();
                var taxes_ids = product.taxes_id;
                var taxes =  this.pos.taxes;
                var product_taxes = [];
                console.log(product)
                _(taxes_ids).each(function(el){
                    product_taxes.push(_.detect(taxes, function(t){
                        return t.id === el;
                    }));
                });
    
                var all_taxes = this.compute_all(product_taxes, price_unit, 1, this.pos.currency.rounding);
    
                return round_pr(all_taxes.total_included * (1 - this.get_discount()/100), rounding);
            }
        },
        get_display_price: function(){
            if (this.pos.config.iface_tax_included === 'total') {
                console.log(this)
                return this.get_price_with_tax();
            } else {
                console.log
                return this.get_base_price();
            }
        },
    }),
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
            if (this.pos.gui.pos.gui.current_screen) {
                var order = this.pos.get_order()
                if(order){
                    this.pos.gui.pos.gui.current_screen.product_list_widget.product_list.forEach(element => {
                        if (order.selected_orderline) {
                            if (order.selected_orderline.product.id == element.id) {
                                if (order.pricelist) {
                                    var price = 0
                                    
                                    order.pricelist.items.forEach(item => {
                                        if (item.product_tmpl_id[0] == element.id) {
                                            var price = ((19 / 100) * parseFloat(item.price.split(' ')[0].split(".")[0]))
                                            console.log(order.selected_orderline)
                                            order.selected_orderline.price = order.selected_orderline.price - price
                                        }
                                    })
                                    // var price = order.pricelist.items.filter(function (product) {
                                    //     return product[1].id == element.id;
                                    // }).fixed_price
                                   
                                }
                            }
                        }
                    });
                }
                }
                
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