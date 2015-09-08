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

class waybill_driver_payment(osv.osv):
    """"""
    
    _name = 'logistic.waybill_driver_payment'
    _description = 'waybill_driver_payment'
    _inherits = {  }
    _inherit = [ 'ir.needaction_mixin','mail.thread' ]

    _states_ = [
        # State machine: driver_payment_basic
        ('draft','Draft'),
        ('paid','Paid'),
        ('cancelled','Cancelled'),
    ]
    _track = {
        'state': {
            'logistic.waybill_driver_payment_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'logistic.waybill_driver_payment_paid': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'paid',
            'logistic.waybill_driver_payment_cancelled': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancelled',
        },
    }
    _columns = {
        'name': fields.char(string='Name', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'date': fields.date(string='Date', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'driver_id': fields.many2one('res.partner', string='Driver', readonly=True, required=True, states={'draft': [('readonly', False)]}, context={'default_is_driver':True}, domain=[('is_driver','=',True)]),
        'note': fields.text(string='Note'),
        'state': fields.selection(_states_, "State"),
        'waybill_ids': fields.one2many('logistic.waybill', 'driver_payment_id', string='Waybills', readonly=True, states={'draft': [('readonly', False)]}), 
    }

    _defaults = {
        'state': 'draft',
        'date': fields.date.context_today,
    }


    _constraints = [
    ]


    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'logistic.waybill_driver_payment', obj_id, cr)
            wf_service.trg_create(uid, 'logistic.waybill_driver_payment', obj_id, cr)
        return True



waybill_driver_payment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
