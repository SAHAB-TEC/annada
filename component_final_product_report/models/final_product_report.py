from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class FinalProductReports(models.Model):
    _name = 'final.product.reports'
    _description = _('Final Product Reports')
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Product')
    components = fields.One2many('final.product.report.line', 'report_id', compute='_compute_components',
                                 string='Components', store=True)

    secondary_uom_ids = fields.Many2many('uom.uom', compute='_compute_secondary_product_uom', string="Secondary UoMs")

    component_uom_id = fields.Many2one('uom.uom', string='Component UoM', store=True, readonly=False, domain="[('id', 'in', secondary_uom_ids)]")

    def print(self):
        return self.env.ref('component_final_product_report.action_final_product_report_pdf').report_action(self)

    @api.depends('product_id')
    def _compute_secondary_product_uom(self):
        for rec in self:
            all_secondary_uoms = rec.product_id.secondary_uom_ids.mapped('secondary_uom_id')
            rec.secondary_uom_ids = all_secondary_uoms

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.component_uom_id = self.product_id.uom_id


    @api.depends('product_id', 'component_uom_id')
    def _compute_components(self):
        """ Compute the components when a product is selected. """
        for record in self:
            record.components = [(5, 0, 0)]  # Clear previous components
            if not record.product_id:
                continue

            product_bom_lines = self.env['mrp.bom.line'].search([('product_id', '=', record.product_id.id)])

            components_data = [self._prepare_component_data(bom_line, record.product_id, record.component_uom_id) for bom_line in
                               product_bom_lines]
            record.write({'components': components_data})

    def _prepare_component_data(self, bom_line, material, uom):
        """ Prepare the data for a single component line. """
        bom_id = bom_line.bom_id
        my_l_id = 0
        for p_m_l in bom_id.bom_line_ids:
            if p_m_l.product_id == material:
                my_l_id = p_m_l.id

        bom_line_id = self.env['mrp.bom.line'].search([('id', '=', my_l_id)])

        line_uom = bom_line_id.product_uom_id
        line_qty = bom_line_id.product_qty

        parent_qty = bom_id.product_qty
        parent_uom = bom_id.product_uom_id



        final_product = bom_id.product_tmpl_id

        component_qty = bom_line.product_qty
        remaining_target = self._get_remaining_target(final_product)

        main_uom = material.uom_id
        secondary_uom = uom
        concentrate_stock = material.qty_available
        approved_purchased = material.pending_po_product_qty

        consumer_center = (remaining_target * line_qty) / parent_qty

        if main_uom != secondary_uom:
            component_qty = component_qty * secondary_uom.factor / main_uom.factor
            concentrate_stock = concentrate_stock * secondary_uom.factor / main_uom.factor
            approved_purchased = approved_purchased * secondary_uom.factor / main_uom.factor

        if main_uom != secondary_uom:
            consumer_center = consumer_center * secondary_uom.factor / main_uom.factor

        center_stage = concentrate_stock - consumer_center

        new_target_2025 = self._get_new_target(final_product)
        half_year_target = new_target_2025 / 2
        half_year_target_concentrate = half_year_target * line_qty / parent_qty
        full_year_target_concentrate = new_target_2025 * line_qty / parent_qty

        if main_uom != secondary_uom:
            half_year_target_concentrate = half_year_target_concentrate * secondary_uom.factor / main_uom.factor
            full_year_target_concentrate = full_year_target_concentrate * secondary_uom.factor / main_uom.factor



        required_six_months = half_year_target_concentrate - center_stage - approved_purchased
        required_full_year = full_year_target_concentrate - center_stage - approved_purchased

        if required_six_months < 0:
            required_six_months = 0
        if required_full_year < 0:
            required_full_year = 0


        return (0, 0, {
            'product_id': final_product.id,
            'line_uom_id': line_uom.id,
            'remaining_target': remaining_target,
            'concentrate_stock': concentrate_stock,
            'approved_purchased': approved_purchased,
            'consumer_center': consumer_center,
            'center_stage': center_stage,
            'new_target_2025': new_target_2025,
            'half_year_target': half_year_target,
            'half_year_target_concentrate': half_year_target_concentrate,
            'full_year_target_concentrate': full_year_target_concentrate,
            'required_six_months': required_six_months if required_six_months > 0 else 0,
            'required_full_year': required_full_year if required_full_year > 0 else 0,
        })

    def _get_remaining_target(self, product):
        """ Calculate the remaining target for the product. """

        produced_records = self.env['mrp.production'].search([
            ('product_tmpl_id', '=', product.id), ('state', '=', 'done')
        ])
        produced_qty = sum(produced_records.mapped('product_qty'))
        return product.annual_target - produced_qty

    def _get_approved_purchased(self, material):
        """ Calculate the approved purchased quantity for the material. """
        purchase_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', material.id),
            ('order_id.state', 'in', ['purchase', 'done']),

        ])

        total_in_man_units = 0

        for p_line in purchase_lines:
            line_qty = p_line.product_qty
            line_uom = p_line.product_uom
            if line_uom != material.uom_id:
                line_qty = line_qty * line_uom.factor / material.uom_id.factor
            else:
                line_qty = line_qty

            total_in_man_units += line_qty

        return total_in_man_units

    def _get_new_target(self, product):
        """ Get the new target for the next year. """
        current_year = datetime.now().year
        next_year = current_year + 1

        next_year_target = product.target_ids.filtered(lambda t: t.name == str(next_year))
        if next_year_target:
            return next_year_target[0].target_amount

        _logger.warning(f"No target found for {next_year}")
        return 0


