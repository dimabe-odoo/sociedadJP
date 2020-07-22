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
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/jp_commune.xml',
        'views/res_partner.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}