# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MrpDelegate(models.Model):
    _name = 'mrp.delegate'
    _description = 'MrpDelegate'

    product_ids = fields.Many2many('product.product', string='Products')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    shift_name = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('night', 'Night'),
    ], string='Shift', default='morning')

    date_from = fields.Datetime(string='Date From')
    date_to = fields.Datetime(string='Date To')


    line_ids = fields.One2many('mrp.delegate.line', 'delegate_id', string='Delegate Lines')


    def action_delegate_refresh(self):
        self.line_ids.unlink()
        mrp_ids = self.env['mrp.production'].search([
            ('product_id', 'in', self.product_ids.ids),
            ('delegate_id', 'in', self.employee_ids.ids),
            ('shift_name', '=', self.shift_name),
            ('date_done', '>=', self.date_from),
            ('date_done', '<=', self.date_to),
        ])
        for mrp in mrp_ids:
            self.line_ids.create({
                'delegate_id': self.id,
                'employee_id': mrp.delegate_id.id,
                'shift_name': mrp.shift_name,
                'date': mrp.date_done,
                'qty': mrp.product_qty,
                'product_id': mrp.product_id.id,
                'mo_id': mrp.id
            })
    #
    # def action_print_report(self):
    #     return self.env.ref('rgb_mrp_custom.action_mrp_delegate').report_action(self)
    
    
class MrpDelegateLine(models.Model):
    _name = 'mrp.delegate.line'
    _description = 'MrpDelegateLine'

    delegate_id = fields.Many2one('mrp.delegate', string='Delegate')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    shift_name = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('night', 'Night'),
    ], string='Shift', default='morning')
    date = fields.Date(string='Date')
    qty = fields.Float(string='Qty')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='State', default='draft')
    
    product_id = fields.Many2one('product.product', string='Product')
    mo_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    