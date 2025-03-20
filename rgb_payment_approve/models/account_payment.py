# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    can_confirm = fields.Boolean(compute='_compute_can_confirm', default=False)
    # PaymentApproveRequest
    payment_approve_request_ids = fields.One2many('payment.approve.request', 'payment_id', string="Request Approve")
    
    @api.depends('create_date', 'write_date', 'create_uid', 'write_uid', 'payment_approve_request_ids', 'payment_approve_request_ids.state', 'payment_type')
    @api.onchange('create_date', 'write_date', 'create_uid', 'write_uid', 'payment_approve_request_ids', 'payment_approve_request_ids.state', 'payment_type')
    def _compute_can_confirm(self):
        for rec in self:
            if rec.payment_type == 'inbound':
                rec.can_confirm = True
                continue
            
            if     self.env.user.has_group('rgb_payment_approve.group_payment_approve_manager') \
                or self.env.user.has_group('rgb_payment_approve.group_payment_approve_user') \
                or self.env.user.has_group('rgb_payment_approve.group_payment_approve_manager2') \
                or self.env.user.has_group('rgb_payment_approve.group_payment_approve_user2'):
                    
                if self.env.user.has_group('rgb_payment_approve.group_payment_approve_general_manager'):
                    rec.can_confirm = True
                else:
                    approved = self.env['payment.approve.request'].search([('payment_id', '=', rec.id), ('state', '=', 'approved')])
                    if approved:
                        rec.can_confirm = True
                    else:
                        rec.can_confirm = False
            else:
                rec.can_confirm = True
    
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for rec in self:
            # check can approve
            if not rec.can_confirm:
                raise UserError(_("You can't approve this payment :( %s )", rec.name))
        return res
            
    def get_manager(self):
        # return system admin
        return self.env.ref('base.user_admin').email
        
    def action_request_approve(self):
        for rec in self:
            
            group_system = self.env.ref('base.group_system')
            group_manager = False
            self._send_notify_to_manager(rec.user_id)
            if self.env.user.has_group('rgb_payment_approve.group_payment_approve_user'):
                group_manager = self.env.ref('rgb_payment_approve.group_payment_approve_manager')
            if self.env.user.has_group('rgb_payment_approve.group_payment_approve_user2'):
                group_manager = self.env.ref('rgb_payment_approve.group_payment_approve_manager2')
            if self.env.user.has_group('rgb_payment_approve.group_payment_approve_manager') or self.env.user.has_group('rgb_payment_approve.group_payment_approve_manager2'):
                group_manager = self.env.ref('rgb_payment_approve.group_payment_approve_general_manager')
            
            if not group_manager:
                group_manager = self.env.ref('base.group_system')
            direct_manager = self.env['res.users'].search([('groups_id', 'in', group_manager.id)], limit=1)
            if not direct_manager:
                direct_manager = self.env['res.users'].search([('groups_id', 'in', group_system.id)], limit=1)
                
            request = self.env['payment.approve.request'].create({
                'user_id': self.env.user.id,
                'manager_id': direct_manager.id,
                'payment_id': rec.id
            })
            # notify the manager
            
            # create activity
            activity_data = {
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'res_id': request.id,
                'res_model_id': self.env.ref('rgb_payment_approve.model_payment_approve_request').id,
                'summary': _('Payment Approve Request'),
                'user_id': direct_manager.id,
                'date_deadline': fields.Datetime.now(),
                'note': _('Please approve this payment'),
            }
            res = self.env['mail.activity'].sudo().create(activity_data)
            
    def _send_notify_to_manager(self, user):
        template_id = self.env.ref('rgb_payment_approve.email_template_payment_approve_request').id # FIXME: change email template
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
                

class PaymentApproveRequest(models.Model):
    _name = 'payment.approve.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    user_id = fields.Many2one('res.users', string="User")
    manager_id = fields.Many2one('res.users', string="Manager")
    payment_id = fields.Many2one('account.payment', string="Payment")
    message = fields.Text(string="Message")
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='new')
    
    
    def action_approve(self):
        for rec in self:
            rec.state = 'approved'
            
    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
    
    def action_set_to_new(self):
        for rec in self:
            rec.state = 'new'

