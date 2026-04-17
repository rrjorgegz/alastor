from odoo import models


class PartnerContractMailAlerter(models.Model):
    _name = "partner.contract.mail.alerter"
    _description = "Contracts Mail Alerter"

    def send_alert_mails(self):
        alert_ids = self.env["partner.contract.mail.alert"].search(
            [("active", "=", True)]
        )
        alerts = self.env["partner.contract.mail.alert"].browse(alert_ids)
        for alert in alerts:
            alert.send()

        return True
