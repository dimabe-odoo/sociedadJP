odoo.define('pos_popup_button',function(require){
    'use_strict';
    var screens = require('point_of_sale.screens');
    var PopupButton = screens.ActionButtonWidget.extend({
        template : 'PopupButton',
        button_click : function() {
            this.gui.show_popup('confirm',{
                'title': 'PopUp',
                'body':'Opening popup after clicking on the button',
            });
        }
    });
    screens.define_action_button({
        'name':'popup_button',
        'widget':PopupButton,
        'condition': function(){
            return this.pos.config.popup_button;
        },
    });
    return PopupButton
});