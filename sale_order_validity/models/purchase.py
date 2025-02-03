# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    expired_date = fields.Datetime(string="Expired", required=False, )
    list_price = fields.Float(related='product_id.lst_price', string='Sale Price', readonly=False, )
