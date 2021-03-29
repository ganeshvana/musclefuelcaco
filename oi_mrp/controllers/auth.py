# -*- coding: utf-8 -*-

from odoo.http import Controller, request, route


class LoginAuthentication(Controller):

    @route('/user/auth', type="json", auth='public', methods=["POST"], csrf=False)
    def authenticate_user(self):
        data = request.jsonrequest
        db = data.get("db")
        login = data.get("login")
        password = data.get("password")
        user_id = request.session.authenticate(db, login, password)
        res = {"msg": "Authentication failed"}
        if user_id:
            user = request.env['res.users'].browse(user_id)
            if user:
                access_token = user.sudo().generate_access_token()
                res = {"access_token": access_token,
                       "user_id": user_id}
        return res
