from odoo import models, fields, api, _

class Uom(models.Model):
    _inherit = 'uom.uom'

    is_main_uom = fields.Boolean(string='Is Main UOM', default=False)