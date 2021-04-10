# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import requests
import json
from ast import literal_eval


class ProductCategory(models.Model):
    _inherit = 'mrp.production'

    def get_data_from_musclefuel(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('musclefuel.api_url')
        jwt_token = "3726fa0d2ae0550da60b39a42dc4408c"
        date = str(fields.Date.today())
        headers = {"given_date": date,
                   "secret_key": jwt_token}
        url = base_url + 'oodoOrderDetailsperdate/' + json.dumps(headers)
        r = requests.get(url, timeout=30)
        result = literal_eval(r.text)
        if 'data' in result:
            print(result['data'])
            for line in result['data']:
                product_obj = self.env['product.product'].search([('id', '=', int(line['productId']))])
                if product_obj:
                    data = {
                        'product_id': product_obj.id,
                        'product_uom_id': product_obj.uom_id.id,
                        'product_qty': int(line['cnt'])
                    }
                    MO = self.env['mrp.production'].sudo().create(data)
                    print(MO.name)
                else:
                    pass
            return True
