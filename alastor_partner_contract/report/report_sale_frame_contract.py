from odoo import api, fields, models


class ReportSaleFrameContract(models.AbstractModel):
    _name = "report.alastor.partner.contract.report_sale_frame_contracts"
    _description = "Sales Frame Contracts"

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            "doc_ids": docids,
            "doc_model": "partner.sale.frame.contract",
            "docs": self.env["partner.sale.frame.contract"].browse(docids),
            "report_type": data.get("report_type") if data else "",
        }
