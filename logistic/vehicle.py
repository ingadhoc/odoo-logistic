# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import models, fields, api


class vehicle(models.Model):

    """"""

    _inherit = 'fleet.vehicle'

    _requirement_states = [
        # State machine: requirement_basic
        ('ok', 'OK'),
        ('next_to_renew', 'Next To Renew'),
        ('need_renew', 'Need Renew'),
    ]

    @api.one
    def _get_requirement_state(self):
        self.requirement_state = 'ok'
        if self.env['logistic.requirement'].search(
                [('vehicle_id', '=', self.id), ('state', '=', 'need_renew')]):
            self.requirement_state = 'need_renew'
        elif self.env['logistic.requirement'].search(
                [('vehicle_id', '=', self.id), ('state', '=', 'next_to_renew')]):
            self.requirement_state = 'next_to_renew'

    type = fields.Selection(
        [('car', 'Car'), ('tractor', 'Tractor'), ('wagon', 'Wagon')],
        string='Type')
    wagon_id = fields.Many2one(
        'fleet.vehicle',
        string='Wagon',
        context={'default_type': 'wagon'}, domain=[('type', '=', 'wagon')])
    driver_id = fields.Many2one(
        'res.partner',
        string='Driver',
        context={'default_is_driver': True}, domain=[('is_driver', '=', True)])
    default_validity = fields.Integer(string='default_validity')
    default_kilometers = fields.Integer(string='default_kilometers')
    year = fields.Integer(string='Year')
    motor_sn = fields.Char(string='Motor Number')
    length = fields.Float(string='Length  (mts)')
    width = fields.Float(string='Width (mts)')
    capacity = fields.Integer('Capacity (pallets)')
    name = fields.Char('Name', required=True)
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
