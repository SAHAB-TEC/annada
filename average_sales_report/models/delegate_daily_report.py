# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DelegateDailyReport(models.Model):
    _name = 'delegate.daily.report'
    _description = 'DelegateDailyReport'

    employee_id = fields.Many2one('hr.employee', string='Delegate', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)

    line_ids = fields.One2many('delegate.daily.report.line', 'report_id', string='Delegate Daily Report Line')    
    def generate_report(self):
        self.ensure_one()
        # add lines for each day between date_from and date_to
        date_from = fields.Date.from_string(self.date_from)
        date_to = fields.Date.from_string(self.date_to)
        current_date = date_from
        self.line_ids = [(5, 0, 0)]
        while current_date <= date_to:
            sale_ids = self.env['sale.order'].search([
                ('date_order', '>=', current_date),
                ('date_order', '<=', current_date),
                ('delegate_sale_id', '=', self.employee_id.id),
                ('state', 'in', ['sale'])
            ])
            
            payment_ids = self.env['account.payment'].search([
                ('date', '>=', current_date),
                ('date', '<=', current_date),
                ('delegate_pay_id', '=', self.employee_id.id),
                ('state', 'in', ['posted'])
            ])
            self.line_ids.create({
                'report_id': self.id,
                'date': current_date, 
                'sale_ids': [(6, 0, sale_ids.ids)],
                'sale_amount': sum(sale_ids.mapped('amount_total')),
                'payment_ids': [(6, 0, payment_ids.ids)],
                'payment_amount': sum(payment_ids.mapped('amount')),
            })
            current_date += timedelta(days=1)


class DelegateDailyReportLine(models.Model):
    _name = 'delegate.daily.report.line'
    _description = 'DelegateDailyReportLine'

    report_id = fields.Many2one('delegate.daily.report', string='Delegate Daily Report')
    date = fields.Date(string='Date', required=True)
    sale_ids = fields.Many2many('sale.order', string='Sale Order')
    sale_amount = fields.Float(string='Sale Amount')
    payment_ids = fields.Many2many('account.payment', string='Payment')
    payment_amount = fields.Float(string='Payment Amount')
