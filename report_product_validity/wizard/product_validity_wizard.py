# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class BarcodeProductLabelsWiz(models.TransientModel):
    _name = "product.validity.wiz"
    _description = 'Product Validity Wizard'

    date_from = fields.Date(string="From", required=False, )
    date_to = fields.Date(string="To", required=False, )

    def print_product_validity(self):
        domain = []
        date_from = self.date_from
        if date_from:
            domain += [('expiration_date', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('expiration_date', '<=', date_to)]
        validity = self.env['stock.lot'].search_read(domain)
        # print("validity===>", validity)
        data = {
            'form': self.read()[0],
            'validity': validity,
        }
        return self.env.ref('report_product_validity.printed_product_validity').report_action(self, data=data)

    def action_view_expire(self):
        self.ensure_one()
        domain = []
        date_from = self.date_from
        if date_from:
            domain += [('expiration_date', '>=', date_from)]
        date_to = self.date_to
        if date_to:
            domain += [('expiration_date', '<=', date_to)]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expire',
            'view_mode': 'list',
            'view_id': self.env.ref('report_product_validity.view_stock_expire_tree').id,
            'res_model': 'stock.lot',
            'domain': [
                ('expiration_date', '>=', date_from),
                ('expiration_date', '<=', date_to),
            ],
            'context': "{'create': False}"
        }
