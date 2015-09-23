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


{'active': False,
    'application': True,
    'author': 'ADHOC S.A',
    'category': 'base.module_category_knowledge_management',
    'demo': [],
    'depends': [
        'logistic',
        'product_customer_price',
        'disable_openerp_online',
        # 'purchase_double_validation_imp',
        'cron_run_manually',
        'partner_person',
        'logistic_reports',
    ],
    'description': """
AFTER INSTALLATION CONFIGURATIONS:
* Set purchase ammount to 0
* Enable supplier pricelist on products
* Config person data
Necesita los repo:
    lp:server-env-tools    
""",
    'installable': True,
    'license': 'AGPL-3',
    'name': 'Logistic Project',
    'test': [],
    'data': [
    ],
    'version': '8.0.0.0.0',
    'website': 'www.adhoc.com.ar'}
