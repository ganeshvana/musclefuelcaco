# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockValUpdate(models.TransientModel):
    _name = 'stock.val.update'
    _description = "Stock Val Update"   
    
    date = fields.Datetime('Date')
                
    def update_date(self):        
        context = self._context
        active_ids = context['active_ids']  
        for val in active_ids:
            rec = self.env['stock.valuation.layer'].browse(val)
            rec .create_date = self.date
            self._cr.execute("Update stock_valuation_layer set create_date = %s WHERE id=%s", (self.date,rec.id,))
        
    
    