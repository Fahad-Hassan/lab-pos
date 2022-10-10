# -*- coding: utf-8 -*-
{
    'name': 'Medical Lims POS',
    'summary': """
            From the registration of patients and their samples to 
            the sending of the analysis report.
                """,
    'description': """Manarerergement bkbkhossssfjbjb adfdfdf medical laboratory """,
    'version': '14.0.1.0',
    'sequence':15,
    'website': "",
    'category': 'Extra Tools',
    'author' : 'Oussama Sekkak',
    'maintainter' : 'Oussama Sekkak',

    'depends': [
        'lims',
        'point_of_sale'
    ],
    'data': [
        # 'security/lims_security.xml',
        # 'security/ir.model.access.csv',
        # 'views/product_views.xml',
        'views/lims_views.xml',
        'views/template.xml',
        # # 'views/menus.xml',
        # # 'views/res_config_settings_view.xml',
    ],
    'demo': [],
    'qweb': [
    'static/src/xml/Screens/ClientListScreen/pos.xml',
    ],
    'web.assets_backend': [
        'lims_pos/static/src/js/js.js',
    ],
    'images':['static/description/banner.gif'],
    'auto_install': False,
    'application':True,
    'installable':True,
    'license': 'OPL-1',
}
