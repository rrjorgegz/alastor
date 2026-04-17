from datetime import datetime

from odoo import _, models


class PartnerContractAutoCloser(models.Model):
    _name = "partner.contract.auto.closer"
    _description = "Contracts Auto Closer"
    _inherit = ["mail.thread"]

    def auto_close(self):
        classes = [
            "partner.purchase.frame.contract",
            "partner.purchase.contract",
            "partner.purchase.supplement",
            "partner.sale.frame.contract",
            "partner.sale.contract",
            "partner.sale.supplement",
        ]
        for model in classes:
            today = datetime.today().strftime("%Y-%m-%d")
            model_ids = self.env[model].search(
                [
                    ("state", "=", "active"),
                    ("expiration_date", "<=", today),
                    ("term_action", "=", "close"),
                ]
            )
            self.env[model].write({"state": "done", "close_date": today})
            if model_ids:
                self.env[model].message_post(body=_("Closed by system"))

            model_ids2 = self.env[model].search(
                [
                    ("state", "=", "active"),
                    ("expiration_date", "<=", today),
                    ("term_action", "=", "extend"),
                ]
            )
            self.env[model].extend(model_ids2)

        return True
