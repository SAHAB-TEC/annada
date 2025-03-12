# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Saneen K (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models


class ProductProduct(models.Model):
    """Inherits the 'product.template' for adding the secondary uom"""
    _inherit = "product.product"

    is_need_secondary_uom = fields.Boolean(string="Need Secondary UoM's",
                                           help="Enable this field for "
                                                "using the secondary uom")
    secondary_uom_ids = fields.One2many('secondary.uom.line', 'product_id',
                                        string="Secondary UoM's",
                                        help='Select the secondary UoM and '
                                             'their ratio', store=True)

    @api.onchange('is_need_secondary_uom')
    def _onchange_is_need_secondary_uom(self):
        """Function that write the default Uom and their ratio to the
        secondary uom"""
        base_uom = self.env['uom.uom'].sudo().search(
                [('category_id', '=', self.uom_id.category_id.id)])
        if not self.secondary_uom_ids:
            for uom in base_uom:
                self.write({
                    'secondary_uom_ids': [(0, 0, {
                        'secondary_uom_id': uom.id,
                        'secondary_uom_ratio': float(uom.factor_inv),
                        'example_ratio': f" 1 {uom.name} = {uom.factor_inv}"
                                         f" {self.uom_id.name}",
                    })]
                })

    secondary_product_uom_id = fields.Many2one(
        'uom.uom', string='UoM',
        store=True, readonly=False,
        help="Select the Secondary Uom",
        default=lambda self: self.uom_id,
        domain="[('id', 'in', secondary_uom_ids)]")

    secondary_on_hand = fields.Float(string='On Hand',
                                     compute='_compute_secondary_on_hand',
                                     help="Secondary On Hand Quantity",
                                     store=True)
    secondary_free_qty = fields.Float(string='Free Quantity',
                                      compute='_compute_secondary_free_qty',
                                      help="Secondary Free Quantity",
                                      store=True)
    secondary_income_qty = fields.Float(string='Incoming Quantity',
                                        compute='_compute_secondary_income_qty',
                                        help="Secondary Incoming Quantity",
                                        store=True)
    secondary_outgoing_qty = fields.Float(string='Outgoing Quantity',
                                          compute='_compute_secondary_outgoing_qty',
                                          help="Secondary Outgoing Quantity",
                                          store=True)
    secondary_forecast_qty = fields.Float(string='Forecast Quantity',
                                          compute='_compute_secondary_forecast_qty',
                                          help="Secondary Forecast Quantity",
                                          store=True)

    @api.depends('secondary_product_uom_id')
    def _compute_secondary_on_hand(self):
        for rec in self:
            on_hand = rec.qty_available
            main_uom = rec.uom_id
            secondary_uom = rec.secondary_product_uom_id
            if main_uom and secondary_uom:
                on_hand = main_uom._compute_quantity(
                    on_hand, secondary_uom)
            rec.secondary_on_hand = on_hand

    @api.depends('secondary_product_uom_id')
    def _compute_secondary_free_qty(self):
        for rec in self:
            free_qty = rec.free_qty
            main_uom = rec.uom_id
            secondary_uom = rec.secondary_product_uom_id
            if main_uom and secondary_uom:
                free_qty = main_uom._compute_quantity(free_qty, secondary_uom)
            rec.secondary_free_qty = free_qty

    @api.depends('secondary_product_uom_id')
    def _compute_secondary_income_qty(self):
        for rec in self:
            income_qty = rec.incoming_qty
            main_uom = rec.uom_id
            secondary_uom = rec.secondary_product_uom_id
            if main_uom and secondary_uom:
                income_qty = main_uom._compute_quantity(income_qty, secondary_uom)
            rec.secondary_income_qty = income_qty

    @api.depends('secondary_product_uom_id')
    def _compute_secondary_outgoing_qty(self):
        for rec in self:
            outgoing_qty = rec.outgoing_qty
            main_uom = rec.uom_id
            secondary_uom = rec.secondary_product_uom_id
            if main_uom and secondary_uom:
                outgoing_qty = main_uom._compute_quantity(
                    outgoing_qty, secondary_uom)
            rec.secondary_outgoing_qty = outgoing_qty

#     forecasting
    @api.depends('secondary_product_uom_id')
    def _compute_secondary_forecast_qty(self):
        for rec in self:
            forecast_qty = rec.virtual_available
            main_uom = rec.uom_id
            secondary_uom = rec.secondary_product_uom_id
            if main_uom and secondary_uom:
                forecast_qty = main_uom._compute_quantity(
                    forecast_qty, secondary_uom)
            rec.secondary_forecast_qty = forecast_qty


class ProductTemplate(models.Model):
    """Inherits the 'product.template' for adding the secondary uom"""
    _inherit = "product.template"

    is_need_secondary_uom = fields.Boolean(string="Need Secondary UoM's",
                                           help="Enable this field for "
                                                "using the secondary uom")
    secondary_uom_ids = fields.One2many('secondary.uom.line', 'product_tmpl_id',
                                        string="Secondary UoM's",
                                        help='Select the secondary UoM and '
                                             'their ratio', store=True)




    @api.onchange('is_need_secondary_uom')
    def _onchange_is_need_secondary_uom(self):
        """Function that write the default Uom and their ratio to the
        secondary uom"""
        base_uom = self.env['uom.uom'].sudo().search(
                [('category_id', '=', self.uom_id.category_id.id)])
        if not self.secondary_uom_ids:
            for uom in base_uom:
                self.write({
                    'secondary_uom_ids': [(0, 0, {
                        'secondary_uom_id': uom.id,
                        'secondary_uom_ratio': float(uom.factor_inv),
                        'example_ratio': f" 1 {uom.name} = {uom.factor_inv}"
                                         f" {self.uom_id.name}",
                    })]
                })