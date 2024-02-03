# -*- coding: utf-8 -*-

from odoo import fields, models


class ConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]

    group_sales_frame_contracts = fields.Boolean(
        "Contratos Marco de Ventas",
        implied_group="alastor_partner_contract.group_sales_frame_contracts",
    )
    group_sales_contracts = fields.Boolean(
        "Contratos de Ventas",
        implied_group="alastor_partner_contract.group_sales_contracts",
    )
    group_sales_supplements = fields.Boolean(
        "Suplementos de Ventas",
        implied_group="alastor_partner_contract.group_sales_supplements",
    )
    group_purchases_frame_contracts = fields.Boolean(
        "Contratos Marco de Compras",
        implied_group="alastor_partner_contract.group_purchases_frame_contracts",
    )
    group_purchases_contracts = fields.Boolean(
        "Contratos de Compras",
        implied_group="alastor_partner_contract.group_purchases_contracts",
    )
    group_purchases_supplements = fields.Boolean(
        "Suplemntos de Compras",
        implied_group="alastor_partner_contract.group_purchases_supplements",
    )
