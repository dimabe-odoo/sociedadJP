odoo.define('pos.custom_button', function (require) {
'use strict';
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    var CustomButton = screens.ActionButtonWidget.extend({
        template : 'CustomButton',

        button_click : function(){
            var self = this;
            self.custom_function();
        },
        custom_function : function(){
            var self = this;
            models.load_fields('pos.session', ['supply_id']);
            var check = document.getElementById('loan_qty');
            console.log(models)
        },
        action_data: function(){
            var self = this;
            rpc.query({
                model:'pos.order',
                method:'test',
                args : [[user],{'id':2}]
            }).then(function(e){
                console.log('hola')
            })
        }
    });
    screens.define_action_button({
        'name':'custom_button',
        'widget':CustomButton
    })
});