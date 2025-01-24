# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProductYearTarget(models.Model):
    _name = 'product.year.target'
    _description = _('ProductYearTarget')

    lines = fields.One2many('product.year.target.line', 'target_id', string="Lines", compute='calculate_lines', store=True)
    product_type = fields.Selection([
        ('final_product', 'Final Product'),
        ('component', 'Component'),
        ('all', 'All')
    ], string="Product Type", default='final_product')

    def print(self):
        return self.env.ref('average_sales_report.action_target_report').report_action(self)

    @api.depends('product_type')
    def calculate_lines(self):
        for record in self:
            lines = []
            record.lines = False

            if record.product_type == 'all':
                product_ids = self.env['product.product'].search([('target_ids', '!=', False)])
            else:
                bom_ids = self.env['mrp.bom'].search([])
                domain = [('target_ids', '!=', False)]
                if record.product_type == 'final_product':
                    domain.append(('bom_ids', 'in', bom_ids.ids))
                else:
                    domain.append(('bom_ids', 'not in', bom_ids.ids))
                product_ids = self.env['product.product'].search(domain)

            for product in product_ids:
                current_year = fields.Date.today().year
                current_year_target = self.env['product.target'].search([
                    ('name', '=', str(current_year)),
                    ('product_template_id', '=', product.product_tmpl_id.id)
                ])

                next_year_target = self.env['product.target'].search([
                    ('name', '=', str(current_year + 1)),
                    ('product_template_id', '=', product.product_tmpl_id.id)
                ])

                lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom': current_year_target.product_uom.id,
                    'product_uom_next': next_year_target.product_uom.id,
                    'target_current_year': current_year_target.target_amount if current_year_target else 0,
                    'target_next_year': next_year_target.target_amount if next_year_target else 0
                }))
            record.lines = lines


class ProductYearTargetLine(models.Model):
    _name = 'product.year.target.line'
    _description = _('ProductYearTargetLine')

    target_id = fields.Many2one('product.year.target', string="Target")
    product_id = fields.Many2one('product.product', string="Product")
    bom_id = fields.Many2one('mrp.bom', string="BOM")

    product_uom_category_id = fields.Many2one(related='bom_id.product_id.uom_id.category_id', depends=['bom_id'])
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="UOM Current Year",
    )
    product_uom_next = fields.Many2one(
        comodel_name='uom.uom',
        string="UOM Next Year",
    )

    target_current_year = fields.Float("Target Current Year")
    target_next_year = fields.Float("Target Next Year")