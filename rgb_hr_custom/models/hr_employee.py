# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = _('HrEmployee')
    
    university = fields.Char(string='University')
    faculty = fields.Char(string='Faculty')
    department = fields.Char(string='Department')

    release_date = fields.Date(string='Release Date')
    expiration_date = fields.Date(string='Expiration Date')
    national_id = fields.Char(string='National ID')
    
    city_of_birth = fields.Char(string='City')
    municipal = fields.Char(string='Municipal/Region')
    district = fields.Char(string='District')
    
    administration = fields.Char('Administration')
    job_title = fields.Char('Job Title')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    years_of_experience = fields.Integer('Years of Experience')
    phone_1 = fields.Char('Phone 1')
    phone_2 = fields.Char('Phone 2')
    
    other_work_location_id = fields.Many2one('hr.work.location', string='Other Work Location')


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    timesheet_manager_id = fields.Many2one('hr.employee', string='Timesheet Manager')

