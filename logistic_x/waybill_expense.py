# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import models, fields, api, _
import time
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp


class waybill_expense(models.Model):

    """"""

    _inherit = 'logistic.waybill_expense'

    @api.one
    @api.depends('price_unit', 'product_uom_qty')
    def _amount_line(self):
        # tax_obj = self.pool.get('account.tax')
        # cur_obj = self.pool.get('res.currency')
        self.price_subtotal = self.price_unit * self.product_uom_qty
        # taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
        # cur = line.order_id.pricelist_id.currency_id
        # res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])

    price_subtotal = fields.Float(
        compute='_amount_line',
        string='Subtotal', digits_compute=dp.get_precision('Account'))
    date = fields.Date(
        related='waybill_id.date',  string='Date', store=True)

    def action_invoice_create(self, cr, uid, ids, grouped=False, date_invoice=False, context=None):
        invoice_ids = []
        partner_currency = {}

        if context is None:
            context = {}
        # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context['date_invoice'] = date_invoice

        for o in self.browse(cr, uid, ids, context=context):
            pricelist = self.get_pricelist(
                cr, uid, o.supplier_id, context=context)
            currency_id = pricelist.currency_id.id
            if not o.supplier_id or not o.product_id:
                raise Warning(
                    _('Warning!'), _('To create invoice expenses must have supplier and product'))
            if (o.supplier_id.id in partner_currency) and (partner_currency[o.supplier_id.id] <> currency_id):
                raise Warning(
                    _('Error!'),
                    _('You cannot group expenses having different currencies for the same supplier.'))

            partner_currency[o.supplier_id.id] = currency_id
        if grouped:
            for supplier_id in partner_currency:
                expense_ids = self.search(
                    cr, uid, [('id', 'in', ids), ('supplier_id', '=', supplier_id)], context=context)
                invoice_ids.append(
                    self._invoice_create(cr, uid, expense_ids, context=context))
        else:
            for expense_id in ids:
                invoice_ids.append(
                    self._invoice_create(cr, uid, [expense_id], context=context))
        return invoice_ids

    def _invoice_create(self, cr, uid, ids, context=None):
        inv_obj = self.pool.get('account.invoice')
        if context is None:
            context = {}
        # TODO
        # self.check_travel_one_partner
        # Just to make clear that all ids should be from the same partner
        partner_expense_ids = ids
        invoice_line_ids = self.invoice_line_create(
            cr, uid, partner_expense_ids, context=context)

        invoice_vals = self._prepare_invoice(
            cr, uid, partner_expense_ids, invoice_line_ids, context=context)
        inv_id = inv_obj.create(cr, uid, invoice_vals, context=context)
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], invoice_vals[
                                                          'payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        print 'expe', inv_id
        return inv_id

    def get_pricelist(self, cr, uid, partner, context=None):
        if partner.property_product_pricelist:
            return partner.property_product_pricelist
        else:
            pricelist_ids = self.pool['product.pricelist'].search(
                cr, uid, [('type', '=', 'purchase')], context=context)
            if pricelist_ids:
                pricelist_id = pricelist_ids[0]
            else:
                raise Warning(
                    _('Error!'), _('Order cannot be created because no purchase pricelist exists!'))
        return self.pool['product.pricelist'].browse(cr, uid, pricelist_id, context=context)

    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        create_ids = []
        if context.get('grouped_line'):
            product_ids = [x.product_id.id for x in self.browse(
                cr, uid, ids, context=context) if x.product_id]
            for product_id in list(set(product_ids)):
                expense_ids = self.search(
                    cr, uid,
                    [('id', 'in', ids), ('product_id', '=', product_id)],
                    context=context)
                if expense_ids == []:
                    expense_ids = ids
                expenses = self.browse(cr, uid, expense_ids, context=context)
                vals = self._prepare_order_line_invoice_line(
                    cr, uid, expenses, context=context)
                if vals:
                    inv_line_id = self.pool.get('account.invoice.line').create(
                        cr, uid, vals, context=context)
                    self.write(
                        cr, uid, expense_ids, {'invoice_line_id': inv_line_id}, context=context)
                    create_ids.append(inv_line_id)
        else:
            for expense in self.browse(cr, uid, ids, context=context):
                vals = self._prepare_order_line_invoice_line(
                    cr, uid, expense, context=context)
                if vals:
                    inv_line_id = self.pool.get('account.invoice.line').create(
                        cr, uid, vals, context=context)
                    self.write(
                        cr, uid, [expense.id], {'invoice_line_id': inv_line_id}, context=context)
                    create_ids.append(inv_line_id)
        return create_ids

    def _prepare_order_line_invoice_line(self, cr, uid, expense, context=None):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        res = {}
        if context.get('grouped_line'):
            if not expense[0].invoice_line_id:
                if expense[0].product_id:
                    account_id = expense[
                        0].product_id.property_account_income.id
                    if not account_id:
                        account_id = expense[
                            0].product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise Warning(_('Error!'),
                                      _('Please define income account for this product: "%s" (id:%d).') %
                                      (expense.product_id.name, expense.product_id.id,))
            fpos = expense[0].supplier_id.property_account_position.id or False
            account_id = self.pool.get('account.fiscal.position').map_account(
                cr, uid, fpos, account_id)
            tax_ids = self.pool.get('account.fiscal.position').map_tax(
                cr, uid, fpos, expense[0].product_id.taxes_id)
            name = expense[0].product_id.name
            name += ', Hoja de Ruta: '
            name += ", ".join(
                [x.waybill_id.reference for x in expense if x.waybill_id.reference])
            pu = 0.0
            uosqty = 0.0
            for expense_id in expense:
                uosqty = uosqty + expense_id.product_uom_qty
                if uosqty:
                    pu = round(expense_id.price_unit,
                               self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
                if not account_id:
                    raise Warning(_('Error!'),
                                  _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'uos_id': expense[0].product_id and expense[0].product_id.uom_id.id or False,
                'product_id': expense[0].product_id.id or False,
                'invoice_line_tax_id': [(6, 0, tax_ids)],
            }

        else:
            if not expense.invoice_line_id:
                if expense.product_id:
                    account_id = expense.product_id.property_account_income.id
                    if not account_id:
                        account_id = expense.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise Warning(_('Error!'),
                                      _('Please define income account for this product: "%s" (id:%d).') %
                                      (expense.product_id.name, expense.product_id.id,))
                uosqty = self._get_line_qty(cr, uid, expense, context=context)
                uos_id = self._get_line_uom(cr, uid, expense, context=context)
                pu = 0.0
                if uosqty:
                    pu = round(expense.price_unit,
                               self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
                fpos = expense.supplier_id.property_account_position.id or False
                account_id = self.pool.get('account.fiscal.position').map_account(
                    cr, uid, fpos, account_id)
                if not account_id:
                    raise Warning(_('Error!'),
                                  _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
                tax_ids = self.pool.get('account.fiscal.position').map_tax(
                    cr, uid, fpos, expense.product_id.taxes_id)
                res = {
                    'name': expense.product_id.name,
                    'account_id': account_id,
                    'price_unit': pu,
                    'quantity': uosqty,
                    # 'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': expense.product_id.id or False,
                    # TODO: add tax
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                }

        return res

    def _get_line_qty(self, cr, uid, expense, context=None):
        return expense.product_uom_qty

    def _get_line_uom(self, cr, uid, expense, context=None):
        return expense.product_id and expense.product_id.uom_id.id or False

    def _prepare_invoice(self, cr, uid, partner_expense_ids, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        expense = self.browse(cr, uid, partner_expense_ids[0], context=context)
        partner = expense.supplier_id
        waybill = self.browse(
            cr, uid, partner_expense_ids[0], context=context).waybill_id
        company = waybill.company_id
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
                                                              [('type', '=', 'purchase'),
                                                               ('company_id', '=', company.id)],
                                                              limit=1)
        if not journal_ids:
            raise Warning(_('Error!'),
                          _('Please define purchases journal for this company: "%s" (id:%d).') % (company.name, company.id))
        origin = _('Gastos de Hoja de Ruta')
        invoice_vals = {
            'origin': origin,
            'type': 'in_invoice',
            'account_id': partner.property_account_payable.id,
            'partner_id': partner.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': self.get_pricelist(cr, uid, partner, context=context).currency_id.id,
            'payment_term': partner.property_supplier_payment_term and partner.property_supplier_payment_term.id or False,
            'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
            'date_invoice': context.get('date_invoice', False),
            'company_id': company.id,
        }
        return invoice_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
