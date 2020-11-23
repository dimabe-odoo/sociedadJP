odoo.define('pos_discount.andes', function (require) {
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var QWeb = core.qweb;
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
    exports.Orderline = Backbone.Model.extend({
        initialize: function(attr,options){
            this.pos   = options.pos;
            this.order = options.order;
            if (options.json) {
                try {
                    this.init_from_JSON(options.json);
                } catch(error) {
                    console.error('ERROR: attempting to recover product ID', options.json.product_id,
                        'not available in the point of sale. Correct the product or clean the browser cache.');
                }
                return;
            }
            this.product = options.product;
            this.set_product_lot(this.product);
            this.set_quantity(1);
            this.discount = 0;
            this.discountStr = '0';
            this.selected = false;
            this.id = orderline_id++;
            this.price_manually_set = false;
    
            if (options.price) {
                this.set_unit_price(options.price);
            } else {
                this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
            }
        },
        init_from_JSON: function(json) {
            this.product = this.pos.db.get_product_by_id(json.product_id);
            this.set_product_lot(this.product);
            this.price = json.price_unit;
            this.set_discount(json.discount);
            this.set_quantity(json.qty, 'do not recompute unit price');
            this.id = json.id ? json.id : orderline_id++;
            orderline_id = Math.max(this.id+1,orderline_id);
            var pack_lot_lines = json.pack_lot_ids;
            for (var i = 0; i < pack_lot_lines.length; i++) {
                var packlotline = pack_lot_lines[i][2];
                var pack_lot_line = new exports.Packlotline({}, {'json': _.extend(packlotline, {'order_line':this})});
                this.pack_lot_lines.add(pack_lot_line);
            }
        },
        clone: function(){
            var orderline = new exports.Orderline({},{
                pos: this.pos,
                order: this.order,
                product: this.product,
                price: this.price,
            });
            orderline.order = null;
            orderline.quantity = this.quantity;
            orderline.quantityStr = this.quantityStr;
            orderline.discount = this.discount;
            orderline.price = this.price;
            orderline.selected = false;
            orderline.price_manually_set = this.price_manually_set;
            return orderline;
        },
        set_product_lot: function(product){
            this.has_product_lot = product.tracking !== 'none' && this.pos.config.use_existing_lots;
            this.pack_lot_lines  = this.has_product_lot && new PacklotlineCollection(null, {'order_line': this});
        },
        // sets a discount [0,100]%
        set_discount: function(discount){
            var disc = Math.min(Math.max(parseFloat(discount) || 0, 0),100);
            this.discount = disc;
            this.discountStr = '' + disc;
            this.trigger('change',this);
        },
        // returns the discount [0,100]%
        get_discount: function(){
            return this.discount;
        },
        get_discount_str: function(){
            return this.discountStr;
        },
        // sets the quantity of the product. The quantity will be rounded according to the
        // product's unity of measure properties. Quantities greater than zero will not get
        // rounded to zero
        set_quantity: function(quantity, keep_price){
            this.order.assert_editable();
            if(quantity === 'remove'){
                this.order.remove_orderline(this);
                return;
            }else{
                var quant = parseFloat(quantity) || 0;
                var unit = this.get_unit();
                if(unit){
                    if (unit.rounding) {
                        var decimals = this.pos.dp['Product Unit of Measure'];
                        var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                        this.quantity    = round_pr(quant, rounding);
                        this.quantityStr = field_utils.format.float(this.quantity, {digits: [69, decimals]});
                    } else {
                        this.quantity    = round_pr(quant, 1);
                        this.quantityStr = this.quantity.toFixed(0);
                    }
                }else{
                    this.quantity    = quant;
                    this.quantityStr = '' + this.quantity;
                }
            }
    
            // just like in sale.order changing the quantity will recompute the unit price
            if(! keep_price && ! this.price_manually_set){
                this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
                this.order.fix_tax_included_price(this);
            }
            this.trigger('change', this);
        },
        // return the quantity of product
        get_quantity: function(){
            return this.quantity;
        },
        get_quantity_str: function(){
            return this.quantityStr;
        },
        get_quantity_str_with_unit: function(){
            var unit = this.get_unit();
            if(unit && !unit.is_pos_groupable){
                return this.quantityStr + ' ' + unit.name;
            }else{
                return this.quantityStr;
            }
        },
    
        get_required_number_of_lots: function(){
            var lots_required = 1;
    
            if (this.product.tracking == 'serial') {
                lots_required = Math.abs(this.quantity);
            }
    
            return lots_required;
        },
    
        compute_lot_lines: function(){
            var pack_lot_lines = this.pack_lot_lines;
            var lines = pack_lot_lines.length;
            var lots_required = this.get_required_number_of_lots();
    
            if(lots_required > lines){
                for(var i=0; i<lots_required - lines; i++){
                    pack_lot_lines.add(new exports.Packlotline({}, {'order_line': this}));
                }
            }
            if(lots_required < lines){
                var to_remove = lines - lots_required;
                var lot_lines = pack_lot_lines.sortBy('lot_name').slice(0, to_remove);
                pack_lot_lines.remove(lot_lines);
            }
            return this.pack_lot_lines;
        },
    
        has_valid_product_lot: function(){
            if(!this.has_product_lot){
                return true;
            }
            var valid_product_lot = this.pack_lot_lines.get_valid_lots();
            return this.get_required_number_of_lots() === valid_product_lot.length;
        },
    
        // return the unit of measure of the product
        get_unit: function(){
            var unit_id = this.product.uom_id;
            if(!unit_id){
                return undefined;
            }
            unit_id = unit_id[0];
            if(!this.pos){
                return undefined;
            }
            return this.pos.units_by_id[unit_id];
        },
        // return the product of this orderline
        get_product: function(){
            return this.product;
        },
        // selects or deselects this orderline
        set_selected: function(selected){
            this.selected = selected;
            this.trigger('change',this);
        },
        // returns true if this orderline is selected
        is_selected: function(){
            return this.selected;
        },
        // when we add an new orderline we want to merge it with the last line to see reduce the number of items
        // in the orderline. This returns true if it makes sense to merge the two
        can_be_merged_with: function(orderline){
            var price = parseFloat(round_di(this.price || 0, this.pos.dp['Product Price']).toFixed(this.pos.dp['Product Price']));
            var order_line_price = orderline.get_product().get_price(orderline.order.pricelist, this.get_quantity());
            order_line_price = orderline.compute_fixed_price(order_line_price);
            if( this.get_product().id !== orderline.get_product().id){    //only orderline of the same product can be merged
                return false;
            }else if(!this.get_unit() || !this.get_unit().is_pos_groupable){
                return false;
            }else if(this.get_discount() > 0){             // we don't merge discounted orderlines
                return false;
            }else if(!utils.float_is_zero(price - order_line_price,
                        this.pos.currency.decimals)){
                return false;
            }else if(this.product.tracking == 'lot') {
                return false;
            }else{
                return true;
            }
        },
        merge: function(orderline){
            this.order.assert_editable();
            this.set_quantity(this.get_quantity() + orderline.get_quantity());
        },
        export_as_JSON: function() {
            var pack_lot_ids = [];
            if (this.has_product_lot){
                this.pack_lot_lines.each(_.bind( function(item) {
                    return pack_lot_ids.push([0, 0, item.export_as_JSON()]);
                }, this));
            }
            return {
                qty: this.get_quantity(),
                price_unit: this.get_unit_price(),
                price_subtotal: this.get_price_without_tax(),
                price_subtotal_incl: this.get_price_with_tax(),
                discount: this.get_discount(),
                product_id: this.get_product().id,
                price_display_one:  this.get_display_price_one(),
                price_display :     this.get_display_price(),
                tax_ids: [[6, false, _.map(this.get_applicable_taxes(), function(tax){ return tax.id; })]],
                id: this.id,
                pack_lot_ids: pack_lot_ids
            };
        },
        //used to create a json of the ticket, to be sent to the printer
        export_for_printing: function(){
            return {
                quantity:           this.get_quantity(),
                unit_name:          this.get_unit().name,
                price:              this.get_unit_display_price(),
                discount:           this.get_discount(),
                product_name:       this.get_product().display_name,
                product_name_wrapped: this.generate_wrapped_product_name(),
                price_lst:          this.get_lst_price(),
                display_discount_policy:    this.display_discount_policy(),
                price_display_one:  this.get_display_price_one(),
                price_display :     this.get_display_price(),
                price_with_tax :    this.get_price_with_tax(),
                price_without_tax:  this.get_price_without_tax(),
                price_with_tax_before_discount:  this.get_price_with_tax_before_discount(),
                tax:                this.get_tax(),
                product_description:      this.get_product().description,
                product_description_sale: this.get_product().description_sale,
            };
        },
        generate_wrapped_product_name: function() {
            var MAX_LENGTH = 24; // 40 * line ratio of .6
            var wrapped = [];
            var name = this.get_product().display_name;
            var current_line = "";
    
            while (name.length > 0) {
                var space_index = name.indexOf(" ");
    
                if (space_index === -1) {
                    space_index = name.length;
                }
    
                if (current_line.length + space_index > MAX_LENGTH) {
                    if (current_line.length) {
                        wrapped.push(current_line);
                    }
                    current_line = "";
                }
    
                current_line += name.slice(0, space_index + 1);
                name = name.slice(space_index + 1);
            }
    
            if (current_line.length) {
                wrapped.push(current_line);
            }
    
            return wrapped;
        },
        // changes the base price of the product for this orderline
        set_unit_price: function(price){
            this.order.assert_editable();
            this.price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
            this.trigger('change',this);
        },
        get_unit_price: function(){
            var digits = this.pos.dp['Product Price'];
            // round and truncate to mimic _symbol_set behavior
            return parseFloat(round_di(this.price || 0, digits).toFixed(digits));
        },
        get_unit_display_price: function(){
            if (this.pos.config.iface_tax_included === 'total') {
                var quantity = this.quantity;
                this.quantity = 1.0;
                var price = this.get_all_prices().priceWithTax;
                this.quantity = quantity;
                return price;
            } else {
                return this.get_unit_price();
            }
        },
        get_base_price:    function(){
            var rounding = this.pos.currency.rounding;
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
                return this.get_price_with_tax();
            } else {
                return this.get_base_price();
            }
        },
        get_price_without_tax: function(){
            return this.get_all_prices().priceWithoutTax;
        },
        get_price_with_tax: function(){
            return this.get_all_prices().priceWithTax;
        },
        get_price_with_tax_before_discount: function () {
            return this.get_all_prices().priceWithTaxBeforeDiscount;
        },
        get_tax: function(){
            return this.get_all_prices().tax;
        },
        get_applicable_taxes: function(){
            var i;
            // Shenaningans because we need
            // to keep the taxes ordering.
            var ptaxes_ids = this.get_product().taxes_id;
            var ptaxes_set = {};
            for (i = 0; i < ptaxes_ids.length; i++) {
                ptaxes_set[ptaxes_ids[i]] = true;
            }
            var taxes = [];
            for (i = 0; i < this.pos.taxes.length; i++) {
                if (ptaxes_set[this.pos.taxes[i].id]) {
                    taxes.push(this.pos.taxes[i]);
                }
            }
            return taxes;
        },
        get_tax_details: function(){
            return this.get_all_prices().taxDetails;
        },
        get_taxes: function(){
            var taxes_ids = this.get_product().taxes_id;
            var taxes = [];
            for (var i = 0; i < taxes_ids.length; i++) {
                taxes.push(this.pos.taxes_by_id[taxes_ids[i]]);
            }
            return taxes;
        },
        _map_tax_fiscal_position: function(tax) {
            var self = this;
            var current_order = this.pos.get_order();
            var order_fiscal_position = current_order && current_order.fiscal_position;
            var taxes = [];
    
            if (order_fiscal_position) {
                var tax_mappings = _.filter(order_fiscal_position.fiscal_position_taxes_by_id, function (fiscal_position_tax) {
                    return fiscal_position_tax.tax_src_id[0] === tax.id;
                });
    
                if (tax_mappings && tax_mappings.length) {
                    _.each(tax_mappings, function(tm) {
                        if (tm.tax_dest_id) {
                            taxes.push(self.pos.taxes_by_id[tm.tax_dest_id[0]]);
                        }
                    });
                } else{
                    taxes.push(tax);
                }
            } else {
                taxes.push(tax);
            }
    
            return taxes;
        },
        /**
         * Mirror JS method of:
         * _compute_amount in addons/account/models/account.py
         */
        _compute_all: function(tax, base_amount, quantity, price_exclude) {
            if(price_exclude === undefined)
                var price_include = tax.price_include;
            else
                var price_include = !price_exclude;
            if (tax.amount_type === 'fixed') {
                var sign_base_amount = Math.sign(base_amount) || 1;
                // Since base amount has been computed with quantity
                // we take the abs of quantity
                // Same logic as bb72dea98de4dae8f59e397f232a0636411d37ce
                return tax.amount * sign_base_amount * Math.abs(quantity);
            }
            if (tax.amount_type === 'percent' && !price_include){
                return base_amount * tax.amount / 100;
            }
            if (tax.amount_type === 'percent' && price_include){
                return base_amount - (base_amount / (1 + tax.amount / 100));
            }
            if (tax.amount_type === 'division' && !price_include) {
                return base_amount / (1 - tax.amount / 100) - base_amount;
            }
            if (tax.amount_type === 'division' && price_include) {
                return base_amount - (base_amount * (tax.amount / 100));
            }
            return false;
        },
        /**
         * Mirror JS method of:
         * compute_all in addons/account/models/account.py
         *
         * Read comments in the python side method for more details about each sub-methods.
         */
        compute_all: function(taxes, price_unit, quantity, currency_rounding, handle_price_include=true) {
            var self = this;
    
            // 1) Flatten the taxes.
    
            var _collect_taxes = function(taxes, all_taxes){
                taxes.sort(function (tax1, tax2) {
                    return tax1.sequence - tax2.sequence;
                });
                _(taxes).each(function(tax){
                    if(tax.amount_type === 'group')
                        all_taxes = _collect_taxes(tax.children_tax_ids, all_taxes);
                    else
                        all_taxes.push(tax);
                });
                return all_taxes;
            }
            var collect_taxes = function(taxes){
                return _collect_taxes(taxes, []);
            }
    
            taxes = collect_taxes(taxes);
    
            // 2) Avoid dealing with taxes mixing price_include=False && include_base_amount=True
            // with price_include=True
    
            var base_excluded_flag = false; // price_include=False && include_base_amount=True
            var included_flag = false;      // price_include=True
            _(taxes).each(function(tax){
                if(tax.price_include)
                    included_flag = true;
                else if(tax.include_base_amount)
                    base_excluded_flag = true;
                if(base_excluded_flag && included_flag)
                    throw new Error('Unable to mix any taxes being price included with taxes affecting the base amount but not included in price.');
            });
    
            // 3) Deal with the rounding methods
    
            var round_tax = this.pos.company.tax_calculation_rounding_method != 'round_globally';
    
            var initial_currency_rounding = currency_rounding;
            if(!round_tax)
                currency_rounding = currency_rounding * 0.00001;
    
            // 4) Iterate the taxes in the reversed sequence order to retrieve the initial base of the computation.
            var recompute_base = function(base_amount, fixed_amount, percent_amount, division_amount){
                 return (base_amount - fixed_amount) / (1.0 + percent_amount / 100.0) * (100 - division_amount) / 100;
            }
    
            var base = round_pr(price_unit * quantity, initial_currency_rounding);
    
            var sign = 1;
            if(base < 0){
                base = -base;
                sign = -1;
            }
    
            var total_included_checkpoints = {};
            var i = taxes.length - 1;
            var store_included_tax_total = true;
    
            var incl_fixed_amount = 0.0;
            var incl_percent_amount = 0.0;
            var incl_division_amount = 0.0;
    
            var cached_tax_amounts = {};
            if (handle_price_include){
                _(taxes.reverse()).each(function(tax){
                    if(tax.include_base_amount){
                        base = recompute_base(base, incl_fixed_amount, incl_percent_amount, incl_division_amount);
                        incl_fixed_amount = 0.0;
                        incl_percent_amount = 0.0;
                        incl_division_amount = 0.0;
                        store_included_tax_total = true;
                    }
                    if(tax.price_include){
                        if(tax.amount_type === 'percent')
                            incl_percent_amount += tax.amount;
                        else if(tax.amount_type === 'division')
                            incl_division_amount += tax.amount;
                        else if(tax.amount_type === 'fixed')
                            incl_fixed_amount += quantity * tax.amount
                        else{
                            var tax_amount = self._compute_all(tax, base, quantity);
                            incl_fixed_amount += tax_amount;
                            cached_tax_amounts[i] = tax_amount;
                        }
                        if(store_included_tax_total){
                            total_included_checkpoints[i] = base;
                            store_included_tax_total = false;
                        }
                    }
                    i -= 1;
                });
            }
    
            var total_excluded = round_pr(recompute_base(base, incl_fixed_amount, incl_percent_amount, incl_division_amount), initial_currency_rounding);
            var total_included = total_excluded;
    
            // 5) Iterate the taxes in the sequence order to fill missing base/amount values.
    
            base = total_excluded;
    
            var taxes_vals = [];
            i = 0;
            var cumulated_tax_included_amount = 0;
            _(taxes.reverse()).each(function(tax){
                if(tax.price_include && total_included_checkpoints[i] !== undefined){
                    var tax_amount = total_included_checkpoints[i] - (base + cumulated_tax_included_amount);
                    cumulated_tax_included_amount = 0;
                }else
                    var tax_amount = self._compute_all(tax, base, quantity, true);
    
                tax_amount = round_pr(tax_amount, currency_rounding);
    
                if(tax.price_include && total_included_checkpoints[i] === undefined)
                    cumulated_tax_included_amount += tax_amount;
    
                taxes_vals.push({
                    'id': tax.id,
                    'name': tax.name,
                    'amount': sign * tax_amount,
                    'base': sign * round_pr(base, currency_rounding),
                });
    
                if(tax.include_base_amount)
                    base += tax_amount;
    
                total_included += tax_amount;
                i += 1;
            });
    
            return {
                'taxes': taxes_vals,
                'total_excluded': sign * round_pr(total_excluded, this.pos.currency.rounding),
                'total_included': sign * round_pr(total_included, this.pos.currency.rounding),
            }
        },
        get_all_prices: function(){
            var self = this;
    
            var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
            var taxtotal = 0;
    
            var product =  this.get_product();
            var taxes_ids = product.taxes_id;
            var taxes =  this.pos.taxes;
            var taxdetail = {};
            var product_taxes = [];
    
            _(taxes_ids).each(function(el){
                var tax = _.detect(taxes, function(t){
                    return t.id === el;
                });
                product_taxes.push.apply(product_taxes, self._map_tax_fiscal_position(tax));
            });
            product_taxes = _.uniq(product_taxes, function(tax) { return tax.id; });
    
            var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
            var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), this.get_quantity(), this.pos.currency.rounding);
            _(all_taxes.taxes).each(function(tax) {
                taxtotal += tax.amount;
                taxdetail[tax.id] = tax.amount;
            });
    
            return {
                "priceWithTax": all_taxes.total_included,
                "priceWithoutTax": all_taxes.total_excluded,
                "priceSumTaxVoid": all_taxes.total_void,
                "priceWithTaxBeforeDiscount": all_taxes_before_discount.total_included,
                "tax": taxtotal,
                "taxDetails": taxdetail,
            };
        },
        display_discount_policy: function(){
            return this.order.pricelist.discount_policy;
        },
        compute_fixed_price: function (price) {
            var order = this.order;
            if(order.fiscal_position) {
                var taxes = this.get_taxes();
                var mapped_included_taxes = [];
                var new_included_taxes = [];
                var self = this;
                _(taxes).each(function(tax) {
                    var line_taxes = self._map_tax_fiscal_position(tax);
                    if (line_taxes.length && line_taxes[0].price_include){
                        new_included_taxes = new_included_taxes.concat(line_taxes);
                    }
                    if(tax.price_include && !_.contains(line_taxes, tax)){
                        mapped_included_taxes.push(tax);
                    }
                });
    
                if (mapped_included_taxes.length > 0) {
                    if (new_included_taxes.length > 0) {
                        var price_without_taxes = this.compute_all(mapped_included_taxes, price, 1, order.pos.currency.rounding, true).total_excluded
                        return this.compute_all(new_included_taxes, price_without_taxes, 1, order.pos.currency.rounding, false).total_included
                    }
                    else{
                        return this.compute_all(mapped_included_taxes, price, 1, order.pos.currency.rounding, true).total_excluded;
                    }
                }
            }
            return price;
        },
        get_fixed_lst_price: function(){
            return this.compute_fixed_price(this.get_lst_price());
        },
        get_lst_price: function(){
            return this.product.lst_price;
        },
        set_lst_price: function(price){
          this.order.assert_editable();
          this.product.lst_price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
          this.trigger('change',this);
        },
    });
    
    v
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
                                            var orderlines = order.get_orderlines();
                                            order.selected_orderline.price = order.selected_orderline.price - price;
                                            order.selected_orderline.product.taxes_id = []
                                            console.log(order.selected_orderline)
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