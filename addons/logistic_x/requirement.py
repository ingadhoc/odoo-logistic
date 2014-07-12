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


import re
from openerp import netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _
# from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time

class requirement(osv.osv):
    """"""
    
    _inherit = 'logistic.requirement'

    def _get_initial_odometer(self, cr, uid, ids, initial_odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr,uid,ids,context=context):
            if record.initial_odometer_id:
                res[record.id] = record.initial_odometer_id.value
        return res

    def _set_initial_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).vehicle_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
        return self.write(cr, uid, id, {'initial_odometer_id': odometer_id}, context=context)

    def get_remainings(self, cr, uid, ids, name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):            
            res[record.id] = {
                'remaining_range': False,
                'remaining_days': False,
            }            
            if record.type == 'maintenance':
                if record.initial_odometer and record.vehicle_id.odometer and record.odometer_range:
                    res[record.id]['remaining_range'] = record.initial_odometer + record.odometer_range - record.vehicle_id.odometer
            elif record.expiration_date:
                today = datetime.datetime.today()
                expiration_date = datetime.datetime.strptime(record.expiration_date, DEFAULT_SERVER_DATE_FORMAT)
                remaining_days = (expiration_date - today).days
                res[record.id]['remaining_days'] = remaining_days
        return res

    def get_renews_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        for record_id in ids:
            renews_ids = self.search(cr, uid, [('renewed_by_id','=', record_id)], context=context)
            print 'renews_ids', renews_ids
            if renews_ids:
                res[record_id] = renews_ids[0]
            else:
                res[record_id] = False
        return res

    _columns = {
        'initial_odometer_id': fields.many2one('fleet.vehicle.odometer', 'Initial Odometer', help='Odometer measure of the vehicle at the moment of this log'),
        'initial_odometer': fields.function(_get_initial_odometer, fnct_inv=_set_initial_odometer, type='float', string='Initial Odometer', ),    
        'remaining_range': fields.function(get_remainings, type='integer', string='Remaining Range', multi='get_remainings'),
        'remaining_days': fields.function(get_remainings, type='integer', string='Remaining Days', multi='get_remainings'),
        'renews_id': fields.function(get_renews_id, type='many2one', relation='logistic.requirement', string='Renews',),
        'po_line_id': fields.many2one('purchase.order.line', string='Purchase Order Line', readonly=True,),
        'invoice_line_ids': fields.related('po_line_id', 'invoice_lines', type='many2many', relation='account.invoice.line', string='Invoice Lines', readonly=True, ), 
        'purchase_order_id': fields.related('po_line_id', 'order_id', type='many2one', relation='purchase.order', string='Purchase Order', readonly=True, ), 
    }

    _defaults = {
    }

    def unlink(self, cr, uid, ids, context=None):
        for t in self.read(cr, uid, ids, ['state'], context=context):
            if t['state'] not in ('draft', 'cancelled'):
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete requirement(s) which are not in draft or cancelled state.'))
        return super(requirement, self).unlink(cr, uid, ids, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.renewed_by_id:
                raise osv.except_osv(
                    _('Invalid Action!'),
                    _('Cannot cancel requirements that has a renewed by requirement! You must first delete the related renewed by requirement.'))
        return True

    def verify_requirement_state(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        date = time.strftime(DEFAULT_SERVER_DATE_FORMAT) 
        wf_service = netsvc.LocalService("workflow")
        # Next to renew requirements
        ok_requirement_ids = self.search(cr, uid, [('state','in', ['ok','need_renew'])], context=context)
        for record in self.browse(cr, uid, ok_requirement_ids, context):
            if record.remaining_range <= record.warning_days or record.remaining_range <= record.warning_range:
                wf_service.trg_validate(uid, 'logistic.requirement', record.id, 'sgn_next_to_renew', cr)

        # need renew requirements
        need_renew_ids = self.search(cr, uid, [('state','in', ['ok','next_to_renew']),('expiration_date','<=',date),('type','=','document')], context=context)
        
        # No peudo agregar esta parte en el search porque remianing_range es un function sin search
        maintenance_ids = self.search(cr, uid, [('state','in', ['ok','next_to_renew']),('type','=','maintenance')], context=context)
        for record in self.browse(cr, uid, maintenance_ids, context):
            if record.remaining_range <= 0:
                need_renew_ids.append(record.id)
        for record_id in need_renew_ids:
            wf_service.trg_validate(uid, 'logistic.requirement', record_id, 'sgn_need_renew', cr)                          

        return True

    def on_change_product(self, cr, uid, ids, product_id, issue_date, context=None):
        v = {}
        if product_id:
            product = self.pool['product.product'].browse(cr, uid, product_id, context=context)
            if product.service_subtype == 'maintenance':
                v = {
                    'odometer_range': product.default_range,
                    'warning_range': product.default_warning_range,
                    'name': product.name,
                }
            elif product.service_subtype == 'document':
                if issue_date and product.default_validity_days:
                    expiration_date = (datetime.datetime.strptime(issue_date, '%Y-%m-%d') + relativedelta(days=product.default_validity_days)).strftime('%Y-%m-%d')
                    v = {
                        'expiration_date': expiration_date,
                        'warning_days': product.default_warning_days,
                        'name': product.name,
                    }
        else:
            v = {
                'expiration_date': False,
                'warning_days': False,
                'name': False,
            }            
        return {'value': v}

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        v = {
            'initial_odometer': False,
        }        
        if vehicle_id:
            vehicle = self.pool['fleet.vehicle'].browse(cr, uid, vehicle_id, context=context)
            if vehicle.odometer:
                v = {
                    'initial_odometer': vehicle.odometer,
                }
        return {'value': v}

    def make_new_requirement(self, cr, uid, ids, po_line_dic, context=None):
        res = {}
        for requirement in self.browse(cr, uid, ids, context=context):
            if requirement.vehicle_id:
                initial_odometer = requirement.vehicle_id.odometer
            else:
                initial_odometer = False
            if requirement.expiration_date:
                expiration_date = (datetime.datetime.strptime(requirement.expiration_date, '%Y-%m-%d') + relativedelta(days=requirement.product_id.default_validity_days)).strftime('%Y-%m-%d')
            vals = {
                'type': requirement.type,
                'vehicle_id': requirement.vehicle_id.id, 
                'partner_id': requirement.partner_id.id, 
                'name': requirement.name,
                'product_id': requirement.product_id.id, 
                'initial_odometer': initial_odometer,
                'odometer_range': requirement.product_id.default_range, 
                'warning_range': requirement.product_id.default_warning_range, 
                'odometer_unit': requirement.product_id.range_unit, 
                'odometer_unit': requirement.product_id.range_unit, 
                'issue_date': requirement.expiration_date, 
                'expiration_date': requirement.expiration_date, 
                'warning_days': requirement.product_id.default_warning_days, 
                'note': requirement.note,
                'po_line_id': po_line_dic.get(requirement.id,False),
            }
            new_requirement_id = self.create(cr, uid, vals, context=context)
            res[requirement.id] = new_requirement_id
            self.write(cr, uid, [requirement.id], {'renewed_by_id': new_requirement_id}, context=context)
        return res

    def request_renew(self, cr, uid, ids, context=None):
        po_line_dic = self.make_po(cr, uid, ids, context=context)
        self.make_new_requirement(cr, uid, ids, po_line_dic, context=context)
        return True

    def set_ok(self, cr, uid, ids, context=None):
        for requirement in self.browse(cr, uid, ids, context=context):
            if requirement.renews_id:
                self.write
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'logistic.requirement', requirement.renews_id.id, 'sgn_renewed', cr)
        
    def check_supplier_info(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for requirement in self.browse(cr, uid, ids, context=context):
            message = ''
            partner = requirement.product_id.seller_id #Taken Main Supplier of Product of requirement.

            if not requirement.product_id.seller_ids:
                raise osv.except_osv(_('Error!'), _('No supplier defined for this product !'))
            elif not partner:
                raise osv.except_osv(_('Error!'), _('No default supplier defined for this product'))
            elif not partner_obj.address_get(cr, uid, [partner.id], ['delivery'])['delivery']:
                raise osv.except_osv(_('Error!'), _('No address defined for the supplier'))

            if message:
                if requirement.message != message:
                    cr.execute('update requirement_order set message=%s where id=%s', (message, requirement.id))
                return False

            if user.company_id and user.company_id.partner_id:
                if partner.id == user.company_id.partner_id.id:
                    raise osv.except_osv(_('Configuration Error!'), _('The product "%s" has been defined with your company as reseller which seems to be a configuration error!' % requirement.product_id.name))

        return True

    def _get_purchase_schedule_date(self, cr, uid, requirement, company, context=None):
        """Return the datetime value to use as Schedule Date (``date_planned``) for the
           Purchase Order Lines created to satisfy the given requirement.

           :param browse_record requirement: the requirement for which a PO will be created.
           :param browse_report company: the company to which the new PO will belong to.
           :rtype: datetime
           :return: the desired Schedule Date for the PO lines
        """
        requirement_date_planned = datetime.datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
        # requirement_date_planned = datetime.strptime(requirement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = (requirement_date_planned - relativedelta(days=company.po_lead))
        return schedule_date  
        
    def _get_purchase_order_date(self, cr, uid, requirement, company, schedule_date, context=None):
        """Return the datetime value to use as Order Date (``date_order``) for the
           Purchase Order created to satisfy the given requirement.

           :param browse_record requirement: the requirement for which a PO will be created.
           :param browse_report company: the company to which the new PO will belong to.
           :param datetime schedule_date: desired Scheduled Date for the Purchase Order lines.
           :rtype: datetime
           :return: the desired Order Date for the PO
        """
        seller_delay = int(requirement.product_id.seller_delay)
        return schedule_date - relativedelta(days=seller_delay)              

    def make_po(self, cr, uid, ids, context=None):
        """ Make purchase order from requirement
        @return: New created Purchase Orders requirement wise
        """
        self.check_supplier_info(cr, uid, ids, context=context)
        res = {}
        if context is None:
            context = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        partner_obj = self.pool.get('res.partner')
        uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        prod_obj = self.pool.get('product.product')
        acc_pos_obj = self.pool.get('account.fiscal.position')
        seq_obj = self.pool.get('ir.sequence')
        warehouse_ids = self.pool['stock.warehouse'].search(cr, uid, [], context=context)
        if warehouse_ids:
            warehouse = self.pool['stock.warehouse'].browse(cr, uid, warehouse_ids[0], context=context)    
        for requirement in self.browse(cr, uid, ids, context=context):
            partner = requirement.product_id.seller_id # Taken Main Supplier of Product of requirement.
            seller_qty = requirement.product_id.seller_qty
            partner_id = partner.id
            address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id
            uom_id = requirement.product_id.uom_po_id.id

            qty = 1
            if seller_qty:
                qty = max(qty,seller_qty)

            price = pricelist_obj.price_get(cr, uid, [pricelist_id], requirement.product_id.id, qty, partner_id, {'uom': uom_id})[pricelist_id]

            schedule_date = self._get_purchase_schedule_date(cr, uid, requirement, company, context=context)
            purchase_date = self._get_purchase_order_date(cr, uid, requirement, company, schedule_date, context=context)

            #Passing partner_id to context for purchase order line integrity of Line name
            new_context = context.copy()
            new_context.update({'lang': partner.lang, 'partner_id': partner_id})

            product = prod_obj.browse(cr, uid, requirement.product_id.id, context=new_context)
            taxes_ids = requirement.product_id.supplier_taxes_id
            taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)

            name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % requirement.name
            if requirement.vehicle_id:
                origin = requirement.vehicle_id.name
            elif requirement.partner_id:
                origin = requirement.partner_id.name
            else:
                origin = ''                       
            po_vals = {
                'name': name,
                'origin': origin + ' - ' + requirement.name,
                'partner_id': partner_id,
                'location_id': warehouse.lot_input_id.id,
                'warehouse_id': warehouse.id,
                'pricelist_id': pricelist_id,
                'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'company_id': company.id,
                'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                'payment_term_id': partner.property_supplier_payment_term.id or False,
            }
            po_id = self.pool.get('purchase.order').create(cr, uid, po_vals, context=context)
            name = product.partner_ref
            if product.description_purchase:
                name += '\n'+ product.description_purchase
            line_vals = {
                'name': name,
                'product_qty': qty,
                'product_id': requirement.product_id.id,
                'product_uom': uom_id,
                'price_unit': price or 0.0,
                'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'order_id': po_id,
                'taxes_id': [(6,0,taxes)],
            }
            po_line_id = self.pool.get('purchase.order.line').create(cr, uid, line_vals, context=context)

            # self.write(cr, uid, [requirement.id], {'po_line_id': po_line_id}, context=context)
            res[requirement.id] = po_line_id
        return res
        # return True


# This methods works and creates a requirement order than later will be a purchase order. The problem is that we want the requirement to have a m2o to the pruchase order line in order to have the price history
    # def _prepare_order_line_requirement(self, cr, uid, requirement, context=None):
    #     date_planned = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
    #     location_ids = self.pool['stock.warehouse'].search(cr, uid, [], context=context)
    #     company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
    #     if location_ids:
    #         default_location_id = location_ids[0]
    #     else:
    #         print 'error'
    #     if requirement.vehicle_id:
    #         name = requirement.vehicle_id.name
    #     elif requirement.partner_id:
    #         name = requirement.partner_id.name
    #     else:
    #         name = ''           
    #     return {
    #         'name': requirement.name,
    #         'origin': name + ' - ' + requirement.name,
    #         'date_planned': date_planned,
    #         'product_id': requirement.product_id.id,
    #         'product_qty': 1,
    #         'product_uom': requirement.product_id.uom_id.id,
    #         'product_uos_qty': 1,
    #         'product_uos': requirement.product_id.uom_id.id,
    #         'location_id': default_location_id,
    #         'procure_method': 'make_to_order',
    #         # 'move_id': move_id,
    #         'company_id': company.id,
    #         # 'note': line.name,
    #     }

    # def make_purchase_order(self, cr, uid, ids, context=None):
    #     requirement_obj = self.pool.get('requirement.order')
    #     requirement_ids = []
    #     for requirement in self.browse(cr, uid, ids, context=context):
    #         requirement_id = requirement_obj.create(cr, uid, self._prepare_order_line_requirement(cr, uid, requirement, context=context))        
    #         requirement_ids.append(requirement_id)
    #         wf_service = netsvc.LocalService("workflow")
    #         wf_service.trg_validate(uid, 'requirement.order', requirement_id, 'button_confirm', cr)
    #     return requirement_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
