# -*- encoding: UTF-8 -*-
from email.policy import default

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_expire_id = fields.Many2one(comodel_name="stock.lot", string="Lot/Expire", required=False, compute="_comp_lot", store=True, readonly=False)
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
                    [('product_id', '=', rec.product_id.id), ('product_qty', '>', 0)])
                if types and len(types) > 0:
                    rec.stock_lot_ids = [(6, 0, types.ids)]
                    rec.lot_expire_id = types.ids[0]
                else:
                    rec.stock_lot_ids = False
                    rec.lot_expire_id = False
            else:
                rec.stock_lot_ids = False
                rec.lot_expire_id = False

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # action confirm
    def action_confirm(self):
        self.ensure_one()

        if self.delegate_sale_id:
            max_sale_amount = self.delegate_sale_id.max_sale_amount
            remain_amount = self.delegate_sale_id.remaining_total
            if self.amount_total + remain_amount > max_sale_amount:
                raise UserError(
                    _("You can not confirm this order because the amount is greater than the maximum amount allowed"))
        res = super(SaleOrder, self).action_confirm()
        return res
