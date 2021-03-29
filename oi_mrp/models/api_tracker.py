# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ApiTracker(models.Model):
    _name = 'oi.api.tracker'
    _description = 'Api Tracker'

    name = fields.Char("Api Name")
    request_body = fields.Text("Request Body")
    response = fields.Text("Response")
