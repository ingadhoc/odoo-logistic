# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from datetime import datetime
from calendar import monthrange
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare


class travel(osv.osv):

    """"""

    _inherit = 'logistic.travel'

    def _get_days_range(self, cr, uid, ids, fields, arg, context):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.from_date and record.to_date:
                from_date = datetime.strptime(
                    record.from_date, '%Y-%m-%d  %H:%M:%S')
                to_date = datetime.strptime(
                    record.to_date, '%Y-%m-%d  %H:%M:%S')
                days = (to_date - from_date).days
                days_avg = days / monthrange(from_date.year, from_date.month)[1]

                res[record.id] = {
                    'days_range': days,
                    'days_range_avg': days_avg,
                }
            else:
                res[record.id] = {
                    'days_range': 0,
                    'days_range_avg': 0,
                }
        return res

    _columns = {
        'days_range': fields.function(_get_days_range, type='integer',
                                      string='Days Range', multi="cal_days", store=True),
        'days_range_avg': fields.function(_get_days_range, type='float',
                                          string='Days Range Average', multi="cal_days", store=True),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
