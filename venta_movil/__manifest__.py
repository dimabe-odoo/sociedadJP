# -*- coding: utf-8 -*-
{
    'name': "Venta Móvil JP",

    'summary': """
        Aplicación de venta móvil 
        
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Dimabe Ltda",
    'website': "http://www.dimabe.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','sale','point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/jp_commune.xml',
        'views/res_partner.xml',
        'views/product_product.xml',
        'views/templates.xml',
        'views/stock_picking.xml',
        'views/sale_order.xml',
        'views/stock_location.xml',
        'views/stock_warehouse.xml',
        'views/purchase_order.xml',
        'views/pos_order.xml',
        'views/mobile_sale_order.xml',
        'views/truck_session.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb':[
        'static/src/xml/pos_discount.xml'
    ]
}