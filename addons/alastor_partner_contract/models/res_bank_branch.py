from odoo import _, fields, models


class ResBankBranch(models.Model):
    _name = "res.bank.branch"
    _description = "Sucursal Bancaria"

    def name_get(self):
        result = []
        for bank_branch in self:
            result.append(
                (
                    bank_branch.id,
                    (
                        bank_branch.bank_id.bic
                        and (bank_branch.bank_id.bic + " - ")
                        or ""
                    )
                    + bank_branch.name,
                )
            )
        return result

    bank_id = fields.Many2one("res.bank", "Bank", required=True, ondelete="cascade")
    name = fields.Char("Name", required=True)
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    zip = fields.Char("Zip", change_default=True, size=24)
    city = fields.Many2one(
        "res.country.municipality", "Municipality", domain="[('state_id', '=', state)]"
    )
    state = fields.Many2one(
        "res.country.state",
        "Fed. State",
        domain="[('country_id', '=', country)]",
        default="bank",
    )
    country = fields.Many2one("res.country", "Country")
    email = fields.Char("Email")
    phone = fields.Char("Phone")
    fax = fields.Char("Fax")
    _sql_constraints = [
        ("name_unique", "unique(name, bank_id)", _("Names must be unique per bank!"))
    ]
