# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools
from odoo.exceptions import ValidationError
import requests
import json
from ast import literal_eval

import logging
import threading

_logger = logging.getLogger(__name__)


class MRPOrders(models.TransientModel):
    _name = 'mrp.order.compute'
    _description = 'Run Fetch Manually'

    date = fields.Date("Date")

    def get_data_from_musclefuel(self, date=False):
        base_url = self.env['ir.config_parameter'].sudo().get_param('musclefuel.api_url')
        jwt_token = "3726fa0d2ae0550da60b39a42dc4408c"
        if not self.date:
            date = str(fields.Date.today())
        else:
            date = str(self.date)

        headers = {"given_date": date,
                   "secret_key": jwt_token}
        url = base_url + 'oodoOrderDetailsperdate/' + json.dumps(headers)
        r = requests.get(url, timeout=30)
        result = literal_eval(r.text)
        if 'data' in result:
            _logger.info('order data %s', result)
            print(result['data'])
            for line in result['data']:
                product_obj = self.env['product.product'].search([('default_code', '=', line['productId'])])
                if product_obj:
                    bom = self.env['mrp.bom']._bom_find(product=product_obj, bom_type='normal')
                    if bom:
                        bom_id = bom.id
                    else:
                        bom_id = False
                    data = {
                        'bom_id': bom_id,
                        'product_id': product_obj.id,
                        'date_planned_start': date,
                        'product_uom_id': product_obj.uom_id.id,
                        'product_qty': int(line['cnt']),
                        'total_carbs': str(line['carbs_amount']),
                        'total_proteins': str(line['proteins_amount'])
                    }
                    MO = self.env['mrp.production'].sudo().create(data)
                    print(MO.name)
                    if MO.bom_id and MO.product_qty > 0:
                        # keep manual entries
                        list_move_raw = [(4, move.id) for move in
                                         MO.move_raw_ids.filtered(lambda m: not m.bom_line_id)]
                        moves_raw_values = MO._get_moves_raw_values()
                        move_raw_dict = {move.bom_line_id.id: move for move in
                                         MO.move_raw_ids.filtered(lambda m: m.bom_line_id)}
                        for move_raw_values in moves_raw_values:
                            if move_raw_values['bom_line_id'] in move_raw_dict:
                                # update existing entries
                                list_move_raw += [
                                    (1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                            else:
                                # add new entries
                                list_move_raw += [(0, 0, move_raw_values)]
                        MO.move_raw_ids = list_move_raw
                else:
                    pass
            return True
