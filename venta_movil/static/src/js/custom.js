odoo.define('pos.custom_button', function (require) {
'use strict';
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var sessiong = require('point_of_sale.session')
    var models = require('point_of_sale.models');
    var CustomButton = screens.ActionButtonWidget.extend({
        template : 'CustomButton',

        button_click : function(){
            var self = this;
            self.custom_function();
        },
        custom_function : function(){
            var self = this;
            var models_test = require('point_of_sale.models')
            var check = document.getElementById('loan_qty');
            this.action_data()
        },
        action_data: function(){
            var self = this;
            var user = session.uid;
            rpc.query({
                model:'pos.order',
                method:'test',
                args : [[user],{'id':user}]
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