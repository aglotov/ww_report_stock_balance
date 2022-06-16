# -*- coding: utf-8 -*-
#################################################################################
# Author      : White Wind Ltd. (<https://wwind.ua/>)
# Copyright(c): 2022-White Wind Ltd.
# All Rights Reserved.
#################################################################################
{
    'name': "Report Stock Balance Sheet",
    'summary': "Stock balance sheet helps to analyze balance and moves by products and locations",

    'description': "",

    'author': "White Wind Ltd.",
    'website': "https://wwind.ua",
    'license': 'AGPL-3',

    'category': "Inventory",
    'version': '14.0.1.0.0',

    'depends': ['stock'],

    'data': [
        'views/product_product_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
}
