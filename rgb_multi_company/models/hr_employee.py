from odoo import api, models, fields, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def get_company_domain(self):
        return [('id', 'in', self.env.company.ids)]

    company_id = fields.Many2one(domain=lambda self: self.get_company_domain())
