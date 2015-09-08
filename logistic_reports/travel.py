# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from datetime import datetime
from calendar import monthrange


class travel(models.Model):

    """"""

    _inherit = 'logistic.travel'

    @api.one
    @api.depends('from_date', 'to_date')
    def _get_days_range(self):
        if self.from_date and self.to_date:
            from_date = datetime.strptime(
                self.from_date, '%Y-%m-%d  %H:%M:%S')
            to_date = datetime.strptime(
                self.to_date, '%Y-%m-%d  %H:%M:%S')
            days = (to_date - from_date).days
            days_avg = days * 100.0 / \
                monthrange(from_date.year, from_date.month)[1]
            self.days_range = days
            self.days_range_avg = days_avg
        else:
            self.days_range = 0
            self.days_range_avg = 0

    days_range = fields.Integer(
        compute='_get_days_range', string='Days Range',
        multi="cal_days",
        store=True)
    days_range_avg = fields.Float(
        compute='_get_days_range', string='Days Range Average',
        multi="cal_days",
        store=True)
