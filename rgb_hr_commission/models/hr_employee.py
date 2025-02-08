# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = _('HrEmployee')
    
    commission_type = fields.Selection([
        ('sales_wholesale_premium', 'Sales (Wholesale - Premium)'),
        ('sales_wholesale_normal', 'Sales (Wholesale - Normal)'),
        ('sales_retail', 'Sales (Retail)'),
        ('sales_cafe_restaurant', 'Sales (Café/Restaurant)'),
        ('supervisor', 'Supervisor'),
        ('warehouse', 'Warehouse'),
        ('management', 'Management'),
        ('finance', 'Finance'),
        ('driver', 'Driver')],
        string='Commission Type', groups='hr.group_hr_user')

    retail_employees = fields.Many2many('hr.employee', 'hr_employee_retail_rel', 'employee_id', 'retail_employee_id', string='Retail Employees', groups='hr.group_hr_user')
    wholesale_employees = fields.Many2many('hr.employee', 'hr_employee_wholesale_rel', 'employee_id', 'wholesale_employee_id', string='Wholesale Employees', groups='hr.group_hr_user')

    target_payment_amount = fields.Float(string='Target Payment Amount', groups='hr.group_hr_user')
    min_target = fields.Float(string='Minimum Target', groups='hr.group_hr_user')
    warehouse_rate = fields.Float(string='Rate', groups='hr.group_hr_user', required=commission_type == 'warehouse')
    max_salary = fields.Float(string='Max Salary', groups='hr.group_hr_user')
    max_commission = fields.Float(string='Max Commission', groups='hr.group_hr_user')
    first_pln = fields.Float(string='First PLN', groups='hr.group_hr_user', required=commission_type == 'sales_retail')
    second_pln = fields.Float(string='Second PLN', groups='hr.group_hr_user', required=commission_type == 'sales_retail')
    third_pln = fields.Float(string='Third PLN', groups='hr.group_hr_user', required=commission_type in ['sales_retail', 'warehouse'])
    fourth_pln = fields.Float(string='Fourth PLN', groups='hr.group_hr_user', required=commission_type == 'sales_retail')



