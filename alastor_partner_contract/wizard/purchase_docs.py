# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseDocs(models.TransientModel):
    _name = "purchase.docs"
    _description = "Purchase documents wizard"

    company_ids = fields.Many2many("res.company", "purchase_docs_res_company_rel", string="Companies")
    state_received = fields.Boolean("Received")
    state_scheduled = fields.Boolean("Scheduled")
    state_approved = fields.Boolean("Approved")
    state_active = fields.Boolean("Active", default=True)
    state_done = fields.Boolean("Done")
    state_rejected = fields.Boolean("Rejected")

    def print_report(self):
        companies = []
        for company in self.company_ids:
            companies.append(company.id)

        states = []
        if self.state_received:
            states.append("received")
        if self.state_scheduled:
            states.append("scheduled")
        if self.state_approved:
            states.append("approved")
        if self.state_active:
            states.append("active")
        if self.state_done:
            states.append("done")
        if self.state_rejected:
            states.append("rejected")

        if len(companies):
            frame_contract_ids = self.env["partner.purchase.frame.contract"].search([("state", "in", states), ("company_id", "in", companies)], order="reception_date asc")
            contract_ids = self.env["partner.purchase.contract"].search([("state", "in", states), ("company_id", "in", companies)], order="reception_date asc")
            supplement_ids = self.env["partner.purchase.supplement"].search([("state", "in", states), ("company_id", "in", companies)], order="reception_date asc")
        else:
            frame_contract_ids = self.env["partner.purchase.frame.contract"].search([("state", "in", states)], order="reception_date asc")
            contract_ids = self.env["partner.purchase.contract"].search([("state", "in", states)], order="reception_date asc")
            supplement_ids = self.env["partner.purchase.supplement"].search([("state", "in", states)], order="reception_date asc")

        form = {}
        form["frame_contract_ids"] = frame_contract_ids
        form["contract_ids"] = contract_ids
        form["supplement_ids"] = supplement_ids
        data = {"ids": [], "model": "report.purchase.docs", "form": form}
        return self.env.ref("alastor_partner_contract.action_report_purchase_docs").with_context(landscape=False).report_action(self, data=data)
