# -*- coding: utf-8 -*-

from functools import wraps
from odoo import http
from odoo.http import Controller, Response, request, route


def has_valid_token(api_fun):

    @wraps(api_fun)
    def wrapper(api_req, *args, **kwargs):
        authorization_header = request.httprequest.headers.get('Authorization')
        auth_type, access_token = authorization_header.split(" ")
        uid = request.env['res.users'].sudo().search([('access_token', '=', access_token)])
        if uid:
            return api_fun(api_req, *args, **kwargs)
        else:
            return Response(response="Authentication failed!!", status=401)
    return wrapper
