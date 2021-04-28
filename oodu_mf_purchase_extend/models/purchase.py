from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    category_id = fields.Many2many('res.partner.category', related="partner_id.category_id",string="Tags")
