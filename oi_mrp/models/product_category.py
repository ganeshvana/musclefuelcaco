# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    default_code = fields.Char("Unique Code")

    _sql_constraints = [
        ('unique_default_code', 'unique (default_code)', 'category with this default code already exists!')
    ]
