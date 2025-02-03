# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    total_sale = fields.Float(compute='_sale_total', string="Total Sale", )
    total_payment = fields.Float(compute='_pay_total', string="Total Payment", )
    remaining_total = fields.Float(compute='remaining_sum_total', string="Remaining", )
    contacts_count = fields.Integer('Number of related contacts', compute='_compute_contacts_count')
    inv_count = fields.Integer('Number of Invoices', compute='get_inv_count')
    inv_total = fields.Float(compute='_compute_inv_total', string="Total Invoice", )

    def _compute_inv_total(self):
        sale_order_ids = self.env["sale.order"].search(
            [("delegate_sale_id", "=", self.id)]
        )
        if len(sale_order_ids) > 0:
            invs = sale_order_ids.mapped('invoice_ids')
            self.inv_total = abs(sum(invs.mapped('amount_total')))
        else:
            self.inv_total = 0

    def remaining_sum_total(self):
        self.remaining_total = self.total_sale - self.total_payment

    def action_view_sale_orders(self):
        self.ensure_one()
        sale_order_ids = self.env['sale.order'].search([('delegate_sale_id', '=', self.id)])
        print("sale_order_ids===<>", sale_order_ids)
        action = {
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
        }
        if len(sale_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': sale_order_ids[0],
            })
        else:
            action.update({
                'name': _("SAle Order generated from %s", self.name),
                'domain': [('id', 'in', sale_order_ids.ids)],
                'view_mode': 'tree,form',
            })
        return action

    def action_view_invoices(self):
        self.ensure_one()
        sale_order_ids = self.env['sale.order'].search([('delegate_sale_id', '=', self.id)])
        if not sale_order_ids:
            return False
        invoice_ids = sale_order_ids.mapped('invoice_ids')
        action = {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        action.update({
                'name': _("Invoice generated from %s", self.name),
                'domain': [('id', 'in', invoice_ids.ids)],
                'view_mode': 'tree,form',
            })

        return action

    def _sale_total(self):
        sale_total_ids = self.env['sale.order'].search([('delegate_sale_id', '=', self.id), ('state', '=', 'sale')])

        self.total_sale = abs(sum(sale_total_ids.mapped('amount_total')))

    def get_inv_count(self):
        for rec in self:
            sale_order_ids = self.env['sale.order'].search([('delegate_sale_id', '=', rec.id)])
            if not sale_order_ids:
                rec.inv_count = 0
            else:
                rec.inv_count = len(sale_order_ids.mapped('invoice_ids'))

    def action_view_payment(self):
        self.ensure_one()
        payment_ids = self.env['account.payment'].search([('delegate_pay_id', '=', self.id)])
        print("payment_ids===<>", payment_ids)
        action = {
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'name': _("Payment generated from %s", self.name),
            'domain': [('id', 'in', payment_ids.ids)],
            'view_mode': 'tree,form',
        }

        return action

    def _pay_total(self):
        pay_total_ids = self.env['account.payment'].sudo().search([('delegate_pay_id', '=', self.id)])
        print("pay_total_ids===>", pay_total_ids)
        self.total_payment = abs(sum(pay_total_ids.mapped('amount')))
        print("self.total_payment===>", self.total_payment)

    def _compute_contacts_count(self):
        for employee in self:
            contact_ids = employee.env['res.partner'].search([('delegate_id', '=', employee.id)])
            print("contact_ids===>", contact_ids)
            employee.contacts_count = len(contact_ids)

    def action_partner_contacts(self):
        self.ensure_one()
        contact_ids = self.env['res.partner'].search([('delegate_id', '=', self.id)])
        return {
            'name': _("Related Contacts"),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'res.partner',
            'domain': [('id', 'in', contact_ids.ids)]
        }


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    delegate_pay_id = fields.Many2one(related='partner_id.delegate_id', string='Delegate', readonly=False, )

    max_sale_amount = fields.Float(related='partner_id.delegate_id.max_sale_amount', string='Max Sale Amount', readonly=True, )
    remaining_total = fields.Float(related='partner_id.delegate_id.remaining_total', string='Remaining Total', readonly=False, )
