# -*- coding: utf-8 -*-
##############################################################################
#
#    Ingenieria ADHOC - ADHOC SA
#    https://launchpad.net/~ingenieria-adhoc
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
    'application': True,
    'author': 'Ingenieria ADHOC.',
    'category': u'base.module_category_knowledge_management',
    'demo_xml': [],
    'depends': [u'logistic_x', 
        'product_customer_price',
        'disable_openerp_online',
        'purchase_double_validation_imp',
        'cron_run_manually',
        'partner_person',
        'logistic_reports',
        ],
    'description': u"""
AFTER INSTALLATION CONFIGURATIONS:
* Set purchase ammount to 0
* Enable supplier pricelist on products
* Config person data
Necesita los repo:
    lp:server-env-tools    
""",
    'init_xml': [],
    'installable': True,
    'license': 'AGPL-3',
    'name': u'Logistic Project',
    'test': [],
    'update_xml': [
      ],
    'version': 'No version',
    'website': 'www.ingadhoc.com'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
