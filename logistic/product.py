# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class product(models.Model):

    """"""
    _inherit = 'product.product'

    location_from_id = fields.Many2one(
        'logistic.location',
        string='Location From'
    )
    location_to_id = fields.Many2one(
        'logistic.location',
        string='Location To'
    )
    service_subtype = fields.Selection(
        [('travel', 'Travel'), ('maintenance', 'Maintenance'),
         ('document', 'Document'), ('other', 'Other')],
        string='Subtype',
        default='other'
    )
    default_range = fields.Float(
        string='Default Range'
    )
    range_unit = fields.Selection(
        [('kilometers', 'Kilometers'), ('miles', 'Miles')],
        string='Range Unit',
        default='kilometers'
    )
    default_validity_days = fields.Integer(
        string='Default Validity Days'
    )
    default_warning_days = fields.Integer(
        string='Default Warning Days'
    )
    default_warning_range = fields.Float(
        string='Default Warning Range'
    )
    is_fuel = fields.Boolean(
        string='Is Fuel?'
    )
