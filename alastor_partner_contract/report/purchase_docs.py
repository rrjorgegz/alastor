# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
import time

from odoo import _, api, exceptions, fields, models


class PurchaseDocs(models.AbstractModel):
    _name = "report.purchase.docs"
    _description = "Documentos de compras"
    _template = "alastor_partner_contract.report_purchase_docs"

    def _get_frame_contracts(self, form):
        obj_list = self.env["partner.purchase.frame.contract"].search([])
        return obj_list

    def _get_contracts(self, ids):
        obj_list = self.env["partner.purchase.contract"].search([])
        return obj_list

    def _get_supplements(self, ids):
        obj_list = self.env["partner.purchase.supplement"].search([])
        return obj_list

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get("form") or not self.env.context.get("active_model"):
            raise exceptions.UserError(_("Form content is missing, this report cannot be printed."))
        self.model = self.env.context.get("active_model")

        docs = self.env[self.model].browse(self.env.context.get("active_id"))

        frame_contracts = self._get_frame_contracts(data.get("form"))

        return {"doc_ids": docids, "doc_model": self.model, "docs": docs, "data": data["form"], "get_frame_contracts": frame_contracts, "time": time}
