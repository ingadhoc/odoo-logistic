# -*- coding: utf-8 -*-


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

    @api.one
    def _get_requirement_state(self, initial_odometer_id, arg):
        # res = dict.fromkeys(ids, False)
        requirement_obj = self.env['logistic.requirement']
        self.requirement_state = 'ok'
        if requirement_obj.search([('partner_id', '=', self.id), ('state', '=', 'need_renew')]):
            self.requirement_state = 'need_renew'
        elif requirement_obj.search([('partner_id', '=', self.id), ('state', '=', 'next_to_renew')]):
            self.requirement_state = 'next_to_renew'
        #     res[record_id] = state
        # return res

    document_ids = fields.One2many(
        'logistic.requirement', 'partner_id',
        context={'default_type': 'document'},
        domain=[('type', '=', 'document'),
                ('state', 'not in', ['renewed', 'cancelled'])],
        string='Documents')
    requirement_state = fields.Selection(
        selection=_requirement_states,
        compute='_get_requirement_state', string="Requirements State")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
