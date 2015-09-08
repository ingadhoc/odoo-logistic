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


import re
from openerp import netsvc
from openerp.osv import osv, fields

class product(osv.osv):
    """"""
    
    _name = 'product.product'
    _inherits = {  }
    _inherit = [ 'product.product' ]

    _columns = {
        'location_from_id': fields.many2one('logistic.location', string='Location From'),
        'location_to_id': fields.many2one('logistic.location', string='Location To'),
        'service_subtype': fields.selection([(u'travel', u'Travel'), (u'maintenance', u'Maintenance'), (u'document', u'Document'), (u'other', u'Other')], string='Subtype'),
        'default_range': fields.float(string='Default Range'),
        'range_unit': fields.selection([(u'kilometers', u'Kilometers'), (u'miles', u'Miles')], string='Range Unit'),
        'default_validity_days': fields.integer(string='Default Validity Days'),
        'default_warning_days': fields.integer(string='Default Warning Days'),
        'default_warning_range': fields.float(string='Default Warning Range'),
        'is_fuel': fields.boolean(string='Is Fuel?'),
    }

    _defaults = {
        'service_subtype': 'other',
        'range_unit': 'kilometers',
    }


    _constraints = [
    ]




product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
