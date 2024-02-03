# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner"]

    @api.onchange("city")
    def _onchange_municipality(self):
        self.state_id = self.city.state_id

    ministry = fields.Char("Ministry")
    reeup_code = fields.Char(string="REEUP code", index=True)
    nit_code = fields.Char(string="NIT code")
    nae_code = fields.Char("NAE code")
    city = fields.Many2one("res.country.municipality", string="Municipality")
    # Accreditation
    acc_res_no = fields.Char("Res No")
    acc_res_date = fields.Date("Res date")
    acc_res_emitted = fields.Char("Emitted by")
    # Contacts
    authorized = fields.Boolean("Authorized to firm contract")
    authorized_by = fields.Char("Authorized by")
    approve_charge = fields.Char("Approve charge")
    approve_res_no = fields.Char("Resolución que autoriza")
    approve_res_date = fields.Date("Fecha de resolución que autoriza")
    # villa clara
    code = fields.Char("Code", size=100)
    archive_nro = fields.Char("Archive", size=100)
    short_description = fields.Char("Short Description", size=100)
    is_company = fields.Boolean("Is a Company", help="Check if the contact is a company, otherwise it is a person", default=True)

    def _display_address(self, without_company=False):
        address_format = "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            "state_code": self.state_id.code or "",
            "state_name": self.state_id.name or "",
            "country_code": self.country_id.code or "",
            "country_name": self._get_country_name(),
            "company_name": self.commercial_company_name or "",
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ""
        args["city"] = self.city.name or ""
        if without_company:
            args["company_name"] = ""
        elif self.commercial_company_name:
            address_format = "%(company_name)s\n" + address_format
        return address_format % args


class ResCompany(models.Model):
    _inherit = "res.company"

    add_currency_id = fields.Many2one("res.currency", string="Add Currency")
