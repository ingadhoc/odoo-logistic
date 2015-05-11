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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc

class logistic_expense_make_invoice(osv.osv_memory):
    _name = "logistic.expense.make.invoice"
    _description = "Expense Make Invoice"
    _columns = {
        'grouped': fields.boolean('Group the invoices', help='Check the box to group the invoices for the same suppliers'),
        'invoice_date': fields.date('Invoice Date'),
        'grouped_line': fields.boolean('Group the Invoice Lines')
    }
    _defaults = {
        'grouped': False,
        'invoice_date': fields.date.context_today,
    }


    def make_invoices(self, cr, uid, ids, context=None):
        waybill_expense_obj = self.pool.get('logistic.waybill_expense')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        context['grouped_line'] = data['grouped_line']

        invoice_ids = waybill_expense_obj.action_invoice_create(cr, uid, context.get(
            ('active_ids'), []), data['grouped'], date_invoice=data['invoice_date'], context=context)
        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        if invoice_ids:
            result['domain'] = "[('id','in',"+ str(invoice_ids) + " )]"

        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
