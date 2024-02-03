# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleDocs(models.TransientModel):
    _name = "sale.docs"
    _description = "Sale documents"

    company_ids = fields.Many2many("res.company", "sale_docs_res_company_rel", string="Entidades")
    state_draft = fields.Boolean("Borradores")
    state_proform = fields.Boolean("Proformas")
    state_approved = fields.Boolean("Aprobados")
    state_active = fields.Boolean("Activos", default=True)
    state_done = fields.Boolean("Cerrados")
    state_cancel = fields.Boolean("Cancelados")

    def print_report(self, context=None):
        wizard = self.browse(cr, uid, ids)
        companies = []
        for company in wizard.company_ids:
            companies.append(company.id)

        states = []
        if wizard.state_draft:
            states.append("draft")
        if wizard.state_proform:
            states.append("proform")
        if wizard.state_approved:
            states.append("approval")
        if wizard.state_active:
            states.append("active")
        if wizard.state_done:
            states.append("done")
        if wizard.state_cancel:
            states.append("cancel")

        if len(companies):
            frame_contract_ids = self.env["partner.sale.frame.contract"].search([("state", "in", states), ("company_id", "in", companies)], order="emission_date asc", context=context)
            contract_ids = self.env["partner.sale.contract"].search([("state", "in", states), ("company_id", "in", companies)], order="emission_date asc", context=context)
            supplement_ids = self.env["partner.sale.supplement"].search([("state", "in", states), ("company_id", "in", companies)], order="emission_date asc", context=context)
        else:
            frame_contract_ids = self.env["partner.sale.frame.contract"].search([("state", "in", states)], order="emission_date asc", context=context)
            contract_ids = self.env["partner.sale.contract"].search([("state", "in", states)], order="emission_date asc", context=context)
            supplement_ids = self.env["partner.sale.supplement"].search([("state", "in", states)], order="emission_date asc", context=context)

        form = {}
        form["frame_contract_ids"] = frame_contract_ids
        form["contract_ids"] = contract_ids
        form["supplement_ids"] = supplement_ids
        datas = {"ids": [], "model": "sale.docs", "form": form, "context": context}
        return {"report_name": "partner_contract.report_sale_docs", "type": "ir.actions.report.xml", "datas": datas, "context": context}


SaleDocs()
