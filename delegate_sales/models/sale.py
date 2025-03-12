# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    salesperson = fields.Boolean(string="SalesPerson", )
    commission_delegate_ids = fields.One2many(comodel_name='commission.delegate', inverse_name='hr_delegate_id',
                                              string='Commission', required=False)
    region_line_ids = fields.One2many(comodel_name='delegate.region.lines', inverse_name='delegate_id', string='Region',)

    max_sale_amount = fields.Float(string='Max Sale Amount', required=False)

    mrp_ids = fields.One2many(comodel_name='mrp.production', inverse_name='delegate_id', string='MRP', required=False)

    def print_aged_receivable_report(self):
        # Fetch data for the report
        contact_ids = self.env['res.partner'].search([('delegate_id', '=', self.id)])
        data = self.env['aged.receivable.report'].get_aged_receivable_data(contact_ids.ids)

        if not data:
            # Handle the case where no data is found
            raise UserError("No outstanding invoices found for this partner.")
        # Create a transient record for the report
        report = self.env['aged.receivable.report'].create(data)
        # Return the report action
        return self.env.ref('delegate_sales.action_aged_receivable_report').report_action(report)

class DelegateCommission(models.Model):
    _name = 'commission.delegate'
    _order = 'amount desc'

    hr_delegate_id = fields.Many2one(comodel_name='hr.employee', string='Delegate Commission', required=False)
    amount = fields.Float(string='Amount', required=False)
    percentage = fields.Float(string='percent', required=False)


class DelegateRegion(models.Model):
    _name = 'delegate.region'
    name = fields.Char(string='Region', required=False)

class DelegateRegionLines(models.Model):
    _name = 'delegate.region.lines'

    region_id = fields.Many2one(comodel_name='delegate.region', string='Region', required=False)
    delegate_id = fields.Many2one(comodel_name='hr.employee', string='Delegate', required=False)

class AgedReceivableReport(models.TransientModel):
    _name = 'aged.receivable.report'
    _description = 'Aged Receivable Report'

    partner_id = fields.Many2one('res.partner', string='Partner')
    invoice_date = fields.Date(string='Invoice Date')
    amount = fields.Float(string='Amount')
    currency_id = fields.Many2one('res.currency', string='Currency')
    account_id = fields.Many2one('account.account', string='Account')
    expected_date = fields.Date(string='Expected Date')
    aging_1_30 = fields.Float(string='1-30 Days')
    aging_31_60 = fields.Float(string='31-60 Days')
    aging_61_90 = fields.Float(string='61-90 Days')
    aging_91_120 = fields.Float(string='91-120 Days')
    aging_over_120 = fields.Float(string='Over 120 Days')
    total = fields.Float(string='Total')

    @api.model
    def get_aged_receivable_data(self, partner_ids):
        # Ensure partner_ids is a tuple
        if isinstance(partner_ids, list):
            partner_ids = tuple(partner_ids)
        elif isinstance(partner_ids, int):
            partner_ids = (partner_ids,)
        elif not partner_ids:
            return []  # Return empty list if no partner IDs are provided

        # Query to fetch outstanding invoices for the partner(s)
        query = """
            SELECT am.invoice_date,
                   am.amount_total AS amount,
                   am.currency_id,
                   am.partner_id,
                   am.invoice_date_due AS expected_date,
                   CASE
                       WHEN EXTRACT(DAY FROM age(am.invoice_date_due, CURRENT_DATE)) BETWEEN 0 AND 30 THEN am.amount_residual
                       ELSE 0
                   END AS aging_1_30,
                   CASE
                       WHEN EXTRACT(DAY FROM age(am.invoice_date_due, CURRENT_DATE)) BETWEEN 31 AND 60 THEN am.amount_residual
                       ELSE 0
                   END AS aging_31_60,
                   CASE
                       WHEN EXTRACT(DAY FROM age(am.invoice_date_due, CURRENT_DATE)) BETWEEN 61 AND 90 THEN am.amount_residual
                       ELSE 0
                   END AS aging_61_90,
                   CASE
                       WHEN EXTRACT(DAY FROM age(am.invoice_date_due, CURRENT_DATE)) BETWEEN 91 AND 120 THEN am.amount_residual
                       ELSE 0
                   END AS aging_91_120,
                   CASE
                       WHEN EXTRACT(DAY FROM age(am.invoice_date_due, CURRENT_DATE)) > 120 THEN am.amount_residual
                       ELSE 0
                   END AS aging_over_120,
                   am.amount_residual AS total
            FROM account_move am
            WHERE am.partner_id IN %s 
              AND am.move_type = 'out_invoice' 
              AND am.amount_residual > 0 
              AND am.state = 'posted'
        """
        self.env.cr.execute(query, (partner_ids,))
        results = self.env.cr.dictfetchall()
        return results

class ResPartner(models.Model):
    _inherit = 'res.partner'

    delegate_id = fields.Many2one(comodel_name="hr.employee", string="Delegate", required=False,
                                  domain="[('salesperson', '=', True)]")

    def print_aged_receivable_report(self):
        # Fetch data for the report
        data = self.env['aged.receivable.report'].get_aged_receivable_data(self.id)

        if not data:
            # Handle the case where no data is found
            raise UserError("No outstanding invoices found for this partner.")
        # Create a transient record for the report
        report = self.env['aged.receivable.report'].create(data)
        # Return the report action
        return self.env.ref('delegate_sales.action_aged_receivable_report').report_action(report)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    region = fields.Char(related='partner_id.street2', string='Region', readonly=False, )
    delegate_sale_id = fields.Many2one(related='partner_id.delegate_id', string='Delegate', readonly=False, )
    paid = fields.Float(compute='_paid_total', string="Paid", required=False, )
    remaining_amount = fields.Float(compute='_remaining_total', string="Remaining Amount", required=False, )
    cash = fields.Selection(string='Cash', selection=[('cash', 'Cash')], required=False, )

    def _remaining_total(self):
        for rec in self:
            rec.remaining_amount = rec.amount_total - rec.paid

    def _paid_total(self):
        for ret in self:
            invoices = ret.env['account.move'].search([('name', '=', ret.invoice_ids.name)])

            paid = 0.0
            for rec in invoices:
                paid += rec.amount_total - rec.amount_residual

            ret.paid = paid


class HrContract(models.Model):
    _inherit = 'hr.contract.history'
    _description = 'Employee Contract'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account', check_company=True)
