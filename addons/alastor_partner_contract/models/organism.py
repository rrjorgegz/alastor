from odoo import fields, models


class Organism(models.Model):
    _name = "organism"
    _rec_name = "name"

    name = fields.Char("Nombre", required=True)

    _sql_constraints = [("name", "unique(name)", "Ya existe ese organismo")]
