from odoo import models, fields, api
from odoo.tools.translate import _

class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'

    @api.model
    def _get_user(self):
        move_ids = self._context.get('active_ids', False)
        print ('move_ids',move_ids)
        user = ''
        res = self.env['account.move'].browse(move_ids)
        print ("ressssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",res.prepared_by_id)
        for rec in res:
            # self.prepared_by_id = res.prepared_by_id.id
            user = res.prepared_by_id.id
            # rec.write({'prepared_by_id':res.prepared_by_id.id})
        return user


    prepared_by_id = fields.Many2one('res.users', string='Prepared By', default=_get_user, store=True, copy=False, readonly=True)


    @api.multi
    def reverse_moves(self):
        ac_move_ids = self._context.get('active_ids', False)
        res = self.env['account.move'].browse(ac_move_ids).reverse_moves(self.date, self.journal_id, self.reason, self.prepared_by_id or False)
        if res:
            return {
                'name': _('Reverse Moves'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'domain': [('id', 'in', res)],
            }
        return {'type': 'ir.actions.act_window_close'}


    


    # @api.multi
    # def reverse_moves(self):
    #     ac_move_ids = self._context.get('active_ids', False)
    #     res = self.env['account.move'].browse(ac_move_ids).reverse_moves(self.date, self.journal_id or False)
    #     if res:
    #         return {
    #             'name': _('Reverse Moves'),
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'tree,form',
    #             'res_model': 'account.move',
    #             'domain': [('id', 'in', res)],
    #         }
    #     return {'type': 'ir.actions.act_window_close'}
