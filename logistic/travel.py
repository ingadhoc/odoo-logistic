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

class travel(osv.osv):
    """"""
    
    _name = 'logistic.travel'
    _description = 'travel'

    _columns = {
        'from_date': fields.datetime(string='From', required=True),
        'location_from_id': fields.many2one('logistic.location', string='Location From', required=True),
        'to_date': fields.datetime(string='To', required=True),
        'location_to_id': fields.many2one('logistic.location', string='Location To', required=True),
        'reference': fields.char(string='Reference'),
        'partner_id': fields.many2one('res.partner', string='Customer', domain=[('customer','=',True)]),
        'product_id': fields.many2one('product.product', string='Product', context={'default_type':'service','default_service_subtype':'travel'}, domain=[('type','=','service'),('service_subtype','=','travel')]),
        'price': fields.float(string='Price'),
        'invoice_line_id': fields.many2one('account.invoice.line', string='Invoice Line', readonly=True),
        'waybill_id': fields.many2one('logistic.waybill', string='Waybill', required=True, ondelete='cascade'), 
    }

    _defaults = {
        'from_date': fields.datetime.now,
    }


    _constraints = [
    ]


    def on_change_location(self, cr, uid, ids, location_from_id, location_to_id, context=None):
        """"""
        raise NotImplementedError

    def on_change_product(self, cr, uid, ids, product_id, partner_id, context=None):
        """"""
        raise NotImplementedError



travel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
