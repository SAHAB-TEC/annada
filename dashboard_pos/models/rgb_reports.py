from odoo import models, fields, api
from odoo.osv import expression


class RGBReports(models.Model):
    _name = 'rgb.reports'
    _description = 'RGB Reports'

    @api.model
    def get_mrp_dashboard_data(self, date_from, date_to):
        test_mrp_dashboard_data = []
        if not date_from or not date_to:
            date_from = fields.Date.today().replace(month=1, day=1)
            date_to = fields.Date.today().replace(month=12 ,day=31)
        else:
            date_from_str = date_from
            date_to_str = date_to
            date_from = fields.Date.from_string(date_from)
            date_to = fields.Date.from_string(date_to)

        datetime_from = fields.Datetime.from_string(date_from).replace(hour=0, minute=0, second=0)
        datetime_to = fields.Datetime.from_string(date_to).replace(hour=23, minute=59, second=59)

        # Get the data from the database
        all_mrp = self.env['mrp.production'].search([
            ('date_finished', '>=', datetime_from),
            ('date_finished', '<=', datetime_to),
            ('state', '=', 'done')
        ])
        # group it by product_name and sum product_qty TODO:
        grouped_list = []

        for mrp in all_mrp.mapped('product_id'):
            qty = sum(all_mrp.filtered(lambda x: x.product_id == mrp).mapped('product_qty'))
            test_mrp_dashboard_data.append({
                'product_name': mrp.name,
                'value': qty
            })

        return {
            'mrp_dashboard_data': test_mrp_dashboard_data
        }


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def rgb_get_bank_cash_dashboard_data(self):

        """Populate all bank and cash journal's data dict with relevant information for the kanban card."""
        bank_cash_journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
        if not bank_cash_journals:
            return

        # Number to reconcile
        self._cr.execute("""
            SELECT st_line_move.journal_id,
                   COUNT(st_line.id)
              FROM account_bank_statement_line st_line
              JOIN account_move st_line_move ON st_line_move.id = st_line.move_id
             WHERE st_line_move.journal_id IN %s
               AND NOT st_line.is_reconciled
               AND st_line_move.to_check IS NOT TRUE
               AND st_line_move.state = 'posted'
               AND st_line_move.company_id IN %s
          GROUP BY st_line_move.journal_id
        """, [tuple(bank_cash_journals.ids), tuple(self.env.companies.ids)])

        # Last statement
        bank_cash_journals.last_statement_id.mapped(lambda s: s.balance_end_real)  # prefetch

        outstanding_pay_account_balances = bank_cash_journals._get_journal_dashboard_outstanding_payments()

        journal_list = []
        for journal in bank_cash_journals:
            currency = journal.currency_id or self.env['res.currency'].browse(journal.company_id.sudo().currency_id.id)
            has_outstanding, outstanding_pay_account_balance = outstanding_pay_account_balances[journal.id]

            journal_list.append({
                "journal_name": journal.display_name,
                'balance': currency.format(outstanding_pay_account_balance),
                'company': journal.company_id.name,
            })

        return {

            "journal_balance": journal_list
        }
