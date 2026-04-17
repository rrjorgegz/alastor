from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    _rec_name = "display_name"

    ci = fields.Char("No. Identidad", size=11)
    subordination_level_id = fields.Many2one(
        "partner.subordination.level", string="Subordination Level"
    )
    is_supplier_logistics = fields.Boolean(
        "Es Proveedor de Logistica", default=False, required=True
    )
    supplier_rank = fields.Integer(default=0, copy=False)
    customer_rank = fields.Integer(default=0, copy=False)
    partner_role = fields.Selection(
        [
            ("none", "Ninguno"),
            ("customer", "Cliente"),
            ("supplier", "Proveedor"),
            ("both", "Cliente y Proveedor"),
            ("logistics_supplier", "Proveedor de Logistica"),
        ],
        string="Tipo",
        # compute="_compute_partner_role",
        # store=True,
    )

    @api.depends("customer_rank", "supplier_rank")
    def _compute_partner_role(self):
        for partner in self:
            cust = bool(partner.customer_rank and partner.customer_rank > 0)
            supp = bool(partner.supplier_rank and partner.supplier_rank > 0)
            logic = bool(partner.is_supplier_logistics)
            if cust and supp:
                partner.partner_role = "both"
            elif cust:
                partner.partner_role = "customer"
            elif supp:
                partner.partner_role = "supplier"
            elif logic:
                partner.partner_role = "logistics_supplier"
            else:
                partner.partner_role = "none"

    @api.onchange("partner_role")
    def _onchange_partner_role(self):
        for partner in self:
            if partner.partner_role == "both":
                partner.customer_rank = 1
                partner.supplier_rank = 1
            elif partner.partner_role == "customer":
                partner.customer_rank = 1
            elif partner.partner_role == "supplier":
                partner.supplier_rank = 1
            elif partner.partner_role == "logistics_supplier":
                partner.is_supplier_logistics = True
            else:
                partner.partner_role = "none"
                partner.customer_rank = 0
                partner.supplier_rank = 0
                partner.is_supplier_logistics = False

    frame_contract_sale_ids = fields.One2many(
        "partner.sale.frame.contract", "partner_id", "Sales Frame Contracts"
    )
    contract_sale_ids = fields.One2many(
        "partner.sale.contract", "partner_id", "Sales Contracts"
    )
    # domain=[('sales', '=', True), ('type', '=', 'contract')])
    supplement_sale_ids = fields.One2many(
        "partner.sale.supplement", "partner_id", "Sales Contracts"
    )
    # ,domain=[('sales', '=', True), ('type', '=', 'supplement')])
    frame_contract_purchase_ids = fields.One2many(
        "partner.purchase.frame.contract", "partner_id", "Purchase Frame Contracts"
    )
    contract_purchase_ids = fields.One2many(
        "partner.purchase.contract", "partner_id", "Sales Contracts"
    )
    # ,domain=[('purchases', '=', True), ('type', '=', 'contract')])
    supplement_purchase_ids = fields.One2many(
        "partner.purchase.supplement", "partner_id", "Sales Contracts"
    )
    # ,domain=[('purchases', '=', True), ('type', '=', 'supplement')])
