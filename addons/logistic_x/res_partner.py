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
from openerp import netsvc
from openerp.osv import osv, fields

class res_partner(osv.osv):
    """"""
    
    _inherit = 'res.partner'

    _requirement_states = [
        # State machine: requirement_basic
        ('ok','OK'),
        ('next_to_renew','Next To Renew'),
        ('need_renew','Need Renew'),
    ]

    def _get_requirement_state(self, cr, uid, ids, initial_odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        requirement_obj = self.pool['logistic.requirement']
        for record_id in ids:
            state = 'ok'
            if requirement_obj.search(cr, uid, [('partner_id','=',record_id),('state','=','need_renew')], context=context):
                state = 'need_renew'
            elif requirement_obj.search(cr, uid, [('partner_id','=',record_id),('state','=','next_to_renew')], context=context):      
                state = 'next_to_renew'
            res[record_id] = state
        return res

    _columns = {
        'document_ids': fields.one2many('logistic.requirement', 'partner_id',
            context={'default_type':'document'},
            domain=[('type', '=', 'document'),('state','not in',['renewed','cancelled'])],
            string='Documents',),
        'requirement_state': fields.function(_get_requirement_state, type='selection', selection=_requirement_states, string="Requirements State"),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
