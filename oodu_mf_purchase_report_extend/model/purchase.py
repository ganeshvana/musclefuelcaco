from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp



class purchase_order(models.Model):
    _inherit = "purchase.order"
 
    mo_product = fields.Char("MO Product",compute="_get_mo_product")   
    despatch_through = fields.Char(string="Despatch Through")
    due_date = fields.Date("Due Date")

    @api.one
    @api.depends('origin')
    def _get_mo_product(self):
        for order in self:
            if self.origin:
                mo = self.env['mrp.production'].search([('name', '=', self.origin)])
                if mo:
                	self.mo_product = mo.product_id.name
                else:
                    self.mo_product = ''

    @api.multi
    def action_mo(self):
        for order in self:
            for line in order.order_line:
                if order.mo_product:
                    line.write({'name':order.mo_product})




class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"
 
   
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Purchase Price'))


class accoount_invoice_line(models.Model):
    _inherit = "account.invoice.line"
 
   
    price_unit = fields.Float(string='Price', required=True, digits=dp.get_precision('Purchase Price'))


# class stock_picking(models.Model):
#     _inherit = "stock.picking"

#     date_done = fields.Datetime('Date of Transfer', copy=False, readonly=False, help="Date at which the transfer has been processed or cancelled.")




   
