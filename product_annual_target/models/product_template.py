from datetime import datetime

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.tools.float_utils import float_round
from dateutil.relativedelta import relativedelta



class ProductTemplate(models.Model):
    _inherit = 'product.template'
    target_ids = fields.One2many(
        'product.target',
        'product_template_id',
        string="Annual Target",
        help="List of target amounts for different years",
       groups = "product_annual_target.group_target_access"
    )
    first_quarter = fields.Float(string='First half year target', compute="_compute_q", help='Target for the first quarter', readonly=False, store=True)
    second_quarter = fields.Float(string='Second half year target', compute="_compute_q", help='Target for the second quarter', readonly=False, store=True)
    annual_target = fields.Float(string='Annual Target', compute="_compute_annual_target", store=True, readonly=True)

    def _get_current_year(self):
        return datetime.now().year

    @api.depends('target_ids.target_amount', 'target_ids.name')
    def _compute_annual_target(self):
        """Compute the total annual target for the current year."""
        current_year = self._get_current_year()
        for record in self:
            annual_target = 0.0
            for target in record.target_ids:
                try:
                    target_year = int(target.name)  # Convert name to integer
                    if target_year == current_year:
                        annual_target += target.target_amount
                except ValueError:
                    # Skip invalid names that cannot be converted to integers
                    continue
            record.annual_target = annual_target

    @api.depends('annual_target')
    def _compute_q(self):
        for record in self:
            half_target = record.annual_target / 2
            record.first_quarter = half_target
            record.second_quarter = half_target

    # Quarter 1 fields 
    q1_month1 = fields.Float(store=True, readonly="False", string='January')
    q1_month2 = fields.Float(store=True, readonly="False", string='February')
    q1_month3 = fields.Float(store=True, readonly="False", string='March')
    q1_month4 = fields.Float(store=True, readonly="False", string='April')
    q1_month5 = fields.Float(store=True, readonly="False", string='May')
    q1_month6 = fields.Float(store=True, readonly="False", string='June')
    # Quarter 2 fields ,, sto
    q2_month1 = fields.Float(store=True, readonly="False", string='July')
    q2_month2 = fields.Float(store=True, readonly="False", string='August')
    q2_month3 = fields.Float(store=True, readonly="False", string='September')
    q2_month4 = fields.Float(store=True, readonly="False", string='October')
    q2_month5 = fields.Float(store=True, readonly="False", string='November')
    q2_month6 = fields.Float(store=True, readonly="False", string='December')

    # sum of the months for quarter 1 must = first_quarter
    # sum of the months for quarter 2 must = second_quarter

    # @api.constrains('q1_month1', 'q1_month2', 'q1_month3', 'q1_month4', 'q1_month5', 'q1_month6')
    # def _check_monthly1(self):
    #     for record in self:
    #         if record.q1_month1 == 0.0 and record.q1_month2 == 0.0 and record.q1_month3 == 0.0 and record.q1_month4 == 0.0 and record.q1_month5 == 0.0 and record.q1_month6 == 0.0:
    #             continue
    #         if record.first_quarter - (record.q1_month1 + record.q1_month2 + record.q1_month3 + record.q1_month4 + record.q1_month5 + record.q1_month6) >= 1 \
    #                 or (record.q1_month1 + record.q1_month2 + record.q1_month3 + record.q1_month4 + record.q1_month5 + record.q1_month6) - record.first_quarter >= 1:
    #             raise ValidationError(_("Monthly targets for the first quarter must sum up to the first quarter target."))
    #
    # @api.constrains('q2_month1', 'q2_month2', 'q2_month3', 'q2_month4', 'q2_month5', 'q2_month6')
    # def _check_monthly2(self):
    #     for record in self:
    #         if record.q2_month1 == 0.0 and record.q2_month2 == 0.0 and record.q2_month3 == 0.0 and record.q2_month4 == 0.0 and record.q2_month5 == 0.0 and record.q2_month6 == 0.0:
    #             continue
    #         if record.second_quarter - (record.q2_month2 + record.q2_month2 + record.q2_month3 + record.q2_month4 + record.q2_month5 + record.q2_month6 ) >= 1 \
    #                 or (record.q2_month2 + record.q2_month2 + record.q2_month3 + record.q2_month4 + record.q2_month5 + record.q2_month6 ) - record.second_quarter >= 1:
    #             raise ValidationError(_("Monthly targets for the second quarter must sum up to the second quarter target."))

    def write(self, vals):
        if 'q1_month1' in vals or 'q1_month2' in vals or 'q1_month3' in vals or 'q1_month4' in vals or 'q1_month5' in vals or 'q1_month6' in vals:
            first_quarter = self.first_quarter
    #         _check_monthly1
            if first_quarter - (vals.get('q1_month1', self.q1_month1) + vals.get('q1_month2', self.q1_month2) + vals.get('q1_month3', self.q1_month3) + vals.get('q1_month4', self.q1_month4) + vals.get('q1_month5', self.q1_month5) + vals.get('q1_month6', self.q1_month6)) >= 1 \
                    or (vals.get('q1_month1', self.q1_month1) + vals.get('q1_month2', self.q1_month2) + vals.get('q1_month3', self.q1_month3) + vals.get('q1_month4', self.q1_month4) + vals.get('q1_month5', self.q1_month5) + vals.get('q1_month6', self.q1_month6)) - first_quarter >= 1:
                raise ValidationError(_("Monthly targets for the first quarter must sum up to the first quarter target."))

        if 'q2_month1' in vals or 'q2_month2' in vals or 'q2_month3' in vals or 'q2_month4' in vals or 'q2_month5' in vals or 'q2_month6' in vals:
            second_quarter = self.second_quarter
            if second_quarter - (vals.get('q2_month1', self.q2_month1) + vals.get('q2_month2', self.q2_month2) + vals.get('q2_month3', self.q2_month3) + vals.get('q2_month4', self.q2_month4) + vals.get('q2_month5', self.q2_month5) + vals.get('q2_month6', self.q2_month6)) >= 1 \
                    or (vals.get('q2_month1', self.q2_month1) + vals.get('q2_month2', self.q2_month2) + vals.get('q2_month3', self.q2_month3) + vals.get('q2_month4', self.q2_month4) + vals.get('q2_month5', self.q2_month5) + vals.get('q2_month6', self.q2_month6)) - second_quarter >= 1:
                raise ValidationError(_("Monthly targets for the second quarter must sum up to the second quarter target."))
        return super(ProductTemplate, self).write(vals)

    @api.onchange('first_quarter')
    def onchange_first_secenod(self):
        for line in self:
            if line.first_quarter + line.second_quarter != line.annual_target:
                line.second_quarter = line.annual_target - line.first_quarter

    @api.onchange('second_quarter')
    def onchange_second_first(self):
        for line in self:
            if line.first_quarter + line.second_quarter != line.annual_target:
                line.first_quarter = line.annual_target - line.second_quarter

    def compute_m(self):
        line = self
        monthly_1 = line.first_quarter / 6
        line.write({
            'q1_month1': monthly_1,
            'q1_month2': monthly_1,
            'q1_month3': monthly_1,
            'q1_month4': monthly_1,
            'q1_month5': monthly_1,
            'q1_month6': monthly_1,
        })

        monthly_2 = line.second_quarter / 6
        line.write({
            'q2_month1': monthly_2,
            'q2_month2': monthly_2,
            'q2_month3': monthly_2,
            'q2_month4': monthly_2,
            'q2_month5': monthly_2,
            'q2_month6': monthly_2,
        })

    @api.onchange('annual_target')
    def _onchange_annual_target(self):
        """Automatically split the annual target and distribute to quarters and months."""
        if self.annual_target:
            # Split annual target into two quarters
            half_target = self.annual_target / 2
            self.first_quarter = half_target
            self.second_quarter = half_target

        else:
            self.first_quarter = 0.0
            self.second_quarter = 0.0
            self.write({
                'q1_month1': 0.0,
                'q1_month2': 0.0,
                'q1_month3': 0.0, 'q1_month4': 0.0, 'q1_month5': 0.0, 'q1_month6': 0.0, 'q2_month1': 0.0, 'q2_month2': 0.0, 'q2_month3': 0.0, 'q2_month4': 0.0, 'q2_month5': 0.0, 'q2_month6': 0.0}
            )

    pending_po_product_qty = fields.Float(compute='_compute_pending_po_product_qty', string='Pending Purchased' )
    def _compute_pending_po_product_qty(self):
        for template in self:
            total_qty = 0.0
            for product_variant in template.product_variant_ids:
                domain = [
                    ('product_id', '=', product_variant.id),
                    ('order_id.state', 'in', ['purchase', 'done']),
                    ('order_id.picking_ids.state', '!=', 'done')
                ]
                main_unit = product_variant.uom_id
                purchase_lines = self.env['purchase.order.line'].search(domain)
                # get quantity in unit
                for line in purchase_lines:
                    line_unit = line.product_uom
                    if line_unit != main_unit:
                        total_qty += line.product_qty * line.product_uom.factor_inv / main_unit.factor_inv
                    else:
                        total_qty += line.product_qty
            template.pending_po_product_qty = float_round(
                total_qty,
                precision_rounding=template.uom_id.rounding
            )
    def action_view_pending_po(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.action_purchase_history")
        action['domain'] = ['&', ('state', 'in', ['purchase', 'done']),
                            ('product_id', 'in', self.product_variant_ids.ids),('order_id.picking_ids.state', '!=', 'done')]
        action['display_name'] = _("Purchase History for %s", self.display_name)
        return action

class ProductProduct(models.Model):
    _inherit = 'product.product'

    pending_po_product_qty = fields.Float(compute='_compute_pending_po_product_qty', string='Pending Purchased' )

    def _compute_pending_po_product_qty(self):
        for product in self:
            total_qty = 0.0
            domain = [
                ('product_id', '=', product.id),
                ('order_id.state', 'in', ['purchase', 'done']),
                ('order_id.picking_ids.state', '!=', 'done')
            ]
            main_unit = product.uom_id
            purchase_lines = self.env['purchase.order.line'].search(domain)
            # get quantity in unit
            for line in purchase_lines:
                line_unit = line.product_uom
                if line_unit != main_unit:
                    total_qty += line.product_qty * line.product_uom.factor_inv / main_unit.factor_inv
                else:
                    total_qty += line.product_qty


            product.pending_po_product_qty = float_round(
                total_qty,
                precision_rounding=product.uom_id.rounding
            )
    def action_view_pending_po(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.action_purchase_history")
        action['domain'] = ['&', ('state', 'in', ['purchase', 'done']),
                            ('product_id', '=', self.id),('order_id.picking_ids.state', '!=', 'done')]
        action['display_name'] = _("Purchase History for %s", self.display_name)
        return action