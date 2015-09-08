# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################


from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _


class waybill(models.Model):

    """"""

    _inherit = 'logistic.waybill'

    def _get_initial_odometer(self, cr, uid, ids, initial_odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.initial_odometer_id:
                res[record.id] = record.initial_odometer_id.value
        return res

    def _set_initial_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).tractor_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(
            cr, uid, data, context=context)
        return self.write(cr, uid, id, {'initial_odometer_id': odometer_id}, context=context)

    @api.one
    def _get_final_odometer(self):
        if self.final_odometer_id:
            self.final_odometer = self.final_odometer_id.value

    def _set_final_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).tractor_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(
            cr, uid, data, context=context)
        return self.write(cr, uid, id, {'final_odometer_id': odometer_id}, context=context)

    # WAGON

    def _get_wagon_initial_odometer(self):
        if self.wagon_initial_odometer_id:
            self.wagon_initial_odometer = self.wagon_initial_odometer_id.value

    def _set_wagon_initial_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).wagon_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(
            cr, uid, data, context=context)
        return self.write(cr, uid, id, {'wagon_initial_odometer_id': odometer_id}, context=context)

    @api.one
    def _get_wagon_final_odometer(self):
        if self.wagon_final_odometer_id:
            self.wagon_final_odometer = self.wagon_final_odometer_id.value

    def _set_wagon_final_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if not value:
            # raise except_orm(_('Operation not allowed!'), _('Emptying the odometer value of a vehicle is not allowed.'))
            return True
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = self.browse(cr, uid, id, context=context).wagon_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id}
        odometer_id = self.pool.get('fleet.vehicle.odometer').create(
            cr, uid, data, context=context)
        return self.write(cr, uid, id, {'wagon_final_odometer_id': odometer_id}, context=context)

    @api.one
    @api.depends('initial_odometer', 'final_odometer')
    def _get_distance(self):
        if self.initial_odometer and self.final_odometer:
            self.distance = self.final_odometer - \
                self.initial_odometer

    def _get_amounts(self):
        # for record in self.browse(cr, uid, ids, context=context):
        self.driver_total = False
        if self.driver_unit_price and self.distance:
            self.driver_total = self.driver_unit_price * self.distance

    @api.one
    @api.depends(
        'consumption',
        'initial_liters',
        'final_liters',
        'waybill_expense_ids',
        'waybill_expense_ids.product_uom_qty',
        'state',
        'initial_odometer',
        'final_odometer'
    )
    def _get_fuel_data(self):
        expense_obj = self.env['logistic.waybill_expense']
        charged_liters = 0.0
        fuel_charge_ids = expense_obj.search([(
            'waybill_id', '=', self.id), ('product_id.is_fuel', '=', True)])
        for fuel_charge in expense_obj.browse(fuel_charge_ids):
            charged_liters += fuel_charge.product_uom_qty
        consumed_liters = self.initial_liters + \
            charged_liters - self.final_liters
        if self.distance != 0:
            consumption = consumed_liters / self.distance
        else:
            consumption = 0

        self.charged_liters = charged_liters
        self.consumed_liters = consumed_liters
        self.consumption = consumption
        self.consumption_copy = consumption

    charged_liters = fields.Float(
        string='Charged', compute='_get_fuel_data', multi="fuel_data")
    consumed_liters = fields.Float(
        string='Consumed', compute='_get_fuel_data', multi="fuel_data")
    consumption = fields.Float(
        string='Consumption (l/km)', compute='_get_fuel_data', multi="fuel_data")
    consumption_copy = fields.Float(
        string='Consumption (l/km)',
        compute='_get_fuel_data',
        multi="fuel_data", store=True, group_operator="avg")
    initial_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Initial Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    initial_odometer = fields.Float(
        fnct_inv=_set_initial_odometer,
        compute='_get_initial_odometer',
        string='Initial Odometer',
        readonly=True, states={'active': [('readonly', False)]})
    final_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Final Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    final_odometer = fields.Float(
        fnct_inv=_set_final_odometer,
        compute='_get_final_odometer',
        string='Final Odometer',
        readonly=True, states={'active': [('readonly', False)]})
    distance = fields.Float(
        compute='_get_distance', string='Distance', store=True)
    driver_total = fields.Float(
        compute='_get_amounts', string='Driver Total', multi="_get_amounts")
    wagon_initial_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Initial Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    wagon_initial_odometer = fields.Float(
        fnct_inv=_set_wagon_initial_odometer,
        compute='_get_wagon_initial_odometer',
        string='Initial Odometer', readonly=True,
        states={'active': [('readonly', False)]})
    wagon_final_odometer_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Final Odometer',
        help='Odometer measure of the vehicle at the moment of this log',
        readonly=True, states={'active': [('readonly', False)]})
    wagon_final_odometer = fields.Float(
        fnct_inv=_set_wagon_final_odometer,
        compute='_get_wagon_final_odometer',
        string='Final Odometer', readonly=True,
        states={'active': [('readonly', False)]})
    tractor_status = fields.Selection(
        related='tractor_id.requirement_state', string='Tractor Status')
    wagon_status = fields.Selection(
        related='wagon_id.requirement_state', string='Wagon Status')
    driver_status = fields.Selection(
        related='driver_id.requirement_state', string='Driver Status')

    def on_change_tractor_final_odometer(self, cr, uid, ids, initial_odometer, final_odometer, wagon_initial_odometer, context=None):
        v = {}
        if initial_odometer and final_odometer and wagon_initial_odometer:
            v['wagon_final_odometer'] = final_odometer - \
                initial_odometer + wagon_initial_odometer
        return {'value': v}

    def on_change_wagon(self, cr, uid, ids, wagon_id, context=None):
        v = {}
        if wagon_id:
            wagon = self.pool.get('fleet.vehicle').browse(
                cr, uid, wagon_id, context=context)
            v['wagon_initial_odometer'] = wagon.odometer
        else:
            v['wagon_initial_odometer'] = False
        return {'value': v}

    def on_change_driver(self, cr, uid, ids, driver_id, context=None):
        v = {}
        if driver_id:
            driver = self.pool.get('res.partner').browse(
                cr, uid, driver_id, context=context)
            v['driver_product_id'] = driver.driver_product_id.id
        else:
            v['driver_product_id'] = False
        return {'value': v}

    def on_change_product(self, cr, uid, ids, product_id, context=None):
        v = {}
        if product_id:
            product = self.pool.get('product.product').browse(
                cr, uid, product_id, context=context)
            v['driver_unit_price'] = product.list_price
        else:
            v['driver_unit_price'] = False
        return {'value': v}

    def on_change_tractor(self, cr, uid, ids, tractor_id, context=None):
        v = {}
        if tractor_id:
            vehicle = self.pool.get('fleet.vehicle').browse(
                cr, uid, tractor_id, context=context)
            v['initial_odometer'] = vehicle.odometer
            if vehicle.wagon_id.id:
                v['wagon_id'] = vehicle.wagon_id.id
            else:
                v['wagon_id'] = False
                v['wagon_initial_odometer'] = False
            if vehicle.driver_id.id:
                v['driver_id'] = vehicle.driver_id.id
            else:
                v['driver_id'] = False
        else:
            v['initial_odometer'] = False
            v['wagon_initial_odometer'] = False
            v['wagon_id'] = False
            v['driver_id'] = False
        return {'value': v}

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(
                cr, uid, 'logistic.waybill') or '/'
        return super(waybill, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'date': fields.date.context_today(self, cr, uid, context=context),
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
