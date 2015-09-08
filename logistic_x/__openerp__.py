# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{'active': False,
    'author': 'ADHOC.',
    'category': 'base.module_category_knowledge_management',
    'demo_xml': [
        'data/demo/res.partner.csv',
        'data/demo/logistic.location.csv',
        'data/demo/product.product.csv',
        'data/demo/fleet.vehicle.csv',
        'data/demo/logistic.waybill.csv',
        'data/demo/logistic.travel.csv',
        # 'data/demo/product.supplierinfo.csv',
        'data/demo/documents/logistic.requirement.csv',
        'data/demo/maintenances/logistic.requirement.csv',
        'data/demo/logistic.requirement.xml',
    ],
    'depends': ['logistic'],
    'description': """
Logistic Modifications
""",
    'init_xml': [],
    'installable': True,
    'license': 'AGPL-3',
    'name': 'Logistic Modifications',
    'test': [],
    'update_xml': [
        # 'wizard/travel_sale_order.xml',
        'wizard/travel_make_invoice.xml',
        'wizard/expense_make_invoice.xml',
        'view/partner_view.xml',
        'view/waybill_view.xml',
        'view/product_view.xml',
        'view/travel_view.xml',
        'view/waybill_expense_view.xml',
        'view/fleet_view.xml',
        'view/requirement_view.xml',
        'view/purchase_order.xml',
        'view/waybill_driver_payment_view.xml',
        'data/waybill_sequence.xml',
        'data/cron.xml',
        'workflow/waybill_workflow.xml',
        'workflow/requirement_workflow.xml',
        'security/logistic_group.xml',
        'security/ir.model.access.csv',
    ],
    'version': 'No version',
    'css': [
        'static/src/css/logistic.css',
    ],
    'website': 'www.adhoc.com.ar'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
