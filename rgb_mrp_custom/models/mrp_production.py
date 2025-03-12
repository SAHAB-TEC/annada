# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Datetime
from odoo.tools.safe_eval import datetime

_logger = logging.getLogger(__name__)


class MrpProductionStop(models.Model):
    _name = "mrp.production.stop"
    _description = "Manufacturing Order Stop Record"

    mo_id = fields.Many2one(
        "mrp.production",
        string="Manufacturing Order",
        required=True,
        ondelete="cascade",
    )
    start_time = fields.Datetime(
        string="Stopped From", required=True
    )  # 🕒 When the stop started
    end_time = fields.Datetime(string="Stopped To")  # 🕒 When the stop ended
    stop_reason = fields.Text(string="Reason for Stop")  # ✍️ Reason for stopping

    duration = fields.Float(
        string="Duration (Hours)", compute="_compute_duration", store=True
    )

    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                duration = (
                    record.end_time - record.start_time
                ).total_seconds() / 3600.0
                record.duration = round(duration, 2)
            else:
                record.duration = 0.0


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    shift_name = fields.Selection(
        [
            ("morning", "Morning"),
            ("afternoon", "Afternoon"),
            ("night", "Night"),
        ],
        string="Shift",
        default="morning",
    )

    date_done = fields.Datetime(
        string="Date Done", copy=False, default=fields.Datetime.now
    )
    day_done = fields.Char(
        string="Day Done", copy=False, compute="_compute_day_done", store=True
    )
    day_done_name = fields.Char(
        string="Day Name", copy=False, compute="_compute_day_name", store=True
    )

    recipient_job_name = fields.Char(
        string="Recipient Job Name",
        copy=False,
        compute="_compute_recipient_job_name",
        store=False,
    )
    deliverer_job_name = fields.Char(
        string="Deliverer Job Name",
        copy=False,
        compute="_compute_deliverer_job_name",
        store=False,
    )

    main_qty = fields.Float(
        string="Main Qty", copy=False, compute="_compute_main_qty", store=False
    )

    def _compute_main_qty(self):
        for rec in self:
            rec.main_qty = sum(rec.backorder_ids.mapped("product_qty"))

    # @api.depends('user_id')
    def _compute_deliverer_job_name(self):
        for rec in self:
            rec.deliverer_job_name = rec.user_id.employee_id.job_id.name

    # @api.depends('delegate_id')
    def _compute_recipient_job_name(self):
        for rec in self:
            rec.recipient_job_name = rec.delegate_id.job_id.name

    @api.depends("date_done")
    def _compute_day_name(self):
        for rec in self:
            rec.day_done_name = rec.date_done.strftime("%A") if rec.date_done else False

    can_edit_date_done = fields.Boolean(
        compute="_compute_can_edit_date_done", store=False
    )

    @api.depends("date_done")
    def _compute_day_done(self):
        for rec in self:
            rec.day_done = rec.date_done.strftime("%A") if rec.date_done else False

    def _compute_can_edit_date_done(self):
        for rec in self:
            if self.env.user.has_group("rgb_mrp_custom.group_production__edit_date"):
                rec.can_edit_date_done = True
            else:
                rec.can_edit_date_done = False

    is_timer_running = fields.Boolean(string="Timer Running", default=False)
    last_timer_start = fields.Datetime(string="Last Timer Start")
    total_duration = fields.Float(
        string="Total Time (Hours)", compute="_compute_total_duration", store=True
    )

    timesheet_ids = fields.One2many(
        "account.analytic.line", "mo_id", string="Timesheets"
    )
    stop_times = fields.One2many("mrp.production.stop", "mo_id", string="Stop Times")
    current_stop_id = fields.Many2one(
        "mrp.production.stop", string="Current Stop Record"
    )  # Active stop

    @api.depends("timesheet_ids.unit_amount")
    def _compute_total_duration(self):
        for record in self:
            record.total_duration = sum(record.timesheet_ids.mapped("unit_amount"))

    def action_start_timer(self):
        """Start the timer"""
        self.ensure_one()
        if not self.is_timer_running:
            self.is_timer_running = True
            self.last_timer_start = Datetime.now()
    #     update stop end time
        if self.current_stop_id:
            self.current_stop_id.end_time = fields.Datetime.now()

    def action_pause_timer(self):
        """Pause the timer and create a timesheet entry"""
        self.ensure_one()
        if self.is_timer_running and self.last_timer_start:
            time_spent = (
                Datetime.now() - self.last_timer_start
            ).total_seconds() / 3600.0
            self.env["account.analytic.line"].create(
                {
                    "name": f"Timesheet for {self.name}",
                    "mo_id": self.id,
                    "date": fields.Datetime.now(),
                    "unit_amount": time_spent,
                    "employee_id": self.env.user.employee_id.id,
                }
            )
            self.is_timer_running = False
            self.last_timer_start = False

    def action_resume_timer(self):
        """End the current stop session"""
        self.ensure_one()
        if self.current_stop_id:
            self.current_stop_id.end_time = fields.Datetime.now()  # Record end time
            self.current_stop_id = False  # Clear the active stop

    def action_stop_timer(self):
        """Stop the timer and finalize timesheets"""
        self.action_pause_timer()  # Ensure the last time is recorded
        self.is_timer_running = False

        self.ensure_one()

        stop = self.env["mrp.production.stop"].create(
            {
                "mo_id": self.id,
                "start_time": fields.Datetime.now(),  # Record start time
            }
        )
        self.current_stop_id = stop.id
        self.stop_times |= stop

        return {
            "name": "Stop Timer",
            "type": "ir.actions.act_window",
            "res_model": "mrp.production.stop.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_stop_id": self.current_stop_id.id},
        }
