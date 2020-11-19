odoo.define('pos_discount.andes', function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    screens.ProductListWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent,options);
            this.model = options.model;
            this.productwidgets = [];
            this.weight = options.weight || 0;
            this.show_scale = options.show_scale || false;
            this.next_screen = options.next_screen || false;
            this.search_word = false;
    
            this.click_product_handler = function(){
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                options.click_product_action(product);
            };
    
            this.keypress_product_handler = function(ev){
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
            console.log(this.product_list)
            this.pos.get('orders').bind('add remove change', function () {
                self.renderElement();
            }, this);
    
            this.pos.bind('change:selectedOrder', function () {
                this.renderElement();
            }, this);
        },
        set_product_list: function(product_list, search_word){
            this.product_list = product_list;
            this.search_word = !!search_word ? search_word : false;
            this.renderElement();
        },
        get_product_image_url: function(product){
            return window.location.origin + '/web/image?model=product.product&field=image_128&id='+product.id;
        },
        replace: function($target){
            this.renderElement();
            var target = $target[0];
            target.parentNode.replaceChild(this.el,target);
        },
        calculate_cache_key: function(product, pricelist){
            return product.id + ',' + pricelist.id;
        },
        _get_active_pricelist: function(){
            var current_order = this.pos.get_order();
            var current_pricelist = this.pos.default_pricelist;
    
            if (current_order) {
                current_pricelist = current_order.pricelist;
            }
    
            return current_pricelist;
        },
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
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(cache_key,product_node);
                return product_node;
            }
            return cached;
        },
    
        renderElement: function() {
            var el_str  = QWeb.render(this.template, {widget: this});
            var el_node = document.createElement('div');
                el_node.innerHTML = el_str;
                el_node = el_node.childNodes[1];
    
            if(this.el && this.el.parentNode){
                this.el.parentNode.replaceChild(el_node,this.el);
            }
            this.el = el_node;
    
            var list_container = el_node.querySelector('.product-list');
            for(var i = 0, len = this.product_list.length; i < len; i++){
                var product_node = this.render_product(this.product_list[i]);
                product_node.addEventListener('click',this.click_product_handler);
                product_node.addEventListener('keypress',this.keypress_product_handler);
                list_container.appendChild(product_node);
            }
        },
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