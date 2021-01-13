# -*- coding: utf-8 -*-
{
    'name': "RRHH",

    'summary': """
        Funcionalidades de RRHH adaptados a la ley chilena 
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Dimabe Ltda",
    'website': "http://www.dimabe.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll'],

    # always loaded
    'data': [
        'data/custom_data_demo.xml',
        'data/custom_data_apv.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/custom_data.xml',
        'views/custom_benefits_rrhh.xml',
        'views/custom_indicators.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
