from odoo import api, fields, models, _

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def get_report_informations(self, options):
    	res = super(AccountReport, self).get_report_informations(options)
    	return res
