# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class Bank(models.Model):
    _inherit = "res.bank"
    bank_branch_ids = fields.One2many("res.bank.branch", "bank_id", "Sucursales bancarias")


class BankBranch(models.Model):
    _name = "res.bank.branch"
    _description = "Sucursal Bancaria"

    def name_get(self, cr, uid, ids, context=None):
        result = []
        for bank_branch in self.browse(cr, uid, ids, context):
            result.append((bank_branch.id, (bank_branch.bank_id.bic and (bank_branch.bank_id.bic + " - ") or "") + bank_branch.name))
        return result

    bank_id = fields.Many2one("res.bank", "Bank", required=True, ondelete="cascade")
    name = fields.Char("Name", required=True)
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    zip = fields.Char("Zip", change_default=True, size=24)
    city = fields.Many2one("res.country.municipality", "Municipality", domain="[('state_id', '=', state)]")
    state = fields.Many2one("res.country.state", "Fed. State", domain="[('country_id', '=', country)]")
    country = fields.Many2one("res.country", "Country")
    email = fields.Char("Email")
    phone = fields.Char("Phone")
    fax = fields.Char("Fax")
    _sql_constraints = [("name_unique", "unique(name, bank_id)", _("Names must be unique per bank!"))]


class PartnerBank(models.Model):
    _inherit = "res.partner.bank"

    account_currency_id = fields.Many2one("res.currency", "Moneda de la cuenta", required=True)
    bank_branch_id = fields.Many2one("res.bank.branch", "Sucursal Bancaria", required=True)

    @api.onchange("bank")
    def onchange_bank(self):
        result = {}
        if self.bank:
            self.bank_name = self.bank.name
            self.bank_bic = self.bank.bic
            self.bank_branch_id = False
        return {"value": result}

    @api.onchange("bank_branch_id")
    def onchange_bank_branch_id(self):
        if self.bank_branch_id:
            self.bank = self.bank_branch_id.bank_id

    _defaults = {"state": "bank"}


class SubordinationLevel(models.Model):
    _name = "partner.subordination.level"
    _description = "Nivel de subordinacion"

    name = fields.Char("Name")


class Partner(models.Model):
    _inherit = "res.partner"
    _rec_name = "display_name"

    ci = fields.Char("No. Identidad", size=11)
    subordination_level_id = fields.Many2one("partner.subordination.level", string="Subordination Level")
    is_supplier_logistics = fields.Boolean("Es Proveedor de Logistica")
    """
    frame_contract_sale_ids = fields.One2many('partner.sale.frame.contract', 'partner_id',
                                              'Sales Frame Contracts')
    contract_sale_ids = fields.One2many('partner.contract', 'partner_id', 'Sales Contracts',
                                        domain=[('sales', '=', True), ('type', '=', 'contract')])
    supplement_sale_ids = fields.One2many('partner.contract', 'partner_id', 'Sales Contracts',
                                          domain=[('sales', '=', True), ('type', '=', 'supplement')])
    frame_contract_purchase_ids = fields.One2many('partner.purchase.frame.contract', 'partner_id',
                                                  'Purchase Frame Contracts')
    contract_purchase_ids = fields.One2many('partner.contract', 'partner_id', 'Sales Contracts',
                                            domain=[('purchases', '=', True), ('type', '=', 'contract')])
    supplement_purchase_ids = fields.One2many('partner.contract', 'partner_id', 'Sales Contracts',
                                              domain=[('purchases', '=', True), ('type', '=', 'supplement')])
    """
