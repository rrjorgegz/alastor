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

from openerp.osv import osv
from openerp.report import report_sxw


class SaleDocsPrint(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(SaleDocsPrint, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({"time": time, "get_frame_contracts": self._get_frame_contracts, "get_contracts": self._get_contracts, "get_supplements": self._get_supplements})

    def _get_frame_contracts(self, ids):
        obj_list = self.env["partner.sale.frame.contract"].browse(ids)
        return obj_list

    def _get_contracts(self, ids):
        obj_list = self.env["partner.sale.contract"].browse(ids)
        return obj_list

    def _get_supplements(self, ids):
        obj_list = self.env["partner.sale.supplement"].browse(ids)
        return obj_list


class SaleDocs(osv.AbstractModel):
    _name = "report.partner_contract.report_sale_docs"
    _inherit = "report.abstract_report"
    _template = "partner_contract.report_sale_docs"
    _wrapped_report_class = SaleDocsPrint


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
