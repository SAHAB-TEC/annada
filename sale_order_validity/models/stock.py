# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _

from collections import Counter

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
from dateutil.relativedelta import relativedelta


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_lot_name(self):
        print("*** _get_lot_name *****", self._context.get('show_lots_text'))
        if self._context.get('show_lots_text'):
            l = self.env['ir.sequence'].next_by_code('stock.move.line') or 'lot'
            return l

    lot_name = fields.Char(default=_get_lot_name)

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


class StockLotDisplayName(models.Model):
    _inherit = 'stock.lot'

    def name_get(self):
        self.browse(self.ids).read(['name', 'expiration_date'])
        return [
            (template.id, '%s%s' % (template.name and '[%s] ' % template.name or '', template.expiration_date))
            for template in self]
