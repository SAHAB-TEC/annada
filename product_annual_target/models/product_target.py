from odoo import models, fields, api

class ProductTarget(models.Model):
    _name = 'product.target'
    _description = 'Product Target'

    # name = fields.Char(string="Year", required=True, help="Year (e.g., 2020, 2023)")
    name = fields.Selection([
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
        ('2024', '2024'),
        ('2025', '2025'),
        ('2026', '2026'),
        ('2027', '2027'),
        ('2028', '2028'),
        ('2029', '2029'),
        ('2030', '2030'),
    ], string="Year", required=True, help="Year (e.g., 2020, 2023)")
    # uom_id = fields.Many2one('uom.uom', string="Unit of Measure", required=True, help="Unit of measure for the target amount")
    # target_amount = fields.Float(string="Target Amount", required=True, help="Target amount for the specified year")
    product_template_id = fields.Many2one(
        'product.template',
        string="Product Template",
        ondelete='cascade',
        help="Product associated with this target" ,invisible="1"
    )
    target_amount = fields.Float(
        string="Target Quantity",
        digits='Product Unit of Measure', default=0.0,
        store=True, readonly=False, required=True, precompute=True)

    product_uom_category_id = fields.Many2one(related='product_template_id.uom_id.category_id', depends=['product_template_id'])
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute="_compute_product_uom",
        store=True, readonly=False, precompute=True, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")



    @api.depends('product_template_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_template_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_template_id.uom_id