class FinalProductReportLine(models.Model):
    _name = 'final.product.report.line'
    _description = _('Final Product Report Line')

    report_id = fields.Many2one('final.product.reports', string='Report')
    product_id = fields.Many2one('product.product', string='Product')

    main_uom = fields.Many2one('uom.uom', string='Main UoM')
    line_uom_id = fields.Many2one('uom.uom', string='Line UoM')
    secondary_uom_ids = fields.Many2many('uom.uom', compute='_compute_secondary_product_uom', string="Secondary UoMs")
    secondary_product_uom_id = fields.Many2one('uom.uom', string='Secondary UoM',
                                               domain="[('id', 'in', secondary_uom_ids)]")
    is_secondary_readonly = fields.Boolean(compute='_compute_is_secondary_readonly', string="Is Secondary UoM Readonly")

    remaining_target = fields.Float(string='باقي المستهدف للسنة الحالية للمنتج')
    concentrate_stock = fields.Float(string='مخزون المادة الخام')
    approved_purchased = fields.Float(string='الشراء / المعتمد')
    consumer_center = fields.Float(string='المستهلك لبقية العام من المادة الخام')
    center_stage = fields.Float(string='مرحل المادة الخام')
    new_target_2025 = fields.Float(string='المستهدف للعام الجديد للمنتج')
    half_year_target = fields.Float(string='المستهدف نصف السنوي للمنتج')
    half_year_target_concentrate = fields.Float(string='مستهدف نصف سنوي للمادة الخام')
    full_year_target_concentrate = fields.Float(string='المستهدف السنوي للعام الجديد للخام')
    required_six_months = fields.Float(string='المطلوب لستة اشهر للمادة الخام بعد الخصم')
    required_full_year = fields.Float(string='الخام المطلوب للعام الجديد كاملا بعد الخصم')

    @api.depends('product_id')
    def _compute_secondary_product_uom(self):
        for rec in self:
            all_secondary_uoms = rec.product_id.secondary_uom_ids.mapped('secondary_uom_id')
            rec.secondary_uom_ids = all_secondary_uoms

    @api.depends('secondary_uom_ids')
    def _compute_is_secondary_readonly(self):
        for rec in self:
            rec.is_secondary_readonly = len(rec.secondary_uom_ids) <= 1
