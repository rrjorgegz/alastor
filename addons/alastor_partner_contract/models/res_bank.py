from odoo import fields, models


class ResBank(models.Model):
    _inherit = "res.bank"
    bank_branch_ids = fields.One2many(
        "res.bank.branch", "bank_id", "Sucursales bancarias"
    )
