# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _

from collections import Counter

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
import datetime


class StockLotDisplayName(models.Model):
    _inherit = 'stock.lot'
    _rec_name = 'display_name_1'

    display_name_1 = fields.Char(string='Display Name', compute='_compute_display_name_1', store=True)

    @api.depends('name', 'expiration_date')
    def _compute_display_name_1(self):
        for rec in self:
            rec.display_name_1 = '%s%s' % (rec.name and '[%s] ' % rec.name or '', rec.expiration_date)

    @api.depends('name', 'expiration_date')
    def name_get(self):
        """
            to use retrieving the name, combination of `hotel name & room name`
        """
        res = []
        for rec in self:
            # name = [name] expiration_date
            name = '%s%s' % (rec.name and '[%s] ' % rec.name or '', rec.expiration_date)
            res.append((rec.id, name))
        return res

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_lot_name(self):
        print("*** _get_lot_name *****", self._context.get('show_lots_text'))
        # if self._context.get('show_lots_text'):
        l = self.env['ir.sequence'].next_by_code('stock.move.line') or 'lot'
        return l

    lot_name = fields.Char(default=_get_lot_name)

    @api.depends('product_id', 'lot_id.expiration_date', 'picking_id.scheduled_date')
    def _compute_expiration_date(self):
        for move_line in self:

            exp_date = move_line.move_id.purchase_line_id.expired_date or False
            if exp_date:
                move_line.expiration_date = exp_date
            elif move_line.lot_id.expiration_date:
                move_line.expiration_date = move_line.lot_id.expiration_date
            elif move_line.picking_type_use_create_lots:
                if move_line.product_id.use_expiration_date:
                    if not move_line.expiration_date:
                        from_date = move_line.picking_id.scheduled_date or fields.Datetime.today()
                        move_line.expiration_date = from_date + datetime.timedelta(days=move_line.product_id.expiration_time)
                else:
                    move_line.expiration_date = False

    def _get_value_production_lot(self):
        res = super()._get_value_production_lot()
        exp_date = self.move_id.purchase_line_id.expired_date or False
        if exp_date:
            alert_date = exp_date + relativedelta(months=-6)
        else:
            alert_date = False
        if exp_date:
            use_date = exp_date + relativedelta(days=-1)
        else:
            use_date = False

        print("*** alert_date =>> ", alert_date)
        print("*** exp_date =>> ", exp_date)
        if exp_date:
            res.update({
                'expiration_date': exp_date,
                'use_date': use_date,
                'removal_date': exp_date,
                'alert_date': alert_date,
            })
        return res


