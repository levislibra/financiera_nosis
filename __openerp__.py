# -*- coding: utf-8 -*-
{
    'name': "Financiera Nosis",

    'summary': """
        Integracion con buro de infromes Nosis. Para evaluacion y
        automatizaion de riesgo crediticio en le aceptacion de clientes.""",

    'description': """
        Integracion con buro Nosis.
    """,

    'author': "Librasoft",
    'website': "https://libra-soft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Financie',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'financiera_prestamos'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/extends_res_company.xml',
        'views/nosis_configuracion.xml',
        'views/nosis_informe.xml',
				'views/nosis_cda.xml',
				'views/extends_res_partner.xml',
				'views/nosis_cuestionario.xml',
				'wizards/nosis_pregunta_wizard.xml',
				'data/ir_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}