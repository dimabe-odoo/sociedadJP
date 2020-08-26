odoo.define('pos.custom_button', function (require) {
'use strict';
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');

    var CustomButton = screens.ActionButtonWidget.extend({
        template : 'CustomButton',

        button_click : function(){
            var self = this;
            self.custom_function();
        },
        custom_function : function(){
            var self = this;
            console.log(self)
        }
    });
    screens.define_action_button({
        'name':'custom_button',
        'widget':CustomButton
    })
});