from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.fields import Datetime


class MonthlyCommission(models.Model):
    _name = 'monthly.commission'
    _description = 'Monthly Commission Summary'

    name = fields.Char('Name', compute='_compute_name')

    @api.depends('year', 'month')
    def _compute_name(self):
        for record in self:
            record.name = record.year + '-' + record.month

    year = fields.Char('Year', required=True, default=lambda self: fields.Date.today().year)
    month = fields.Char('Month', required=True, default=lambda self: fields.Date.today().month)

    commission_types = fields.Selection([
        ('all', 'All'),
        ('sales_wholesale_premium', 'Sales (Wholesale - Premium)'),
        ('sales_wholesale_normal', 'Sales (Wholesale - Normal)'),
        ('sales_retail', 'Sales (Retail)'),
        ('sales_cafe_restaurant', 'Sales (Café/Restaurant)'),
        ('supervisor', 'Supervisor'),
        ('warehouse', 'Warehouse'),
        ('management', 'Management'),
        ('finance', 'Finance'),
        ('driver', 'Driver')]
        , string='Commission Type', default='all')

    employees = fields.Many2many('hr.employee', string='Employees')

    lines = fields.One2many('monthly.commission.line', 'monthly_commission_id', string='Lines',)

    def get_emp_domain(self):
        domain = []
        if self.commission_types != 'all' and self.commission_types:
            domain.append(('commission_type', '=', self.commission_types))
        return domain

    def action_compute_lines(self):
        self.ensure_one()
        self.env['monthly.commission.line'].search([('monthly_commission_id', '=', self.id)]).unlink()
        employees = self.env['hr.employee'].search(self.get_emp_domain())
        lines = []
        for employee in employees:
            lines.append((0, 0, {
                'employee_id': employee.id,
                'monthly_commission_id': self.id
            }))
        self.write({'lines': lines})

