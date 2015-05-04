# -*- coding: utf-8 -*-
from datetime import datetime
from openerp.osv import osv, fields
from openerp.osv.orm import except_orm
from openerp.tools.translate import _


class waybill(osv.osv):

    """"""

    _inherit = 'logistic.waybill'
    _order = 'date desc'

    def _get_days_range(self, cr, uid, ids, fields, arg, context):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.date_finish and record.date_start:
                date_start = datetime.strptime(
                    record.date_start, '%Y-%m-%d  %H:%M:%S')
                date_finish = datetime.strptime(
                    record.date_finish, '%Y-%m-%d  %H:%M:%S')
                days = (date_finish - date_start).days
                res[record.id] = days
            else:
                res[record.id] = 0
        return res

    def _get_total(self, cr, uid, ids, fields, arg, context):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            total_price = 0
            total_cost = 0
            if record.travel_ids:
                for travel in record.travel_ids:
                    total_price = total_price + travel.price
            if record.waybill_expense_ids:
                for travel in record.waybill_expense_ids:
                    total_cost = total_cost + travel.price_subtotal
            net = total_price - total_cost
            net_avg = 0
            if total_cost != 0:
                net_avg = ((total_price/total_cost) - 1) * 100
            print net_avg
            res[record.id] = {
                'total_price': total_price,
                'total_cost': total_cost,
                'net_avg': net_avg,
                'net': net,
            }
        return res

    def _get_price_cost_km(self, cr, uid, ids, fields, arg, context):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.distance != 0:
                price_km = record.total_price / record.distance
                cost_km = record.total_cost / record.distance
                net_km = price_km - cost_km
            else:
                price_km = 0
                cost_km = 0
                net_km = 0
            res[record.id] = {
                'price_km': price_km,
                'cost_km': cost_km,
                'net_km': net_km,
            }
        return res

    def _get_total_travel(self, cr, uid, ids, context=None):
        result = []
        for travel in self.pool.get('logistic.travel').browse(cr, uid, ids, context=context):
            if travel.price:
                result.append(travel.waybill_id.id)
        return result

    def _get_total_exp(self, cr, uid, ids, context=None):
        result = []
        for expense in self.pool.get('logistic.waybill_expense').browse(cr, uid, ids, context=context):
            if expense.price_subtotal:
                result.append(expense.waybill_id.id)
        return result

    _columns = {
        'days_range': fields.function(_get_days_range, type='integer', string='Days Range'),
        'total_price': fields.function(
            _get_total, type='float', string='Total Price',
            multi="total",
            store={
                'logistic.travel': (
                    _get_total_travel,
                    ['price'],
                    10),
                'logistic.waybill': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['travel_ids', 'state'],
                    10),
            }),
        'total_cost': fields.function(
            _get_total, type='float', string='Total Cost',
            multi="total",
            store={
                'logistic.waybill_expense': (
                    _get_total_exp,
                    ['price_unit', 'product_uom_qty'],
                    10),
                'logistic.waybill': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['waybill_expense_ids', 'state'],
                    10),
            }),
        'net': fields.function(
            _get_total, type='float', string='Net', multi="total",
            store={
                'logistic.travel': (
                    _get_total_travel,
                    ['price'],
                    10),
                'logistic.waybill_expense': (
                    _get_total_exp,
                    ['price_unit', 'product_uom_qty'],
                    10),
                'logistic.waybill': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['travel_ids', 'waybill_expense_ids', 'state'],
                    10)},
        ),
        'net_avg': fields.function(
            _get_total, type='float', string='Net %', multi="total",
            store={
                'logistic.travel': (
                    _get_total_travel,
                    ['price'],
                    10),
                'logistic.waybill_expense': (
                    _get_total_exp,
                    ['price_unit', 'product_uom_qty'],
                    10),
                'logistic.waybill': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['travel_ids', 'waybill_expense_ids', 'state'],
                    10)}, group_operator="avg"
        ),
        'price_km': fields.function(
            _get_price_cost_km, type='float', string='Price per km',
            multi="total_km",
            store={
                'logistic.waybill': (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['final_odometer', 'net', 'travel_ids', 'initial_odometer', 'state'],
                    10),
                'logistic.travel': (
                    _get_total_travel,
                    ['price'],
                    10),
                'logistic.waybill_expense': (
                    _get_total_exp,
                    ['price_unit', 'product_uom_qty'],
                    10)}, group_operator="avg"),
        'cost_km': fields.function(_get_price_cost_km, type='float', string='Cost per km', multi="total_km", store={
            'logistic.waybill': (
                lambda self, cr, uid, ids, c={}: ids,
                ['final_odometer', 'initial_odometer', 'net', 'waybill_expense_ids', 'state'],
                10),
            'logistic.travel': (
                _get_total_travel,
                ['price'],
                10),
            'logistic.waybill_expense': (
                _get_total_exp,
                ['price_unit', 'product_uom_qty'],
                10)}, group_operator="avg"),
        'net_km': fields.function(_get_price_cost_km, type='float', string='Net per km', multi="total_km", store={
            'logistic.waybill': (
                lambda self, cr, uid, ids, c={}: ids,
                ['net', 'waybill_expense_ids', 'travel_ids', 'final_odometer', 'initial_odometer', 'state'],
                10),
            'logistic.travel': (
                _get_total_travel,
                ['price'],
                10),
            'logistic.waybill_expense': (
                _get_total_exp,
                ['price_unit', 'product_uom_qty'],
                10)}, group_operator="avg"),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
