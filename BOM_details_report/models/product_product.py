from odoo import api, fields, models, _



class ProductProduct(models.Model):
    _inherit = "product.product"

    shortage = fields.Float(string="Shortage")
    surplus = fields.Float(string="Surplus")
    target_amount = fields.Float(string="Target Amount")
    amount_state = fields.Selection([
        ('normal', 'Normal'),
        ('shortage', 'Shortage'),
        ('surplus', 'Surplus'),
    ], string='Amount State', default='normal', store=True,)
    available_qty = fields.Float(string="Available Quantity", compute='_compute_available_qty', store=True)

    @api.depends('qty_available', 'purchased_product_qty')
    def _compute_available_qty(self):
        for record in self:
            record.available_qty = record.qty_available

    # def _compute_amount_state(self):
    #     for record in self:
    #         if record.shortage > 0:
    #             record.amount_state = 'shortage'
    #         elif record.surplus > 0:
    #             record.amount_state = 'surplus'
    #         else:
    #             record.amount_state = 'normal'
