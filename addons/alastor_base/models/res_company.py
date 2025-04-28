from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    add_currency_id = fields.Many2one("res.currency", string="Add Currency")
