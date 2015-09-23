# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import models, fields


class logistic_travel_make_invoice(models.TransientModel):
    _name = "logistic.travel.make.invoice"
    _description = "Travel Make Invoice"

    grouped = fields.Boolean(
        'Group the invoices',
        help='Check the box to group the invoices for the same customers',
        default=False)
    grouped_line = fields.Boolean('Group the Invoice Lines')
    invoice_date = fields.Date(
        'Invoice Date',
        default=fields.date.today())

    def make_invoices(self, cr, uid, ids, context=None):
        travel_obj = self.pool.get('logistic.travel')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        context['grouped_line'] = data['grouped_line']

        invoice_ids = travel_obj.action_invoice_create(cr, uid, context.get(
            ('active_ids'), []), data['grouped'], date_invoice=data['invoice_date'], context=context)
        result = mod_obj.get_object_reference(
            cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        if invoice_ids:
            result['domain'] = "[('id','in'," + str(invoice_ids) + " )]"

        return result
