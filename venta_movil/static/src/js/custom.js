odoo.define('pos.custom_button', function (require) {
'use strict';
    var screens = require('point_of_sale.screens');

    var PopUpButton = screens.ActionButtonWidget.extend({
        template : 'CustomButton',
        button_click : function(){
            this.gui.show_popup('confirm',{
                'title':'Prestamo',
                'body':'¿Esta Seguro debe que quiere realizar el prestamo?'
            });

        }
    })
    screens.define_action_button({
        'name':'popup_button',
        'widget':PopUpButton,
        'condition':function(){
            return this.pos.config.popup_button;
        },
    });
    return PopUpButton;
});