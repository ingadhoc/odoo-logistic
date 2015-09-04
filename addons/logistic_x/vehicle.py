# -*- coding: utf-8 -*-

from openerp import models, fields


class vehicle(models.Model):

    """"""

    _inherit = 'fleet.vehicle'

    _requirement_states = [
        # State machine: requirement_basic
        ('ok', 'OK'),
        ('next_to_renew', 'Next To Renew'),
        ('need_renew', 'Need Renew'),
    ]

    def _get_requirement_state(self, cr, uid, ids, initial_odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        requirement_obj = self.pool['logistic.requirement']
        for record_id in ids:
            state = 'ok'
            if requirement_obj.search(cr, uid, [('vehicle_id', '=', record_id), ('state', '=', 'need_renew')], context=context):
                state = 'need_renew'
            elif requirement_obj.search(cr, uid, [('vehicle_id', '=', record_id), ('state', '=', 'next_to_renew')], context=context):
                state = 'next_to_renew'
            res[record_id] = state
        return res

    length = fields.Float(string='Length  (mts)')
    width = fields.Float(string='Width (mts)')
    capacity = fields.Integer('Capacity (pallets)')
    name = fields.Char('Name', required=True)
        # 'maintenance_ids': fields.one2many('logistic.requirement', 'res_id',
        #     context={'default_type':'maintenance','default_model':self._name},
        #     domain=lambda self: [('model', '=', self._name),('type', '=', 'maintenance')],
        #     auto_join=True,
        #     string='Maintenances',),
    maintenance_ids = fields.One2many(
        'logistic.requirement', 'vehicle_id',
        context={'default_type': 'maintenance'},
        domain=[('type', '=', 'maintenance'),
                ('state', 'not in', ['renewed', 'cancelled'])],
        string='Maintenances',)
    document_ids = fields.One2many(
        'logistic.requirement', 'vehicle_id',
        context={'default_type': 'document'},
        domain=[('type', '=', 'document'),
                ('state', 'not in', ['renewed', 'cancelled'])],
        string='Documents',)
    requirement_state = fields.Selection(
        selection=_requirement_states,
        string="Requirements State", compute='_get_requirement_state')
