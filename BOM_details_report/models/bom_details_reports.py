# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BomDetailsReports(models.Model):
    _name = 'bom.details.reports'
    _description = _('BomDetailsReports')
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    bom_id = fields.Many2one('mrp.bom', string="BOM", compute='_compute_line_ids', store=True)

    quantity = fields.Float(string="Quantity", required=True, digits='Product Unit of Measure', default=0.0, compute="_compute_quantity", readonly=False, store=True)

    @api.depends('product_id')
    def _compute_quantity(self):
        for record in self:
            if not record.product_id:
                continue

            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)], limit=1)
            if not bom:
                _logger.info(f"No BOM found for Product: {record.product_id.name}")
                continue
            record.quantity = bom.product_qty


    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", help="Unit of measure for the quantity",
                             readonly=True, related="bom_id.product_uom_id")
    components = fields.Many2many('product.product', string="Components", store=True)

    line_ids = fields.One2many('bom.details.reports.lines', 'bom_id', string="Lines", compute='_compute_line_ids', store=True)

    @api.depends('product_id', 'quantity')
    def _compute_line_ids(self):
        for record in self:
            record.line_ids = [(6, 0, [])]
            if not record.product_id:
                continue

            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)], limit=1)
            if not bom:
                _logger.info(f"No BOM found for Product: {record.product_id.name}")
                continue
            # record.quantity = bom.product_qty
            record.bom_id = bom.id
            record.uom_id = bom.product_uom_id.id

            bom_lines = bom.bom_line_ids
            line_ids = [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id,
                'secondary_product_uom_id': line.product_uom_id.id,
                'parent_qty': record.quantity,
                'product_qty': line.product_qty / bom.product_qty * record.quantity,
                'bom_product_qty': bom.product_qty,
                'target_amount': line.product_id.target_amount,
                'amount_state': line.product_id.amount_state,
                'available_qty': line.product_id.qty_available,
            }) for line in bom_lines]

            record.write({'line_ids': line_ids})

    def action_print(self):
        return self.env.ref('BOM_details_report.action_bom_report').report_action(self)

