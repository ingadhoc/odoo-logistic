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

class requirement(osv.osv):
    """"""
    
    _name = 'logistic.requirement'
    _description = 'requirement'
    _inherits = {  }
    _inherit = [ 'ir.needaction_mixin','mail.thread' ]

    _states_ = [
        # State machine: requirement_basic
        ('draft','Draft'),
        ('ok','OK'),
        ('next_to_renew','Next To Renew'),
        ('need_renew','Need Renew'),
        ('renewal_requested','Renewal Requested'),
        ('renewed','Renewed'),
        ('cancelled','Cancelled'),
    ]
    _track = {
        'state': {
            'logistic.requirement_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'logistic.requirement_ok': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'ok',
            'logistic.requirement_next_to_renew': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'next_to_renew',
            'logistic.requirement_need_renew': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'need_renew',
            'logistic.requirement_renewal_requested': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'renewal_requested',
            'logistic.requirement_renewed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'renewed',
            'logistic.requirement_cancelled': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancelled',
        },
    }
    _columns = {
        'date': fields.date(string='Date', readonly=True, required=True),
        'type': fields.selection([(u'maintenance', u'Maintenance'), (u'document', u'Document')], string='Type', required=True),
        'vehicle_id': fields.many2one('fleet.vehicle', string='Vehicle'),
        'partner_id': fields.many2one('res.partner', string='Driver', context={'default_is_driver':True}, domain=[('is_driver','=',True)]),
        'product_id': fields.many2one('product.product', string='Product', required=True),
        'name': fields.char(string='Name', required=True),
        'initial_odometer': fields.float(string='Initial Odometer'),
        'odometer_range': fields.float(string='Odometer Range'),
        'warning_range': fields.float(string='Warning Range'),
        'odometer_unit': fields.selection([(u'kilometers', u'Kilometers'), (u'miles', u'Miles')], string='Odometer Unit'),
        'issue_date': fields.date(string='Issue Date'),
        'expiration_date': fields.date(string='Expiration Date'),
        'note': fields.text(string='Note'),
        'remaining_range': fields.integer(string='Remaining Range'),
        'remaining_days': fields.integer(string='Remaining Days'),
        'warning_days': fields.integer(string='Warning Days'),
        'renewed_by_id': fields.many2one('logistic.requirement', string='Renewed By', readonly=True),
        'renews_id': fields.many2one('logistic.requirement', string='Renews', readonly=True),
        'id': fields.integer(string='Id', readonly=True),
        'po_line_id': fields.many2one('sale.order.line', string='Purchase Order Line', readonly=True),
        'state': fields.selection(_states_, "State"),
    }

    _defaults = {
        'state': 'draft',
        'date': fields.date.context_today,
        'odometer_unit': 'kilometers',
        'issue_date': fields.date.context_today,
    }


    _constraints = [
    ]


    def on_change_product(self, cr, uid, ids, product_id, issue_date, context=None):
        """"""
        raise NotImplementedError

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        """"""
        raise NotImplementedError

    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'logistic.requirement', obj_id, cr)
            wf_service.trg_create(uid, 'logistic.requirement', obj_id, cr)
        return True



requirement()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
