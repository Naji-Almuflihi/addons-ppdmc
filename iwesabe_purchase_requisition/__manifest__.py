# -*- coding: utf-8 -*-
{

    'name': 'Purchase Requisition Extend',
    'version': '14.0.1.0',
    'category': 'Purchases',
    'license': 'AGPL-3',
    'author': 'iWesabe',
    'website': 'https://www.iwesabe.com',
    'summary': 'Purchase Requisition Extend',
    'description' : ''' Purchase Requisition Extend ''',
    'depends': ['purchase_requisition','purchase_stock','purchase','purchase_requisition_stock'],
    'data': [
            # 'security/ir.model.access.csv',
            'data/purchase_requisition_data.xml',
            'views/purchase_requisition_view.xml',
            'views/purchase_view.xml',
            'views/stock.xml',
             ],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