# lines
class BomDetailsReportsLines(models.Model):
    _name = 'bom.details.reports.lines'
    _description = _('BomDetailsReportsLines')

    bom_id = fields.Many2one('bom.details.reports', string="Bom")
    product_id = fields.Many2one('product.product', string="Product")
    product_qty = fields.Float(string="Quantity",
                               digits='Product Unit of Measure', default=1.0,
                               store=True, readonly=False, required=True)
    bom_product_qty = fields.Float(string="BOM Quantity",
                                   digits='Product Unit of Measure', default=1.0,
                                   store=True, readonly=False, required=True)
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        store=True, readonly=False, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    shortage = fields.Float(string="Shortage", readonly=True)
    surplus = fields.Float(string="Surplus", readonly=True)
    target_amount = fields.Float(string="Target Amount", compute='_compute_target_amount', store=True, readonly=True)
    parent_qty = fields.Float(string="Parent Quantity", related='bom_id.quantity', readonly=True)
    pending_po_product_qty = fields.Float(compute='_compute_available_qty', string='Pending Purchased', store=True, readonly=True)

    amount_state = fields.Selection([
        ('normal', 'Normal'),
        ('shortage', 'Shortage'),
        ('surplus', 'Surplus'),
    ], string='Amount State', default='normal', store=True, compute='_compute_amount_state')
    available_qty = fields.Float(string="Available Quantity", compute='_compute_available_qty', store=True)
    secondary_uom_ids = fields.Many2many('uom.uom',
                                         string="Secondary Uom Ids",
                                            compute='_compute_secondary_product_uom',
                                         help="For fetching all the secondary"
                                              " uom's")
    secondary_product_uom_id = fields.Many2one(
        'uom.uom', string='Secondary UoM',
        store=True, readonly=False,
        help="Select the Secondary Uom",
        domain="[('id', 'in', secondary_uom_ids)]")
    secondary_product_uom_qty = fields.Float(string='Secondary Quantity',
                                             help="Select the Secondary Uom "
                                                  "Quantity", default=1, compute='_compute_secondary_product_qty')
    is_secondary_readonly = fields.Boolean(string="Is Secondary Uom",
                                           help="The field to check whether"
                                                " the selected uom is"
                                                " secondary and if yes then "
                                                "make the field readonly", compute='_compute_is_secondary_readonly', store=True)
    remaining_target = fields.Float(string="Remaining Target", compute='_compute_remaining_target', store=False)

    def _compute_remaining_target(self):
        for record in self:
            # get qty from mrp
            consumed_lines = self.env['stock.move'].search([
                ('product_id', '=', record.product_id.id),
                ('raw_material_production_id', '!=', False),
                ('state', '=', 'done')
            ])

            consumed_qty = sum(consumed_lines.mapped('product_uom_qty'))
            if record.product_id.annual_target - consumed_qty < 0:
                record.remaining_target = 0
            else:
                record.remaining_target = record.product_id.annual_target - consumed_qty

    @api.depends('product_qty', 'parent_qty', 'bom_product_qty')
    def _compute_target_amount(self):
        for record in self:
            record.target_amount = (record.product_qty / record.bom_product_qty) * record.parent_qty

    @api.depends('product_id', 'product_id.qty_available', 'product_id.purchased_product_qty', 'secondary_product_uom_id')
    def _compute_available_qty(self):
        for record in self:
            pending_po_product_qty = record.product_id.pending_po_product_qty
            po_unit = record.product_id.uom_id
            second_uom = record.secondary_product_uom_id
            # pending_po_product_qty for secondary uom
            if second_uom:
                pending_po_product_qty = pending_po_product_qty * po_unit.factor_inv / second_uom.factor_inv

            record.pending_po_product_qty = pending_po_product_qty

            available_qty = record.product_id.qty_available
            # available_qty for secondary uom
            if record.secondary_product_uom_id:
                available_qty = available_qty * record.product_id.uom_id.factor_inv / record.secondary_product_uom_id.factor_inv
            record.available_qty = available_qty

            #         compute shortage and surplus
            if not record.secondary_product_uom_id or record.secondary_product_uom_id == record.product_uom:
                product_qty = record.product_qty
            else:
                product_qty = record.product_qty * record.product_uom.factor_inv / record.secondary_product_uom_id.factor_inv

            record.surplus = record.available_qty + record.pending_po_product_qty
            if product_qty > record.available_qty:
                # target qty in secondary uom
                record.shortage = product_qty - record.available_qty - record.pending_po_product_qty
                record.amount_state = 'shortage'
            else:
                record.shortage = 0

                record.amount_state = 'surplus'

    @api.depends('shortage', 'surplus')
    def _compute_amount_state(self):
        for record in self:
            if record.shortage > 0:
                record.amount_state = 'shortage'
            else:
                record.amount_state = 'surplus'

    @api.depends('secondary_product_uom_id', 'product_qty')
    def _compute_secondary_product_qty(self):
        for record in self:
            if not record.secondary_product_uom_id:
                record.secondary_product_uom_id = record.product_uom.id

            if record.secondary_product_uom_id == record.product_uom:
                record.secondary_product_uom_qty = record.product_qty
                continue

            # get quantity from secondary uom

            main_unit = record.product_uom
            secondary_unit = record.secondary_product_uom_id

            if main_unit.category_id.id != secondary_unit.category_id.id:
                raise UserError(_("The selected UoM's are not in the same category."))

            secondary_qty = record.product_qty * main_unit.factor_inv / secondary_unit.factor_inv
            record.secondary_product_uom_qty = secondary_qty

    @api.depends('product_id', 'product_id.secondary_uom_ids', 'product_id.is_need_secondary_uom')
    def _compute_secondary_product_uom(self):
        """Compute the default secondary uom"""
        for rec in self:
            all_secondary_uoms = rec.product_id.secondary_uom_ids.mapped('secondary_uom_id')
            if rec.product_id.is_need_secondary_uom and all_secondary_uoms:
                rec.secondary_uom_ids = [(6, 0, all_secondary_uoms.ids)]
            else:
                rec.secondary_uom_ids = [(6, 0, [])]

    @api.depends('product_id', 'product_id.secondary_uom_ids', 'product_id.is_need_secondary_uom')
    def _compute_is_secondary_readonly(self):
        for rec in self:
            all_secondary_uoms = rec.product_id.secondary_uom_ids.mapped('secondary_uom_id')
            if all_secondary_uoms and len(all_secondary_uoms) > 1:
                rec.is_secondary_readonly = False
            else:
                rec.is_secondary_readonly = True