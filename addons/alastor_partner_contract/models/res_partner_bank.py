from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    account_currency_id = fields.Many2one(
        "res.currency", "Moneda de la cuenta", required=True
    )
    bank_branch_id = fields.Many2one(
        "res.bank.branch", "Sucursal Bancaria", required=True
    )

    @api.onchange("bank")
    def onchange_bank(self):
        result = {}
        if self.bank:
            self.bank_name = self.bank.name
            self.bank_bic = self.bank.bic
            self.bank_branch_id = False
        return {"value": result}

    @api.onchange("bank_branch_id")
    def onchange_bank_branch_id(self):
        if self.bank_branch_id:
            self.bank = self.bank_branch_id.bank_id
