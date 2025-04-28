from odoo import fields, models


class ContractType(models.Model):
    """Types of Contracts"""

    _name = "partner.contract.type"
    _description = "Tipo de contrato"

    code = fields.Integer("Código", index=True)
    name = fields.Char("Denominación", size=64, required=True, index=True)
    description = fields.Text("Descripción", size=255, traslade=True, index=True)
    # number_days = fields.Integer('Number of days', help="Number of days of the contract.")
    purchases = fields.Boolean("Compras")
    sales = fields.Boolean("Ventas")
    active = fields.Boolean("Activo", default=True)

    _sql_constraints = [
        (
            "contract_code",
            "unique (code)",
            "El código del tipo de contrato debe ser único!",
        )
    ]
