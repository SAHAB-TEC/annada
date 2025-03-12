# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MrpProductionStopWizard(models.TransientModel):
    _name = 'mrp.production.stop.wizard'
    _description = _('MrpProductionStopWizard')

    stop_id = fields.Many2one('mrp.production.stop', string="Stop Record", required=True)

    stop_reason = fields.Text(string="Reason for Stop", required=True)

    def confirm_stop(self):
        """Record the stop reason and time"""
        self.ensure_one()
        self.stop_id.stop_reason = self.stop_reason
