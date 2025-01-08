# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DelegateCommissionWiz(models.TransientModel):
    _name = "delegate.commission.wiz"
    _description = 'Delegate Commission Wizard'

    date_from = fields.Date(string="From", required=True, )
    date_to = fields.Date(string="To", required=True, )

    delegate_ids = fields.Many2many(comodel_name="hr.employee", string="Delegate", required=False,
                                    domain="[('salesperson', '=', True)]")

    def print_delegate_commission(self):
        emp_data = []
        date_from = self.date_from
        date_to = self.date_to

        delegate = self.delegate_ids
        if not delegate:
            delegate = self.env['hr.employee'].search([('salesperson', '=', True)])
        for emp in delegate:
            domain = [('date_order', '>=', date_from), ('date_order', '<=', date_to), ('delegate_sale_id', '=', emp.id)]

            orders = self.env['sale.order'].search(domain)
            # print("validity===>", validity)
            total_sale = abs(sum(orders.mapped('amount_total')))
            # relus1 = self.env['commission.delegate'].search([('hr_delegate_id', '=', emp.id)], order='amount desc')
            # relus2 = self.env['commission.delegate'].search([('hr_delegate_id', '=', emp.id)])
            # print("relus1===>", relus1[0].amount)
            # print("relus2===>", relus2[0].amount)
            per = 0
            for line in emp.commission_delegate_ids:
                if total_sale >= line.amount:
                    per = line.percentage
                    break
            rec = {
                'emp_name': emp.name,
                'total_sales': total_sale,
                'percent': per,
                'value': per * total_sale / 100.0,
            }
            emp_data.append(rec)

        data = {
            'form': self.read()[0],
            'emp_data': emp_data,
        }
        return self.env.ref('report_delegate_commission.printed_delegate_commission').report_action(self, data=data)
