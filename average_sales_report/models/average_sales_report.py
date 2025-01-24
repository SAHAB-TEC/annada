# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime

from odoo.exceptions import UserError


class AverageSalesLines(models.Model):
    _name = 'average.sales.report.line'
    _description = 'Average Sales Report Template'

    report_id = fields.Many2one('average.sales.report.form', string="Report")
    product_id = fields.Many2one('product.product', string="Product", required=False)
    bom_id = fields.Many2one('mrp.bom', string="BOM")

    product_uom_category_id = fields.Many2one(related='bom_id.product_id.uom_id.category_id', depends=['bom_id'])
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        related='bom_id.product_tmpl_id.uom_id',
        )

    secondary_uom_ids = fields.Many2many('uom.uom',
                                         string="Secondary Uom Ids",
                                         compute='_compute_secondary_product_uom',
                                         help="For fetching all the secondary"
                                              " uom's")
    secondary_product_uom_id = fields.Many2one(
        'uom.uom', string='Secondary UoM',
        readonly=False,
        help="Select the Secondary Uom",
        domain="[('id', 'in', secondary_uom_ids)]")

    is_secondary_readonly = fields.Boolean(string="Is Secondary Uom",
                                           help="The field to check whether"
                                                " the selected uom is"
                                                " secondary and if yes then "
                                                "make the field readonly", compute='_compute_is_secondary_readonly',
                                           store=True)
    sales_first_half = fields.Float("Sales First Half", store=True)
    sales_second_half = fields.Float("Sales Second Half", store=True)
    sales_per_year = fields.Float("Sales Per Year", store=True)
    sales_per_year_second_unit = fields.Float("Sales Per Year Second Unit", store=True)
    percentage_first_half = fields.Float("Percentage Sales First Half", store=True)
    percentage_second_half = fields.Float("Percentage Sales Second Half", store=True)
    #
    # @api.depends('secondary_product_uom_id', 'sales_first_half', 'sales_second_half', 'sales_per_year', 'percentage_first_half', 'report_id.year')
    # def _compute_secondary_product_qty(self):
    #     for record in self:
    #         if not record.secondary_product_uom_id:
    #             record.secondary_product_uom_id = record.product_uom.id
    #
    #         main_unit = record.product_uom
    #         secondary_unit = record.secondary_product_uom_id
    #
    #         if record.secondary_product_uom_id == record.product_uom:
    #             record.sales_per_year_second_unit = record.sales_per_year
    #         else:
    #             record.sales_per_year_second_unit = record.sales_per_year * main_unit.factor_inv / secondary_unit.factor_inv
    #
    #         record.sales_first_half = record.sales_per_year_second_unit / 2
    #         record.sales_second_half = record.sales_per_year_second_unit / 2
    #         record.percentage_first_half = record.sales_first_half / 6
    #         record.percentage_second_half = record.sales_second_half / 6

    @api.depends('bom_id', 'bom_id.product_tmpl_id.secondary_uom_ids', 'bom_id.product_tmpl_id.is_need_secondary_uom', 'report_id.year')
    def _compute_secondary_product_uom(self):
        """Compute the default secondary uom"""
        for rec in self:
            all_secondary_uoms = rec.bom_id.product_tmpl_id.secondary_uom_ids.mapped('secondary_uom_id')
            if rec.bom_id.product_tmpl_id.is_need_secondary_uom and all_secondary_uoms:
                rec.secondary_uom_ids = [(6, 0, all_secondary_uoms.ids)]
            else:
                rec.secondary_uom_ids = [(6, 0, [])]

    @api.depends('bom_id', 'bom_id.product_id', 'bom_id.product_tmpl_id', 'bom_id.product_tmpl_id.secondary_uom_ids', 'bom_id.product_tmpl_id.is_need_secondary_uom', 'report_id.year')
    def _compute_is_secondary_readonly(self):
        for rec in self:
            all_secondary_uoms = rec.bom_id.product_tmpl_id.secondary_uom_ids.mapped('secondary_uom_id')
            if all_secondary_uoms and len(all_secondary_uoms) > 1:
                rec.is_secondary_readonly = False
            else:
                rec.is_secondary_readonly = True


class AverageSalesReportForm(models.Model):
    _name = 'average.sales.report.form'
    _description = 'Average Sales Report for Product'
    _rec_name = 'year'

    year = fields.Selection([
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

    ], string='Year To Filter', required=True, help="Enter the year for filtering the sales report.", default=lambda self: str(datetime.now().year))

    sales_report_line_ids = fields.One2many('average.sales.report.line', 'report_id', string="Sales Report Lines", compute='calculate_sales', store=True, readonly=False)

    def print(self):
        return self.env.ref('average_sales_report.action_average_sales_report').report_action(self)

    @api.depends('year')
    def calculate_sales(self):
        for record in self:
            current_year = datetime.now().year
            selected_year = int(record.year)
            lines = []
            record.sales_report_line_ids = False
            bom_product_ids = self.env['mrp.bom'].search([])
            for bom_id in bom_product_ids:

                product = bom_id.product_tmpl_id
                sale_orders = self.env['sale.order.line'].search([
                    ('product_id', '=', product.product_variant_id.id),
                    ('order_id.state', '=', 'sale'),
                    ('order_id.date_order', '>=', f'{selected_year}-01-01'),
                    ('order_id.date_order', '<=', f'{selected_year}-12-31')
                ])

                # total_sales = sum(line.product_uom_qty for line in sale_orders)
                # total_sales in main unit
                total_sales = 0.0
                for line in sale_orders:
                    if line.product_uom != line.product_id.uom_id:
                        line_qty = line.product_uom_qty * line.product_uom.factor_inv / line.product_id.uom_id.factor_inv
                    else:
                        line_qty = line.product_uom_qty

                    total_sales += line_qty

                sales_per_year = total_sales

                first_half_orders = sale_orders.filtered(lambda l: l.order_id.date_order.month <= 6)
                sales_first_half = sum(line.product_uom_qty for line in first_half_orders)
                percentage_first_half = sales_first_half / 6

                second_half_orders = sale_orders.filtered(lambda l: l.order_id.date_order.month > 6)
                sales_second_half = sum(line.product_uom_qty for line in second_half_orders)
                percentage_second_half = sales_second_half / 6

                lines.append((0, 0, {
                    'bom_id': bom_id.id,
                    'product_uom': product.uom_id.id,
                    'secondary_product_uom_id': product.uom_id.id,
                    'sales_first_half': sales_first_half,
                    'sales_second_half': sales_second_half,
                    'sales_per_year': sales_per_year,
                    'percentage_first_half': percentage_first_half,
                    'percentage_second_half': percentage_second_half,
                }))

            record.sales_report_line_ids = lines