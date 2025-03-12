from odoo import models, fields, api, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    delegate_id = fields.Many2one(comodel_name="hr.employee", string="Delegate", required=False,
                                  domain="[('salesperson', '=', True)]")