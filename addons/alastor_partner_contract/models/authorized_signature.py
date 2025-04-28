from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AuthorizedSignature(models.Model):
    _name = "authorized.signature"
    _rec_name = "name"

    name = fields.Char("Nombre", required=True)
    dni = fields.Char("CI", required=True)
    partner_purchase_contract_id = fields.Many2one(
        "partner.purchase.contract", ondelete="cascade", string="Contrato de Compra"
    )
    partner_sale_contract_id = fields.Many2one(
        "partner.sale.contract", ondelete="cascade", string="Contrato de Venta"
    )

    @api.constrains("dni")
    def _check_ci(self):
        if self.dni.isdigit():
            if len(self.dni) != 11:
                raise ValidationError(
                    _("El carnet de identidad debe contener 11 dígitos")
                )
        else:
            raise ValidationError(
                _("El carnet de identidad solo debe contener dígitos")
            )

    _sql_constraints = [("dni", "unique(dni)", "Ya existe ese CI")]
