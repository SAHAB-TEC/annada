# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProductYearTarget(models.Model):
    _name = 'product.year.target'
    _description = _('ProductYearTarget')

    lines = fields.One2many('product.year.target.line', 'target_id', string="Lines", compute='calculate_lines',
                            store=True)
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
                produced_current_year = 0.0
                purchased_current_year = 0.0
                start_date = fields.Date.today().replace(year=current_year, month=1, day=1)
                end_date = fields.Date.today().replace(year=current_year, month=12, day=31)

                produced_current_year = self.env['mrp.production'].search([
                    ('product_id', '=', product.id),
                    ('state', '=', 'done'),
                    ('date_finished', '>=', start_date),
                    ('date_finished', '<=', end_date)
                ]).mapped('product_qty')

                purchased_current_year = self.env['purchase.order.line'].search([
                    ('product_id', '=', product.id),
                    ('order_id.state', '=', 'purchase'),
                    ('order_id.date_order', '>=', start_date),
                    ('order_id.date_order', '<=', end_date)
                ]).mapped('product_qty')

                lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom': current_year_target.product_uom.id,
                    'produced_current_year': sum(produced_current_year),
                    'purchased_current_year': sum(purchased_current_year),
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
    produced_current_year = fields.Float("Produced Current Year")
    purchased_current_year = fields.Float("Purchased Current Year")
    target_next_year = fields.Float("Target Next Year")
