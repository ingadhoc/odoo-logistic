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

class waybill(osv.osv):
    """"""
    
    _name = 'logistic.waybill'
    _description = 'waybill'
    _inherits = {  }
    _inherit = [ 'ir.needaction_mixin','mail.thread' ]

    _states_ = [
        # State machine: weybill_basic
        ('active','Active'),
        ('closed','Closed'),
        ('cancelled','Cancelled'),
    ]
    _track = {
        'state': {
            'logistic.waybill_active': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active',
            'logistic.waybill_closed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'closed',
            'logistic.waybill_cancelled': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancelled',
        },
    }
    _columns = {
        'name': fields.char(string='Name', readonly=True),
        'reference': fields.char(string='Reference'),
        'date': fields.date(string='Date', readonly=True, required=True, states={'active': [('readonly', False)]}),
        'tractor_id': fields.many2one('fleet.vehicle', string='Tractor', readonly=True, required=True, states={'active': [('readonly', False)]}, context={'default_type':'tractor'}, domain=[('type','=','tractor')], on_change='on_change_vehicle(vehicle_id, context)'),
        'wagon_id': fields.many2one('fleet.vehicle', string='Wagon', readonly=True, required=True, states={'active': [('readonly', False)]}, context={'default_type':'wagon'}, domain=[('type','=','wagon')]),
        'driver_id': fields.many2one('res.partner', string='Driver', readonly=True, required=True, states={'active': [('readonly', False)]}, context={'default_is_driver':True}, domain=[('is_driver','=',True)]),
        'initial_odometer': fields.float(string='Initial Odometer', readonly=True, required=True, states={'active': [('readonly', False)]}),
        'final_odometer': fields.float(string='Final Odometer', readonly=True, required=True, states={'active': [('readonly', False)]}),
        'odometer_unit': fields.selection([(u'kilometers', u'Kilometers'), (u'miles', u'Miles')], string='Odometer Unit', readonly=True, required=True, states={'active': [('readonly', False)]}),
        'note': fields.text(string='Note'),
        'company_id': fields.many2one('res.company', string='Company', required=True),
        'date_start': fields.datetime(string='Date Start', readonly=True, states={'active': [('readonly', False)]}),
        'date_finish': fields.datetime(string='Date Finish', readonly=True, states={'active': [('readonly', False)]}),
        'driver_product_id': fields.many2one('product.product', string='Driver Product', readonly=True, states={'active': [('readonly', False)]}, context={'default_type':'service','default_service_subtype':'other'}, domain=[('type','=','service'),('service_subtype','=','other')]),
        'distance': fields.float(string='Distance', readonly=True),
        'driver_unit_price': fields.float(string='Driver Unit Price', states={'active': [('readonly', False)]}),
        'currency_id': fields.many2one('res.currency', string='Currency'),
        'company_id': fields.many2one('res.company', string='Company', required=True),
        'initial_liters': fields.float(string='Initial Liters', readonly=True, states={'active': [('readonly', False)]}),
        'final_liters': fields.float(string='Final Liters', readonly=True, states={'active': [('readonly', False)]}),
        'charged_liters': fields.float(string='Charged Liters', readonly=True),
        'consumed_liters': fields.float(string='Consumed Liters', readonly=True),
        'consumption': fields.float(string='Consumption (Km/L)', readonly=True),
        'state': fields.selection(_states_, "State"),
        'travel_ids': fields.one2many('logistic.travel', 'waybill_id', string='Travels', readonly=True, states={'active': [('readonly', False)]}), 
        'waybill_expense_ids': fields.one2many('logistic.waybill_expense', 'waybill_id', string='Expenses', readonly=True, states={'active': [('readonly', False)]}), 
        'driver_payment_id': fields.many2one('logistic.waybill_driver_payment', string='Driver Payment', readonly=True), 
    }

    _defaults = {
        'state': 'active',
        'date': fields.date.context_today,
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'logistic.waybill', context=c),
        'currency_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'logistic.waybill', context=c),
        'odometer_unit': 'kilometers',
    }


    _constraints = [
    ]


    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        """"""
        raise NotImplementedError

    def action_wfk_set_active(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'active'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'logistic.waybill', obj_id, cr)
            wf_service.trg_create(uid, 'logistic.waybill', obj_id, cr)
        return True



waybill()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
