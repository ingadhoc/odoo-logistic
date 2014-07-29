# -*- coding: utf-8 -*-
from openerp import netsvc
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_cancel(self, cr, uid, ids, context=None):
        invoice_line_obj = self.pool['account.invoice.line']
        invoice_line_ids = invoice_line_obj.search(cr, uid, [('invoice_id','in',ids)], context=context)
        travel_obj = self.pool['logistic.travel']
        travel_ids = travel_obj.search(cr, uid, [('invoice_line_id','in',invoice_line_ids)], context=context)
        travel_obj.write(cr, uid, travel_ids, {'invoice_line_id':False}, context=context)
        return super(account_invoice,self).action_cancel(cr, uid, ids, context=context)        