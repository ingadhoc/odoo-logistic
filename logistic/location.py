# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class location(models.Model):

    """"""

    _name = 'logistic.location'
    _description = 'location'

    name = fields.Char(string='Name', required=True)
