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

class waybill_expense(osv.osv):
    """"""
    
    _name = 'logistic.waybill_expense'
    _description = 'waybill_expense'

    _columns = {
        'supplier_id': fields.many2one('res.partner', string='Supplier', context={'default_supplier':True,'default_customer':False}, domain=[('supplier','=',True)]),
        'product_id': fields.many2one('product.product', string='Product', required=True, context={'default_purchase_ok':True}, domain=[('purchase_ok','=',True)]),
        'price_unit': fields.float(string='Price Unit', required=True),
        'product_uom_qty': fields.float(string='Quantity', required=True),
        'price_subtotal': fields.float(string='Subtotal', readonly=True, required=True),
        'invoice_state': fields.boolean(string='Do not Invoice'),
        'note': fields.text(string='Note'),
        'invoice_line_id': fields.many2one('account.invoice.line', string='Invoice Line', readonly=True),
        'waybill_id': fields.many2one('logistic.waybill', string='Waybill', required=True, ondelete='cascade'), 
    }

    _defaults = {
        'product_uom_qty': 1.0,
    }


    _constraints = [
    ]




waybill_expense()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
