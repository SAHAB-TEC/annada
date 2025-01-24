from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class BomWizard(models.TransientModel):
    _name = 'mrp.bom.wizard'
    _description = 'Bill of Material Wizard'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(stringg="Quantity", required=True, default=0.0)
    components = fields.Many2many('product.product', string="Components", compute='_compute_components', store=True)

    @api.depends('product_id', 'quantity')
    def _compute_components(self):
        for record in self:
            # Default assignments
            record.components = [(6, 0, [])]
            if not record.product_id:
                continue

            # Find BOM and components
            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)], limit=1)
            if not bom:
                _logger.info(f"No BOM found for Product: {record.product_id.name}")
                continue

            bom_lines = bom.bom_line_ids
            components = bom_lines.mapped('product_id')
            record.components = [(6, 0, components.ids)]

            total_shortage =0.0
            total_surplus = 0.0

            for line in bom_lines:
                target_amount = line.product_qty * record.quantity
                available_qty = line.product_id.qty_available + line.product_id.purchased_product_qty

                if available_qty > target_amount:
                    surplus = available_qty - target_amount
                    shortage = 0.0
                else:
                    surplus = 0.0
                    shortage = target_amount - available_qty

                total_shortage = shortage
                total_surplus = surplus
                line.product_id.shortage = total_shortage
                line.product_id.surplus = total_surplus
                # record.target_amount = line.product_qty * record.quantity

   
    def generate_report(self):
        
        return self.env.ref('mrp_BOM_details_report.action_bom_report').report_action(self)

    def view_report_html(self):

        return self.env.ref('mrp_BOM_details_report.action_bom_report_html').report_action(self)


class ProductProduct(models.Model):
    _inherit = "product.product"

    shortage = fields.Float(string="Shortage")
    surplus = fields.Float(string="Surplus")
    target_amount = fields.Float(string="Target Amount")
