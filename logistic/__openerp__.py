# -*- coding: utf-8 -*-
##############################################################################
#
#    Logistic
#    Copyright (C) 2014 No author.
#    No email
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


{   'active': False,
    'author': 'No author.',
    'category': u'base.module_category_knowledge_management',
    'demo_xml': [],
    'depends': [   u'purchase',
                   u'account',
                   u'product',
                   u'sale',
                   u'fleet',
                   u'mail'],
    'description': u'Logistic',
    'init_xml': [],
    'installable': True,
    'license': 'AGPL-3',
    'name': u'Logistic',
    'test': [],
    'update_xml': [   u'security/logistic_group.xml',
                      u'view/product_view.xml',
                      u'view/waybill_expense_view.xml',
                      u'view/waybill_view.xml',
                      u'view/travel_view.xml',
                      u'view/requirement_view.xml',
                      u'view/waybill_driver_payment_view.xml',
                      u'view/location_view.xml',
                      u'view/vehicle_view.xml',
                      u'view/partner_view.xml',
                      u'view/logistic_menuitem.xml',
                      u'data/product_properties.xml',
                      u'data/waybill_expense_properties.xml',
                      u'data/waybill_properties.xml',
                      u'data/travel_properties.xml',
                      u'data/requirement_properties.xml',
                      u'data/waybill_driver_payment_properties.xml',
                      u'data/location_properties.xml',
                      u'data/vehicle_properties.xml',
                      u'data/partner_properties.xml',
                      u'data/product_track.xml',
                      u'data/waybill_expense_track.xml',
                      u'data/waybill_track.xml',
                      u'data/travel_track.xml',
                      u'data/requirement_track.xml',
                      u'data/waybill_driver_payment_track.xml',
                      u'data/location_track.xml',
                      u'data/vehicle_track.xml',
                      u'data/partner_track.xml',
                      u'workflow/waybill_workflow.xml',
                      u'workflow/requirement_workflow.xml',
                      u'workflow/waybill_driver_payment_workflow.xml',
                      'security/ir.model.access.csv'],
    'version': 'No version',
    'website': ''}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
