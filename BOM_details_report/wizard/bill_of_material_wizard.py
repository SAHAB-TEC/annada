from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class BomWizard(models.TransientModel):
    _name = 'bom.wizard'
    _description = 'Bill of Material Wizard'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    # quantity = fields.Float(string="Quantity", required=True, default=0.0)
    quantity = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=0.0,
        store=True, readonly=False, required=True, precompute=True)

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
                target_amount = line.product_qty / bom.product_qty * record.quantity
                available_qty = line.product_id.qty_available + line.product_id.pending_po_product_qty

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
        return self.env.ref('BOM_details_report.action_bom_report').report_action(self)

    def view_report_html(self):

        return self.env.ref('BOM_details_report.action_bom_report_html').report_action(self)
