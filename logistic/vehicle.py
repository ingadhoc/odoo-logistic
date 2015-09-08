# -*- coding: utf-8 -*-
##############################################################################
#
#    Logistic
#    Copyright (C) 2014 No author.
#    No email
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

class vehicle(osv.osv):
    """"""
    
    _name = 'fleet.vehicle'
    _inherits = {  }
    _inherit = [ 'fleet.vehicle' ]

    _columns = {
        'type': fields.selection([(u'car', u'Car'), (u'tractor', u'Tractor'), (u'wagon', u'Wagon')], string='Type'),
        'wagon_id': fields.many2one('fleet.vehicle', string='Wagon', context={'default_type':'wagon'}, domain=[('type','=','wagon')]),
        'driver_id': fields.many2one('res.partner', string='Driver', context={'default_is_driver':True}, domain=[('is_driver','=',True)]),
        'default_validity': fields.integer(string='default_validity'),
        'default_kilometers': fields.integer(string='default_kilometers'),
        'year': fields.integer(string='Year'),
        'motor_sn': fields.char(string='Motor Number'),
    }

    _defaults = {
    }


    _constraints = [
    ]




vehicle()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
