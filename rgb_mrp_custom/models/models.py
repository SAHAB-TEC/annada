# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class rgb_mrp_custom(models.Model):
#     _name = 'rgb_mrp_custom.rgb_mrp_custom'
#     _description = 'rgb_mrp_custom.rgb_mrp_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
