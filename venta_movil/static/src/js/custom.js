odoo.define('pos.custom_button', function (require) {
    'use strict';
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var module = require('point_of_sale.models');
    var _super_order = module.Order.prototype;
    var CustomButton = screens.ActionButtonWidget.extend({
        template: 'CustomButton',

        button_click: function () {
            var self = this;
            self.gui.show_popup('number', {
                'title': 'Prestamo',
                'confirm': function () {
                    var value = this.$('.active');
                    var data = _super_order.export_as_JSON.apply(this,arguments);
                    data.loan_supply = value[0].innerHTML;
                    console.log(data)
                    return data;
                },
                'body': '¿Esta seguro de realizar un prestamo?'
            })
        },
    });
    screens.define_action_button({
        'name': 'custom_button',
        'widget': CustomButton
    })
});