# -*- coding: utf-8 -*-
##############################################################################
#
#    Ingenieria ADHOC - ADHOC SA
#    https://launchpad.net/~ingenieria-adhoc
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
from datetime import datetime
from openerp.osv import osv, fields
from openerp.osv.orm import except_orm
from openerp.tools.translate import _


class waybill(osv.osv):

    """"""

    _inherit = 'logistic.waybill'

    def _get_days_range(self, cr, uid, ids, fields, arg, context):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.date_finish and record.date_start:
                date_start = datetime.strptime(record.date_start, '%Y-%m-%d  %H:%M:%S')
                date_finish = datetime.strptime(record.date_finish, '%Y-%m-%d  %H:%M:%S')
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
            res[record.id] = {
                'total_price': total_price,
                'total_cost': total_cost,
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

    _columns = {
        'days_range': fields.function(_get_days_range, type='integer', string='Days Range'),
        'total_price': fields.function(_get_total, type='float', string='Total Price', multi="total",store=True),
        'total_cost': fields.function(_get_total, type='float', string='Total Cost', multi="total",store=True),
        'net': fields.function(_get_total, type='float', string='Net', multi="total",store=True),
        'price_km': fields.function(_get_price_cost_km, type='float', string='Price per km', multi="total_km", store=True),
        'cost_km': fields.function(_get_price_cost_km, type='float', string='Cost per km', multi="total_km", store=True),
        'net_km': fields.function(_get_price_cost_km, type='float', string='Net per km', multi="total_km", store=True),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
