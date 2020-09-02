odoo.define('pos_popup_button', function (require) {
    'use_strict';
    var screens = require('point_of_sale.screens');
    var PopupButton = screens.ActionButtonWidget.extend({
        template: 'CustomButton',
        button_click: function () {
            this.gui.show_popup('confirm', {
                'title': 'Prestamo',
                'body': '¿Esta seguro de realizar el prestamo?',
            });
        }
    });
    screens.define_action_button({
        'name': 'popup_button',
        'widget': PopupButton,
        'condition': function () {
            return this.pos.config.popup_button;
        },
    });
    return PopupButton;
});