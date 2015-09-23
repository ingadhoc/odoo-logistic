# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################


from openerp import models, fields
from openerp import netsvc


class waybill_driver_payment(models.Model):

    """"""

    _name = 'logistic.waybill_driver_payment'
    _description = 'waybill_driver_payment'
    _inherit = 'ir.needaction_mixin', 'mail.thread'

    _states_ = [
        # State machine: driver_payment_basic
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    _track = {
        'state': {
            'logistic.waybill_driver_payment_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'logistic.waybill_driver_payment_paid': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'paid',
            'logistic.waybill_driver_payment_cancelled': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancelled',
        },
    }

    name = fields.Char(
        string='Name',
        readonly=True,
        required=True, states={'draft': [('readonly', False)]})
    date = fields.Date(
        string='Date',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default=fields.date.today())
    driver_id = fields.Many2one(
        'res.partner',
        string='Driver',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        context={'default_is_driver': True}, domain=[('is_driver', '=', True)])
    note = fields.Text(string='Note')
    state = fields.Selection(_states_, "State", default='draft')
    waybill_ids = fields.One2many(
        'logistic.waybill',
        'driver_payment_id',
        string='Waybills',
        readonly=True, states={'draft': [('readonly', False)]})

    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(
                uid, 'logistic.waybill_driver_payment', obj_id, cr)
            wf_service.trg_create(
                uid, 'logistic.waybill_driver_payment', obj_id, cr)
        return True
