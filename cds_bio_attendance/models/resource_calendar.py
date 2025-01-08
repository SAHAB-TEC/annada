# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (c) 2021 CDS Solutions SRL. (http://cdsegypt.com)
#    Maintainer: Eng.Ramadan Khalil (<ramadan.khalil@cdsegypt.com>)
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    day_start_delay = fields.Float('Start Day Delay', default=0)
    normal_working_hours = fields.Float('Normal Working Hours', default=0)
    min_working_hours = fields.Float('Minimum Working Hours', default=0)
    flex_line_ids = fields.One2many('resource.calendar.flex',
                                    inverse_name='calendar_id',
                                    string='Flexable Hours Per Day')


class ResourceCalendarflex(models.Model):
    _name = "resource.calendar.flex"

    calendar_id = fields.Many2one('resource.calendar', 'Calendar')

    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, default='0')
    min_working_hours = fields.Float('Minimum Working Hours', default=0)
    normal_working_hours = fields.Float('Normal Working Hours', default=0)
