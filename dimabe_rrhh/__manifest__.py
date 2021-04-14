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
        'data/custom_data_afp.xml',
        'data/custom_data_ccaf.xml',
        'data/custom_data_hr_payslip.xml',
        'data/custom_data_mutuality.xml',
        'data/custom_data_contract_type.xml',
        'data/custom_data_section.xml',
        'data/custom_employee_type.xml',
        'data/custom_isapre.xml',
        'data/hr_payslip_input_type.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/custom_data.xml',
        'views/custom_benefits_rrhh.xml',
        'views/custom_indicators.xml',
        'views/hr_contract.xml',
        'views/hr_salary_rule.xml',
        'views/hr_payslip.xml',
        'views/wizard_hr_payslip.xml',
        'views/hr_department.xml',
        'views/hr_employee.xml',
        'report/report_payslip.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
