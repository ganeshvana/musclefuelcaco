# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import re

class PrintJournalEntries(models.Model):
    _inherit = 'account.move'


    bank_ifc = fields.Char(string='Bank IFSC',readonly=True)
    acc_number_id = fields.Many2one('res.partner.bank' ,string='Bank Acc No',readonly=True)
    mode_type = fields.Selection([('RTGS', 'RTGS'), ('NEFT', 'NEFT'), ('DCR', 'DCR'), ('ONLINE_TRANSFER', 'ONLINE TRANSFER'), ('SWIFT', 'SWIFT'),('CHEQUE', 'CHEQUE')],string='Mode Type',readonly=True)
    reason = fields.Text(string='Reason',readonly=True)
    crossing = fields.Char('Crossing',readonly=True)
    partner_name = fields.Char('Payee Name',readonly=True)

    def print_journal_entries(self):
        return self.env.ref('de_print_journal_entries.action_journal_entries_report').report_action(self)



    @api.multi
    def _reverse_move(self, date=None, journal_id=None, reason=None, prepared_by_id=None, auto=False):
        self.ensure_one()
        date = date or fields.Date.today()
        if date < self.date_post_direct_journal:
            raise UserError(_('Reverse date cannot be prior to posted date'))

        with self.env.norecompute():
            reversed_move = self.copy(default={
                'date': date,
                'journal_id': journal_id.id if journal_id else self.journal_id.id,
                'reason': reason if reason else self.reason,
                'date_post_direct_journal':date,
                'prepared_by_id': prepared_by_id.id if prepared_by_id else self.prepared_by_id.id,
                'ref': (_('Automatic reversal of: %s') if auto else _('Reversal of: %s')) % (self.name),
                'auto_reverse': False})
            for acm_line in reversed_move.line_ids.with_context(check_move_validity=False):
                acm_line.write({
                    'debit': acm_line.credit,
                    'credit': acm_line.debit,
                    'amount_currency': -acm_line.amount_currency
                })
            self.reverse_entry_id = reversed_move
        self.recompute()
        return reversed_move

    @api.multi
    def reverse_moves(self, date=None, journal_id=None, reason=None, prepared_by_id=None, auto=False):

        date = date or fields.Date.today()
        reversed_moves = self.env['account.move']
        for ac_move in self:
            # unreconcile all lines reversed
            aml = ac_move.line_ids.filtered(
                lambda x: x.account_id.reconcile or x.account_id.internal_type == 'liquidity')
            aml.remove_move_reconcile()
            reversed_move = ac_move._reverse_move(date=date,
                                                  journal_id=journal_id,reason=reason,prepared_by_id=prepared_by_id,
                                                  auto=auto)
            reversed_moves |= reversed_move


            # reconcile together the reconcilable (or the liquidity aml) and their newly created counterpart
            for account in set([x.account_id for x in aml]):
                to_rec = aml.filtered(lambda y: y.account_id == account)
                to_rec |= reversed_move.line_ids.filtered(lambda y: y.account_id == account)
                # reconciliation will be full, so speed up the computation by using skip_full_reconcile_check in the context
                to_rec.reconcile()

        if reversed_moves:
            reversed_moves._post_validate()
            reversed_moves.post()
            return [x.id for x in reversed_moves]
        return []

    # @api.multi
    # def post(self, invoice=False):
    #     res = super(PrintJournalEntries,self).post(invoice=False)
    #     for move in self:
    #         if move.date_post_direct_journal:
    #             move.write({'date_post_direct_journal':move.date_post_direct_journal,'verified_by_id':self.env.uid})
    #         else:
    #             move.write({'date_post_direct_journal':datetime.today(),'verified_by_id':self.env.uid})
    #     return res

    @api.multi
    def post(self, invoice=False):
        self._post_validate()
        for move in self:
            move.line_ids.create_analytic_lines()
            if move.date > fields.Date.today():
            	raise UserError(_('Entry cannot be posted in future date'))

            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the credit notes'))
                            sequence = journal.refund_sequence_id

                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date
            if move.date_post_direct_journal:
                move.write({'date_post_direct_journal':move.date_post_direct_journal,'verified_by_id':self.env.uid})
            else:
                move.write({'date_post_direct_journal':datetime.today(),'verified_by_id':self.env.uid})

            if not self.reason:
                if self.verified_by_id == self.prepared_by_id:
                    raise UserError(_('prepared by and verified by can not be same'))

        return self.write({'state': 'posted'})


    

    date_post_direct_journal = fields.Date('Posted Date',copy=False, readonly=True)

    date_post_from_invoice = fields.Date('Posted Date',readonly=True)
   

    prepared_by_id = fields.Many2one('res.users', string='Prepared By', default=lambda self: self.env.user, copy=False)

    verified_by_id = fields.Many2one('res.users', string='Verified By',copy=False)

    check_sign = fields.Boolean('Signature',default=False)


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    user_id = fields.Many2one('res.users', string='Preparer',default=lambda self: self.env.user, copy=False)
    acc_number_id = fields.Many2one('res.partner.bank',string='Bank Acc No')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', compute_sudo=True,
        related='partner_id.commercial_partner_id', store=True, readonly=True)
    bank_ifc = fields.Char(string='Bank IFSC', compute='_get_ifsc',readonly=True, store=True)
    acc_receivable = fields.Many2one('account.account' ,string='Account Receivable',required=True)
    acc_payable = fields.Many2one('account.account' ,string='Account Payable',store=True)
    reason = fields.Text(string='Narration')

    @api.onchange('bank_ifc')
    def SbiIfc(self):
        if self.bank_ifc:
            check = re.match('SBI', self.bank_ifc)
            if check:
                self.mode_type = 'DCR'
            else:
                self.mode_type = ''

    # @api.depends('acc_number_id')                            
    # @api.onchange('acc_number_id')
    # def _acc_number(self):
    #     self.write({'bank_ifc':self.acc_number_id.bank_id.bic})
    #     # self.bank_ifc =self.acc_number_id.bank_id.bic
    @api.multi
    @api.depends('acc_number_id')
    def _get_ifsc(self):
        for record in self:
            if record.acc_number_id:
                record.bank_ifc = record.acc_number_id.bank_id.bic

    @api.onchange('partner_id')
    def _bank_details(self):
        result = {}
        partner_bank_ids=[]
        if self.partner_id.bank_ids:
            self.bank_ifc = self.partner_id.bank_ids[0].bank_id.bic
            self.acc_number_id = self.partner_id.bank_ids[0]
            # self.bank_ifc = self.acc_numbesr_id.bank_id.bic
        
           
        if self.partner_id:
            if not self.partner_id.bank_ids and not self.commercial_partner_id.bank_ids: 
                print ("self.partner",self.partner_id.bank_ids,self.commercial_partner_id.bank_ids)
                self.bank_ifc = False
                self.acc_number_id = False
                # self.bank_line_ids = False
                result['warning'] = {
                    'title': _('Note'),
                    'message': _('There Is no bank details')}
            if not self.partner_id.bank_ids and self.commercial_partner_id.bank_ids:
                bank_ids = self.commercial_partner_id.bank_ids
                bank_id = bank_ids[0].id if bank_ids else False
                self.acc_number_id = bank_id
                domain = {'acc_number_id': [('id', 'in', bank_ids.ids)]}
        return result


    @api.constrains('communication')
    def _check_memo(self):
        for record in self:
            if record.communication and len(str(record.communication)) >= 31:
                raise ValidationError("Memo accepts only 30 characters, You can not confirm this payment.")


    def _get_move_vals(self, journal=None):

        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        return {
            'date': fields.Date.today(),
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'narration':self.reason,
            'prepared_by_id':self.user_id.id,
            'verified_by_id':self.env.uid,
            'journal_id': journal.id,
            'check_sign':True,
            'mode_type':self.mode_type,
            'acc_number_id':self.destination_journal_id.bank_account_id.id if self.destination_journal_id else self.acc_number_id.id,
            'bank_ifc':self.destination_journal_id.bank_id.bic if self.destination_journal_id else self.bank_ifc,
            'crossing':self.crossing if self.mode_type == 'CHEQUE' else False,
            'partner_name':self.partner_name,
        }



    def _create_transfer_entry(self, amount):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconcilable move line
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, dummy = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        amount_currency = self.destination_journal_id.currency_id and self.currency_id._convert(amount, self.destination_journal_id.currency_id, self.company_id, self.payment_date or fields.Date.today()) or 0

        dst_move = self.env['account.move'].create(self._get_move_transfer_vals(self.destination_journal_id))

        dst_liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, dst_move.id)
        dst_liquidity_aml_dict.update({
            'name': _('Transfer from %s') % self.journal_id.name,
            'account_id': self.destination_journal_id.default_credit_account_id.id,
            'currency_id': self.destination_journal_id.currency_id.id,
            'journal_id': self.destination_journal_id.id})
        aml_obj.create(dst_liquidity_aml_dict)

        transfer_debit_aml_dict = self._get_shared_move_line_vals(credit, debit, 0, dst_move.id)
        transfer_debit_aml_dict.update({
            'name': self.name,
            'account_id': self.company_id.transfer_account_id.id,
            'journal_id': self.destination_journal_id.id})
        if self.currency_id != self.company_id.currency_id:
            transfer_debit_aml_dict.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.amount,
            })
        transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        if not self.destination_journal_id.post_at_bank_rec:
            dst_move.post()
        return transfer_debit_aml



    def _get_move_transfer_vals(self, journal=None):

        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        return {
            'date': fields.Date.today(),
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'narration':self.reason,
            'prepared_by_id':self.user_id.id,
            'verified_by_id':self.env.uid,
            'journal_id': journal.id,
            'check_sign':True,
            'mode_type':self.mode_type,
            'acc_number_id':self.journal_id.bank_account_id.id,
            'bank_ifc':self.journal_id.bank_id.bic,
            'crossing':self.crossing if self.mode_type == 'CHEQUE' else False,
            'partner_name':self.partner_name,
        }


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue


            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'account_analytic_id': inv.account_analytic_id.id,
                        'analytic_tag_ids': [(6, 0, inv.analytic_tag_ids.ids)],
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'account_analytic_id': inv.account_analytic_id.id,
                    'analytic_tag_ids': [(6, 0, inv.analytic_tag_ids.ids)],
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            line = inv.finalize_invoice_move_lines(line)

            if inv.date:
                date = inv.date 
            else:
                date = fields.Date.context_today(self)
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'date_post_from_invoice':fields.Date.context_today(self),
                'narration': inv.comment,
                'verified_by_id':self.env.uid,
                'prepared_by_id':self.user_id.id
            }
            move = account_move.create(move_vals)
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post(invoice = inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True

# class AccountMoveLineInherit(models.Model):
#     _inherit = "account.move.line"
#
#     @api.one
#     def _prepare_analytic_line(self):
#         print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
#         """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
#             an analytic account. This method is intended to be extended in other modules.
#         """
#         amount = (self.credit or 0.0) - (self.debit or 0.0)
#         default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
#         return {
#             'name': default_name,
#             'date': self.date,
#             'account_id': self.analytic_account_id.id,
#             'tag_ids': [(6, 0, self._get_analytic_tag_ids())],
#             'unit_amount': self.quantity,
#             'product_id': self.product_id and self.product_id.id or False,
#             'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
#             'amount': amount,
#             'general_account_id': self.account_id.id,
#             'ref': self.ref,
#             'move_id': self.id,
#             'user_id': self.invoice_id.user_id.id or self._uid,
#             'partner_id': self.partner_id.id,
#             'company_id': self.analytic_account_id.company_id.id or self.env.user.company_id.id,
#         }