class MonthlyCommissionLine(models.Model):
    _name = 'monthly.commission.line'
    _description = 'Monthly Commission Line'

    monthly_commission_id = fields.Many2one('monthly.commission', string='Monthly Commission', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    year = fields.Char('Year', required=True, related='monthly_commission_id.year')
    month = fields.Char('Month', required=True, related='monthly_commission_id.month')
    target_payment_amount = fields.Float('Target Payment Amount', related='employee_id.target_payment_amount')
    min_target = fields.Float('Minimum Target', related='employee_id.min_target')
    commission_types = fields.Selection(related='employee_id.commission_type')
    total_payments = fields.Float('Total Payments', compute='_compute_total_payments')
    target_rate = fields.Float('Target Rate', compute='_compute_target_rate')
    total_commission = fields.Float('Total Commission', compute='_compute_total_commission')

    @api.depends('total_payments', 'target_payment_amount')
    def _compute_target_rate(self):
        for record in self:
            if record.target_payment_amount == 0:
                record.target_rate = 0
            else:
                record.target_rate = record.total_payments / record.target_payment_amount * 100

    @api.depends('employee_id', 'month', 'year')
    def _compute_total_payments(self):
        for record in self:
            year = record.year
            month = record.month

            date_now = fields.Date.today()
            strat_date = date_now.replace(year=int(year), month=int(month), day=1)
            end_date = strat_date + relativedelta(months=1, days=-1)

            payment_ids = self.env['account.payment'].search([
                ('delegate_pay_id', '=', record.employee_id.id),
                ('date', '>=', strat_date),
                ('date', '<=', end_date),
                ('state', '=', 'posted')])

            record.total_payments = sum(payment_ids.mapped('amount'))

    @api.depends('total_payments', 'commission_types', 'target_payment_amount')
    def _compute_total_commission(self):
        for record in self:
            year = record.year
            month = record.month

            date_now = fields.Date.today()
            strat_date = date_now.replace(year=int(year), month=int(month), day=1)
            end_date = strat_date + relativedelta(months=1, days=-1)

            payment_ids = self.env['account.payment'].search([
                ('delegate_pay_id', '=', record.employee_id.id),
                ('date', '>=', strat_date),
                ('date', '<=', end_date),
                ('state', '=', 'posted')])

            record.total_payments = sum(payment_ids.mapped('amount'))

            record.total_commission = 0
            commission = 0
            max_salary = record.employee_id.max_salary
            max_commission = record.employee_id.max_commission

            if record.commission_types == 'sales_wholesale_premium':
                if record.total_payments >= record.target_payment_amount * (record.min_target / 100):
                    commission = record.total_payments * 0.01
                else:
                    commission = record.total_payments * 0.005
                record.total_commission = min(commission, max_commission)

            elif record.commission_types == 'sales_wholesale_normal':
                if record.total_payments >= record.target_payment_amount * (record.min_target / 100):
                    commission = record.total_payments * 0.01
                else:
                    commission = record.total_payments * 0.005
                record.total_commission = min(commission, max_commission)

            elif record.commission_types == 'sales_retail':
                first_pln = record.employee_id.first_pln
                second_pln = record.employee_id.second_pln
                third_pln = record.employee_id.third_pln
                fourth_pln = record.employee_id.fourth_pln

                if record.total_payments < first_pln:
                    commission = record.total_payments * 0.005
                elif record.total_payments < second_pln:
                    commission = record.total_payments * 0.01
                elif record.total_payments < third_pln:
                    comm1 = second_pln * 0.01
                    comm2 = (record.total_payments - second_pln) * 0.02
                    commission = comm1 + comm2
                else:
                    comm1 = second_pln * 0.01
                    comm2 = (third_pln - second_pln) * 0.02
                    comm3 = (record.total_payments - third_pln) * 0.03
                    commission = comm1 + comm2 + comm3
                record.total_commission = min(commission, max_commission)

            elif record.commission_types == 'sales_cafe_restaurant':
                record.total_commission = record.total_payments * 0.01

            elif record.commission_types == 'supervisor':
                direct_reports = record.employee_id.child_ids
                total_payments = 0
                total_target = sum(direct_reports.mapped('target_payment_amount'))
                for report in direct_reports:
                    total_payments += sum(self.env['account.payment'].search([
                        ('delegate_pay_id', '=', report.id),
                        ('date', '>=', strat_date),
                        ('date', '<=', end_date),
                        ('state', '=', 'posted')]).mapped('amount'))

                if total_payments >= total_target:
                    commission = total_payments * 0.005
                else:
                    commission = total_payments * 0.0025

                record.total_commission = commission

            elif record.commission_types == 'warehouse':
                retail_employee_ids = record.employee_id.retail_employees
                wholesale_employee_ids = record.employee_id.wholesale_employees
                total_commission = 0
                total_qty = 0
                rate = record.employee_id.warehouse_rate
                main_uom = self.env['uom.uom'].search([('is_main_uom', '=', True)], limit=1)
                if not main_uom:
                    main_uom = self.env['uom.uom'].search([('name', '=', 'STEKA')], limit=1)

                if not main_uom:
                    raise ValidationError('Main UOM not found')
                if retail_employee_ids:
                    all_delivered_products1 = self.env['stock.move'].search([
                        ('state', '=', 'done'),
                        ('date', '>=', strat_date),
                        ('date', '<=', end_date),
                        ('sale_line_id.order_id.delegate_sale_id', 'in', [employee.id for employee in retail_employee_ids]),
                    ])

                    for move in all_delivered_products1:
                        total_qty += main_uom._compute_quantity(move.product_uom_qty, move.product_id.uom_id)
                        warehouse_rate = move.sale_line_id.order_id.delegate_sale_id.warehouse_rate
                        total_commission += total_qty * warehouse_rate

                if wholesale_employee_ids:
                    all_delivered_products2 = self.env['stock.move'].search([
                        ('state', '=', 'done'),
                        ('date', '>=', strat_date),
                        ('date', '<=', end_date),
                        ('sale_line_id.order_id.delegate_sale_id', 'in', [employee.id for employee in wholesale_employee_ids]),
                    ])

                    for move in all_delivered_products2:
                        total_qty += main_uom._compute_quantity(move.product_uom_qty, move.product_id.uom_id)
                        warehouse_rate = move.sale_line_id.order_id.delegate_sale_id.warehouse_rate
                        total_commission += total_qty * warehouse_rate

                record.total_commission = min(total_commission, max_salary)
            else:
                record.total_commission = 0