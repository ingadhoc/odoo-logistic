# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from datetime import datetime
from openerp import models, fields, api


class waybill(models.Model):

    """"""

    _inherit = 'logistic.waybill'
    _order = 'date desc'

    @api.one
    @api.depends('date_finish', 'date_start')
    def _get_days_range(self):
        if self.date_finish and self.date_start:
            date_start = datetime.strptime(
                self.date_start, '%Y-%m-%d  %H:%M:%S')
            date_finish = datetime.strptime(
                self.date_finish, '%Y-%m-%d  %H:%M:%S')
            self.days_range = (date_finish - date_start).days
        else:
            self.days_range = 0

    @api.one
    @api.depends(
        'state',
        'travel_ids',
        'travel_ids.price',
        'waybill_expense_ids',
        'waybill_expense_ids.price_subtotal'
    )
    def _get_total(self):
        total_price = 0
        total_cost = 0
        if self.travel_ids:
            for travel in self.travel_ids:
                total_price = total_price + travel.price
        if self.waybill_expense_ids:
            for travel in self.waybill_expense_ids:
                total_cost = total_cost + travel.price_subtotal
        net = total_price - total_cost
        net_avg = 0
        if total_cost != 0:
            net_avg = ((total_price / total_cost) - 1) * 100

        self.total_price = total_price
        self.total_cost = total_cost
        self.net_avg = net_avg
        self.net = net

    @api.one
    @api.depends(
        'state',
        'distance',
        'total_price',
        'total_cost',
        'travel_ids',
        'travel_ids.price',
        'waybill_expense_ids',
        'waybill_expense_ids.price_subtotal')
    def _get_price_cost_km(self):
        if self.distance != 0:
            self.price_km = self.total_price / self.distance
            self.cost_km = self.total_cost / self.distance
            self.net_km = self.price_km - self.cost_km
        else:
            self.price_km = 0
            self.cost_km = 0
            self.net_km = 0

    days_range = fields.Integer(compute='_get_days_range', string='Days Range')
    total_price = fields.Float(
        compute='_get_total', string='Total Price',
        multi="total", store=True)

    total_cost = fields.Float(
        compute='_get_total', string='Total Cost',
        multi="total", store=True)
    net = fields.Float(
        compute='_get_total', string='Net', multi="total", store=True)
    net_avg = fields.Float(
        compute='_get_total',
        string='Net %', multi="total", store=True, group_operator="avg")
    price_km = fields.Float(
        compute='_get_price_cost_km', string='Price per km',
        multi="total_km", store=True, group_operator="avg")
    cost_km = fields.Float(
        compute='_get_price_cost_km',
        tring='Cost per km',
        multi="total_km", store=True, group_operator="avg")
    net_km = fields.Float(
        compute='_get_price_cost_km',
        string='Net per km',
        multi="total_km", store=True, group_operator="avg")
