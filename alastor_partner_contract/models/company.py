# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, _, api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    sale_days = fields.Integer("Días ventas")
    purchase_days = fields.Integer("Días compras")
    add_currency_id = fields.Many2one("res.currency", "Moneda adicional")
    partner_id = fields.Many2one("res.partner", "Entidad", required=False)

    @api.model
    def name_search(self, name="", args=[], operator="ilike", limit=100, context={}):
        context = dict(context or {})
        if context.pop("user_preference", None):
            user = self.env["res.users"].search(SUPERUSER_ID)
            cmp_ids = list(set([user.company_id.id] + [cmp.id for cmp in user.company_ids]))
            args = (args or []) + [("id", "in", cmp_ids)]

        ids = self.env["res.company"].search([("name", operator, name)] + args)
        return ids.name_get()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
