# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SupplierType(models.Model):
    _name = "supplier.type"
    _description = "Tipo de Proveedor"

    name = fields.Char("Name", required=True)