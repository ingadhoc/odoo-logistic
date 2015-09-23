# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
from openerp.exceptions import Warning


class logistic_travel_make_sale_order(models.TransientModel):
    _name = "logistic.travel.make.sale.order"
    _description = "Travel Make Sale Orders"

    def make_orders(self, cr, uid, ids, context=None):
        """
             To make sale orders.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: A dictionary which of fields with values.

        """
        if context is None:
            context = {}
        res = False
        orders = []

    # TODO: merge with sale.py/make_invoice
        def make_orders(travel):
            """
                 To make orders.

                 @param order:
                 @param lines:

                 @return:

            """
            a = travel.partner_id.property_account_receivable.id
            if travel.partner_id and travel.partner_id.property_payment_term.id:
                pay_term = travel.partner_id.property_payment_term.id
            else:
                pay_term = False

            if not travel.partner_id.property_product_pricelist:
                pricelist_id = travel.partner_id.property_product_pricelist
            else:
                pricelist_ids = self.pool['product.pricelist'].search(
                    cr, uid, [('type', '=', 'sale')], context=context)
                if pricelist_ids:
                    pricelist_id = pricelist_ids[0]
                else:
                    raise Warning(
                        _('Error!'), _('Order cannot be created because not sale pricelist exists!'))
            inv = {
                # 'name': order.client_order_ref or '',
                'origin': travel.waybill_id.name,
                # 'type': 'out_invoice',
                # 'reference': "P%dSO%d" % (order.partner_id.id, order.id),
                # 'account_id': a,
                'partner_id': travel.partner_id.id,
                'partner_invoice_id': travel.partner_id.id,
                'partner_shipping_id': travel.partner_id.id,
                'pricelist_id': pricelist_id,
                # 'order_line': [(6, 0, lines)],
                # 'currency_id' : travel.pricelist_id.currency_id.id,
                # 'comment': order.note,
                'payment_term': pay_term,
                'fiscal_position': travel.partner_id.property_account_position.id,
                'user_id': travel.partner_id.user_id and travel.partner_id.user_id.id or False,
                # 'company_id': order.company_id and order.company_id.id or False,
                'date_order': fields.date.today(),
            }
            order_id = self.pool.get('sale.order').create(cr, uid, inv)
            return order_id

        def make_lines(travel, order_id):
            """
                 To make orders.

                 @param order:
                 @param lines:

                 @return:

            """
            fpos = travel.partner_id.property_account_position or False
            tax_ids = self.pool.get('account.fiscal.position').map_tax(
                cr, uid, fpos, travel.product_id.taxes_id)

            line = {
                # 'name': travel.product_id.name,
                # 'sequence': line.sequence,
                # 'origin': travel.waybill_id.name,
                # 'account_id': account_id,
                'order_id': order_id,
                'price_unit': travel.price,
                # 'discount': line.discount,
                'tax_id': tax_ids,
                'product_id': travel.product_id.id,
                'name': travel.product_id.name,
                # 'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                # 'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }

            line_id = self.pool.get('sale.order.line').create(cr, uid, line)
            return line_id

        travel_obj = self.pool.get('logistic.travel')
        # sales_order_line_obj = self.pool.get('sale.order.line')
        # sales_order_obj = self.pool.get('sale.order')
        # wf_service = netsvc.LocalService('workflow')
        for travel in travel_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            if travel.partner_id and travel.product_id and not travel.order_line_id:
                order_id = make_orders(travel)
                line_id = make_lines(travel, order_id)
                orders.append(order_id)
                travel_obj.write(
                    cr, uid, travel.id, {'order_line_id': line_id}, context=context)
        #     if (not line.order_line_id):
        # if (not line.ordered) and (line.state not in ('draft', 'cancel')):
        #         if not line.order_line_id in orders:
        #             orders[line.order_id] = []
        #         orders[line.id] = []
        #         line_id = travel_obj.order_line_create(cr, uid, [line.id])
        #         for lid in line_id:
        #             orders[line.order_id].append(lid)
        # for order, il in invoices.items():
        #     res = make_invoice(order, il)
        #     cr.execute('INSERT INTO sale_order_invoice_rel \
        #             (order_id,invoice_id) values (%s,%s)', (order.id, res))
        #     flag = True
        #     data_sale = sales_order_obj.browse(cr, uid, order.id, context=context)
        #     for line in data_sale.order_line:
        #         if not line.invoiced:
        #             flag = False
        #             break
        #     if flag:
        #         wf_service.trg_validate(uid, 'sale.order', order.id, 'manual_invoice', cr)
        #         sales_order_obj.write(cr, uid, [order.id], {'state': 'progress'})
            elif not travel.partner_id:
                raise Warning(_('Error!'), _(
                    'Sale order cannot be created because there is no partner defined for this travel!'))
            elif not travel.product_id:
                raise Warning(_('Error!'), _(
                    'Sale order cannot be created because there is no product defined for this travel!'))
            elif travel.order_line_id:
                raise Warning(_('Error!'), _(
                    'Sale order cannot be created because it already has a related sale order line!'))
        if context.get('open_orders', False):
            return self.open_orders(cr, uid, ids, orders[0], context=context)
        return {'type': 'ir.actions.act_window_close'}

    def open_orders(self, cr, uid, ids, order_ids, context=None):
        """ open a view on one of the given order_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(
            cr, uid, 'sale', 'view_order_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(
            cr, uid, 'sale', 'view_quotation_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Sale Orders'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'res_id': order_ids,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': {},
            'type': 'ir.actions.act_window',
        }
