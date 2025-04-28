from odoo import fields, models


class SupplierType(models.Model):
    _name = "supplier.type"
    _description = "Tipo de Proveedor"

    name = fields.Char("Name", required=True)
