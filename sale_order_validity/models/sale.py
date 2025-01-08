# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_expire_id = fields.Many2one(comodel_name="stock.lot", string="Lot/Expire", required=False, )
    stock_lot_ids = fields.Many2many(comodel_name="stock.lot", string="Lots", compute="_comp_lot")
    before_disc = fields.Float(string="Before Disc", required=False, compute="_comp_total")

    @api.onchange('product_uom_qty', 'price_unit')
    def _comp_total(self):
        for rec in self:
            rec.before_disc = rec.product_uom_qty * rec.price_unit

    @api.depends('product_id')
    def _comp_lot(self):
        for rec in self:
            if rec.product_id:
                types = self.env['stock.lot'].search(
                    [('product_id', '=', rec.product_id.id)]).ids or []
                print("types ==. ", types)

                rec.stock_lot_ids = [(6, 0, types)]
            else:
                rec.stock_lot_ids = False


