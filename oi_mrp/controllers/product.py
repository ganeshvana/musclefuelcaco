# -*- coding: utf-8 -*-

import json
from .token import has_valid_token
from odoo.http import Controller, Response, request, route


class ProductsApi(Controller):

    @route('/product/create', type="json", auth='public', methods=["POST"], csrf=False)
    @has_valid_token
    def add_product(self):
        data = request.jsonrequest
        api_tracker = request.env['oi.api.tracker'].sudo().create({
            'name': '/product/create',
            'request_body': data,
            'response': ''
        })
        if data:
            product_id = data.get('product_id')
            product = request.env["product.template"].sudo().search([('default_code', '=', product_id)])
            if product:
                return {"message": "Product With same ID already exist !"}
            else:
                details = {
                    "default_code": product_id,
                    "name": data.get("name"),
                    "type": 'product',
                    "sale_ok": True,
                    "purchase_ok": True,
                    "categ_id": data.get("category_id") if data.get("category_id") else 1,
                }

                product_obj = product.sudo().create(details)
                response = {"product_id": product_id,
                           "odoo_id": product_obj.id}

                return {"session_valid": True,
                        "response_code": 200,
                        "status": "success",
                        "message_code": "PRODUCT_CREATED",
                        "message": "Product created successfully.",
                        "payload": [response]}


class CategoryApi(Controller):

    @route('/category/create', type="json", auth='public', methods=["POST"], csrf=False)
    @has_valid_token
    def add_category(self):
        data = request.jsonrequest
        api_tracker = request.env['oi.api.tracker'].sudo().create({
            'name': '/category/create',
            'request_body': data,
            'response': ''
        })
        if data:
            category_id = data.get('category_id')
            parent_category_id = data.get('parent_category_id')
            category = request.env["product.category"].sudo().search([('default_code', '=', category_id)])
            if parent_category_id:
                parent_category = request.env["product.category"].sudo().search([('default_code', '=', parent_category_id)]).id
            else:
                parent_category = False
            if category:
                return {"message": "Category With same ID already exist !"}
            else:
                details = {
                    "default_code": category_id,
                    "name": data.get("name"),
                    "property_cost_method": 'standard',
                    "property_valuation": 'manual_periodic',
                    "parent_id": parent_category,
                }

                category_obj = category.sudo().create(details)
                response = {"product_id": category_id,
                           "odoo_id": category_obj.id}

                return {"session_valid": True,
                        "response_code": 200,
                        "status": "success",
                        "message_code": "CATEGORY_CREATED",
                        "message": "Category created successfully.",
                        "payload": [response]}
