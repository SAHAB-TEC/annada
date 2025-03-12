# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductChangeUom(models.TransientModel):
    _name = 'product.change.uom'
    _description = _('ProductChangeUom')

    product_ids = fields.Many2many('product.product', string='Products')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    
    def action_change_uom(self):
        uom_id = self.uom_id
        iom_category = uom_id.category_id
        prods = self.product_ids.filtered(lambda p: p.uom_id.category_id == iom_category)
        if prods and len(prods) > 0:
            prods.sudo().write({
                'secondary_product_uom_id': uom_id.id,
            })

        return {'type': 'ir.actions.act_window_close'}
