from odoo import fields, models


class PartnerSubordinationLevel(models.Model):
    _name = "partner.subordination.level"
    _description = "Nivel de subordinacion"

    name = fields.Char("Name")
