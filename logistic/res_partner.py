# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################


from openerp import models, fields, api


class res_partner(models.Model):

    """"""

    _inherit = 'res.partner'

    _requirement_states = [
        # State machine: requirement_basic
        ('ok', 'OK'),
        ('next_to_renew', 'Next To Renew'),
        ('need_renew', 'Need Renew'),
    ]

    is_driver = fields.Boolean(
        string='Is Driver?'
    )
    driver_product_id = fields.Many2one(
        'product.product',
        string='Driver Product',
        context={'default_type': 'service',
                 'default_service_subtype': 'other'},
        domain=[('type', '=', 'service'), ('service_subtype', '=', 'other')]
    )

    document_ids = fields.One2many(
        'logistic.requirement', 'partner_id',
        context={'default_type': 'document'},
        domain=[('type', '=', 'document'),
                ('state', 'not in', ['renewed', 'cancelled'])],
        string='Documents'
    )
    requirement_state = fields.Selection(
        selection=_requirement_states,
        compute='_get_requirement_state',
        string="Requirements State"
    )

    @api.one
    def _get_requirement_state(self):
        self.requirement_state = 'ok'
        if self.env['logistic.requirement'].search(
                [('partner_id', '=', self.id), ('state', '=', 'need_renew')]):
            self.requirement_state = 'need_renew'
        elif self.env['logistic.requirement'].search(
                [('partner_id', '=', self.id), ('state', '=', 'next_to_renew')]):
            self.requirement_state = 'next_to_renew'
