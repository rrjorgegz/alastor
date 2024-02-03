# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Municipality(models.Model):
    _description = "Municipality"
    _name = "res.country.municipality"

    state_id = fields.Many2one("res.country.state", "State", required=True)
    country_id = fields.Many2one("res.country", string="Country", related="state_id.country_id")
    name = fields.Char("Name", size=64, required=True)
    code = fields.Char("Code", size=3, help="The municipality code in three chars", required=True)

    _order = "code"

    @api.constrains("name")
    def _check_unique_name(self):
        for record in self:
            count = self.search_count([("name", "=", record.name), ("state_id", "=", record.state_id.id), ("id", "!=", record.id)])
            if count == 0:
                return True
            else:
                raise ValidationError("The name must be unique per state!")

    _sql_constraints = [("code", "unique (code)", "The code must be unique!.")]
