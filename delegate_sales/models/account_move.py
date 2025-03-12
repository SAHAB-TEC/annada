from odoo import _, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    hr_delegate_id = fields.Many2one(comodel_name='hr.employee', string='Delegate Commission', required=False)