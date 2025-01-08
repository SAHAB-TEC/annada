# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    salesperson = fields.Boolean(string="SalesPerson", )
    commission_delegate_ids = fields.One2many(comodel_name='commission.delegate', inverse_name='hr_delegate_id',
                                              string='Commission', required=False)


class DelegateCommission(models.Model):
    _name = 'commission.delegate'
    _order = 'amount desc'

    hr_delegate_id = fields.Many2one(comodel_name='hr.employee', string='Delegate Commission', required=False)
    amount = fields.Float(string='Amount', required=False)
    percentage = fields.Float(string='percent', required=False)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    delegate_id = fields.Many2one(comodel_name="hr.employee", string="Delegate", required=False,
                                  domain="[('salesperson', '=', True)]")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    region = fields.Char(related='partner_id.street2', string='Region', readonly=False, )
    delegate_sale_id = fields.Many2one(related='partner_id.delegate_id', string='Delegate', readonly=False, )
    paid = fields.Float(compute='_paid_total', string="Paid", required=False, )
    remaining_amount = fields.Float(compute='_remaining_total', string="Remaining Amount", required=False, )
    cash = fields.Selection(string='Cash', selection=[('cash', 'Cash')], required=False, )

    def _remaining_total(self):
        for rec in self:
            rec.remaining_amount = rec.amount_total - rec.paid

    def _paid_total(self):
        for ret in self:
            invoices = ret.env['account.move'].search([('name', '=', ret.invoice_ids.name)])
            print("invoices===>", invoices)
            for rec in invoices:
                payment = ret.env['account.payment'].search([('ref', '=', rec.name)])
                print("payment==>", payment)
                ret.paid = abs(sum(payment.mapped('amount')))
            print("self.paid==>", ret.paid)
