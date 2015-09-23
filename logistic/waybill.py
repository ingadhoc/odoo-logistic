# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################


from openerp import models, fields, api
from openerp import netsvc
from openerp.exceptions import Warning
from openerp.tools.translate import _


class waybill(models.Model):

    """"""
    _name = 'logistic.waybill'
    _inherit = ['ir.needaction_mixin', 'mail.thread']

    _states_ = [
        # State machine: weybill_basic
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    _track = {
        'state': {
            'logistic.waybill_active': (
                lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active'),
            'logistic.waybill_closed': (
                lambda self, cr, uid, obj, ctx=None: obj['state'] == 'closed'),
            'logistic.waybill_cancelled': (
                lambda self, cr, uid, obj, ctx=None:
                obj['state'] == 'cancelled'),
        },
    }

    @api.one
    def _get_currency(self):
        self.currency_id = self.env['res.users'].browse(
            self._uid).company_id.currency_id.id

    name = fields.Char(
        string='Name',
        readonly=True
        )
    reference = fields.Char(
        string='Reference'
        )
    date = fields.Date(
        string='Date',
        readonly=True,
        required=True,
        states={'active': [('readonly', False)]},
        default=fields.date.today()
        )
    tractor_id = fields.Many2one(
        'fleet.vehicle',
        string='Tractor',
        readonly=True,
        required=True,
        states={'active': [('readonly', False)]},
        context={'default_type': 'tractor'},
        domain=[('type', '=', 'tractor')],
        on_change='on_change_vehicle(vehicle_id, context)'
        )
    wagon_id = fields.Many2one(
        'fleet.vehicle',
        string='Wagon',
        readonly=True,
        required=True,
        states={'active': [('readonly', False)]},
        context={'default_type': 'wagon'},
        domain=[('type', '=', 'wagon')]
        )
    driver_id = fields.Many2one(
        'res.partner',
        string='Driver',
        readonly=True,
        required=True,
        states={'active': [('readonly', False)]},
        context={'default_is_driver': True},
        domain=[('is_driver', '=', True)]
        )
    odometer_unit = fields.Selection(
        [('kilometers', 'Kilometers'), ('miles', 'Miles')],
        string='Odometer Unit',
        readonly=True,
        required=True,
        states={'active': [('readonly', False)]},
        default='kilometers'
        )
    note = fields.Text(
        string='Note'
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True
        )
    date_start = fields.Datetime(
        string='Date Start',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    date_finish = fields.Datetime(
        string='Date Finish',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    driver_product_id = fields.Many2one(
        'product.product',
        string='Driver Product',
        readonly=True,
        states={'active': [('readonly', False)]},
        context={'default_type': 'service',
                 'default_service_subtype': 'other'},
        domain=[('type', '=', 'service'), ('service_subtype', '=', 'other')]
        )
    driver_unit_price = fields.Float(
        string='Driver Unit Price',
        states={'active': [('readonly', False)]}
        )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=_get_currency
        )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda s: s.env['res.company']._company_default_get(
            'logistic.waybill')
        )
    initial_liters = fields.Float(
        string='Initial Liters',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    final_liters = fields.Float(
        string='Final Liters',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    state = fields.Selection(
        _states_,
        "State",
        default='active'
        )
    travel_ids = fields.One2many(
        'logistic.travel',
        'waybill_id',
        string='Travels',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    waybill_expense_ids = fields.One2many(
        'logistic.waybill_expense',
        'waybill_id',
        string='Expenses',
        readonly=True, states={'active': [('readonly', False)]}
        )
    driver_payment_id = fields.Many2one(
        'logistic.waybill_driver_payment',
        string='Driver Payment', readonly=True
        )
    charged_liters = fields.Float(
        string=_('Charged'),
        compute='_get_fuel_data'
        )
    consumed_liters = fields.Float(
        string=_('Consumed Liters'),
        compute='_get_fuel_data'
        )
    consumption = fields.Float(
        string='Consumption (l/km)',
        compute='_get_fuel_data',
        store=True,
        )
    consumption_copy = fields.Float(
        related='consumption',
        string=_('Consumption')
        )
    initial_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer',
        string='Initial Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    initial_odometer = fields.Float(
        inverse='_set_initial_odometer',
        compute='_get_initial_odometer',
        string=_('Initial Odometer'),
        readonly=True,
        required=True,
        states={'active': [('readonly', False)]}
        )
    final_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Final Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    final_odometer = fields.Float(
        inverse='_set_final_odometer',
        compute='_get_final_odometer',
        string='Final Odometer',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    distance = fields.Float(
        string=_('Distance'),
        compute='_get_distance'
        )
    driver_total = fields.Float(
        string=_('Driver Total'),
        compute='_get_amounts'
        )
    wagon_initial_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Initial Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True,
        states={'active': [('readonly', False)]}
        )
    wagon_initial_odometer = fields.Float(
        inverse='_set_wagon_initial_odometer',
        compute='_get_wagon_initial_odometer',
        string='Initial Odometer', readonly=True,
        states={'active': [('readonly', False)]}
        )
    wagon_final_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Final Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    wagon_final_odometer = fields.Float(
        inverse='_set_wagon_final_odometer',
        compute='_get_wagon_final_odometer',
        string='Final Odometer', readonly=True,
        states={'active': [('readonly', False)]}
        )
    tractor_status = fields.Selection(
        related='tractor_id.requirement_state',
        string='Tractor Status'
        )
    wagon_status = fields.Selection(
        related='wagon_id.requirement_state',
        string='Wagon Status'
        )
    driver_status = fields.Selection(
        related='driver_id.requirement_state',
        string='Driver Status'
        )

    @api.one
    @api.depends('initial_odometer', 'final_odometer')
    def _get_distance(self):
        if self.initial_odometer and self.final_odometer:
            self.distance = self.final_odometer - self.initial_odometer

    @api.one
    @api.onchange(
        'final_odometer', 'initial_odometer', 'wagon_initial_odometer')
    def on_change_tractor_final_odometer(self):
        if (
                self.initial_odometer and
                self.final_odometer and
                self.wagon_initial_odometer
                ):
            self.wagon_final_odometer = self.final_odometer - \
                self.initial_odometer + self.wagon_initial_odometer

    @api.one
    @api.onchange('wagon_id')
    def on_change_wagon(self):
        self.wagon_initial_odometer = self.wagon_id.odometer

    @api.one
    @api.onchange('driver_id')
    def on_change_driver(self):
        self.driver_product_id = self.driver_id.driver_product_id.id

    @api.one
    @api.onchange('driver_product_id')
    def on_change_product(self):
        self.driver_unit_price = self.driver_product_id.list_price

    @api.one
    @api.onchange('tractor_id')
    def on_change_tractor(self):
        self.initial_odometer = self.tractor_id.odometer
        if self.tractor_id.wagon_id.id:
            self.wagon_id = self.tractor_id.wagon_id.id
        else:
            self.wagon_id = False
            self.wagon_initial_odometer = False
        if self.tractor_id.driver_id.id:
            self.driver_id = self.tractor_id.driver_id.id
        else:
            self.driver_id = False

    def action_wfk_set_active(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'active'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'logistic.waybill', obj_id, cr)
            wf_service.trg_create(uid, 'logistic.waybill', obj_id, cr)
        return True

    @api.one
    def _get_initial_odometer(self):
        if self.initial_odometer_id:
            self.initial_odometer = self.initial_odometer_id.value

    @api.one
    def _set_initial_odometer(self):
        if not self.initial_odometer:
            return True
        date = self.date
        if not self.date:
            date = fields.date.today()
        data = {'value': self.initial_odometer, 'date': date,
                'vehicle_id': self.tractor_id.id}
        odometer_id = self.env['fleet.vehicle.odometer'].create(data)
        self.initial_odometer_id = odometer_id

    @api.one
    def _get_final_odometer(self):
        if self.final_odometer_id:
            self.final_odometer = self.final_odometer_id.value

    @api.one
    def _set_final_odometer(self):
        if not self.final_odometer:
            return True
        date = self.date
        if not self.date:
            date = fields.date.today()
        data = {'value': self.final_odometer, 'date': date,
                'vehicle_id': self.tractor_id.id}
        odometer_id = self.env['fleet.vehicle.odometer'].create(data)
        self.final_odometer_id = odometer_id

    @api.one
    def _get_wagon_initial_odometer(self):
        if self.wagon_initial_odometer_id:
            self.wagon_initial_odometer = self.wagon_initial_odometer_id.value

    @api.one
    def _set_wagon_initial_odometer(self):
        if not self.wagon_initial_odometer:
            return True
        date = self.date
        if not self.date:
            date = fields.date.today()
        data = {'value': self.wagon_initial_odometer, 'date': date,
                'vehicle_id': self.wagon_id.id}
        odometer_id = self.env['fleet.vehicle.odometer'].create(data)
        self.wagon_initial_odometer_id = odometer_id

    @api.one
    def _get_wagon_final_odometer(self):
        if self.wagon_final_odometer_id:
            self.wagon_final_odometer = self.wagon_final_odometer_id.value

    @api.one
    def _set_wagon_final_odometer(self):
        if not self.wagon_final_odometer:
            return True
        date = self.date
        if not self.date:
            date = fields.date.today()
        data = {'value': self.wagon_final_odometer, 'date': date,
                'vehicle_id': self.wagon_id.id}
        odometer_id = self.env['fleet.vehicle.odometer'].create(data)
        self.wagon_final_odometer_id = odometer_id

    def _get_amounts(self):
        self.driver_total = False
        if self.driver_unit_price and self.distance:
            self.driver_total = self.driver_unit_price * self.distance

    @api.one
    @api.depends(
        'distance',
        'initial_liters',
        'final_liters',
        'waybill_expense_ids.product_id.is_fuel',
        'waybill_expense_ids.product_uom_qty')
    def _get_fuel_data(self):
        charged_liters = sum(self.mapped('waybill_expense_ids').filtered(
            lambda x: x.product_id.is_fuel).mapped('product_uom_qty'))
        consumed_liters = self.initial_liters + \
            charged_liters - self.final_liters
        if self.distance != 0:
            consumption = consumed_liters / self.distance
        else:
            consumption = 0
        self.charged_liters = charged_liters
        self.consumed_liters = consumed_liters
        self.consumption = consumption

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(
                cr, uid, 'logistic.waybill') or '/'
        return super(waybill, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'date': fields.date_today(),
            'travel_ids': [],
            'waybill_expense_ids': [],
            'initial_odometer_id': False,
            'initial_odometer': self.browse(cr, uid, id, context=context).tractor_id.odometer,
            'final_odometer_id': False,
            'wagon_initial_odometer_id': False,
            'wagon_initial_odometer': self.browse(cr, uid, id, context=context).wagon_id.odometer,
            'wagon_final_odometer_id': False,
            'name': self.pool.get('ir.sequence').get(cr, uid, 'logistic.waybill'),
        })
        return super(waybill, self).copy(cr, uid, id, default, context=context)

    def check_closure(self, cr, uid, ids, context=None):
        travel_obj = self.pool['logistic.travel']
        for record in self.browse(cr, uid, ids, context=context):
            if not record.final_odometer or record.initial_odometer >= record.final_odometer:
                raise Warning(
                    _('Error!'), _('Tractor Final odometer must be greater than initial odometer!'))
            if not record.wagon_final_odometer or record.wagon_initial_odometer >= record.wagon_final_odometer:
                raise Warning(
                    _('Error!'), _('Wagon Final odometer must be greater than initial odometer!'))
            if not record.date_start:
                travel_ids = travel_obj.search(
                    cr, uid, [('waybill_id', '=', record.id)], order='from_date', context=context)
                if travel_ids and not record.date_start:
                    date_start = travel_obj.browse(
                        cr, uid, travel_ids[0], context=context).from_date
                    self.write(
                        cr, uid, [record.id], {'date_start': date_start}, context=context)
            if not record.date_finish:
                travel_ids = travel_obj.search(
                    cr, uid, [('waybill_id', '=', record.id)], order='to_date desc', context=context)
                if travel_ids and not record.date_finish:
                    date_finish = travel_obj.browse(
                        cr, uid, travel_ids[0], context=context).to_date
                    self.write(
                        cr, uid, [record.id], {'date_finish': date_finish}, context=context)
