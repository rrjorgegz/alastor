# -*- coding: utf-8 -*-
from datetime import date, datetime, time, timedelta

from dateutil.relativedelta import relativedelta
from odoo import _, api, exceptions, fields, models


class MailAlert(models.Model):
    _name = "partner.contract.mail.alert"
    _description = "Contracts Mail Alert"
    _inherit = ["mail.thread"]

    @api.model
    def _reference_models(self):
        models = self.env["ir.model"].search([("state", "!=", "manual")])
        return [(model.model, model.name) for model in models if model.model.startswith("partner.")]

    name = fields.Char(string="Nombre", required=True)
    active = fields.Boolean("Activa", default=True)
    to = fields.Many2many("res.users", "res_user_mail_alert_rel", "user_id", "alert_id", "Para")
    to_other = fields.Char("Para (adicional)", help="Lista separada por comas de direcciones de email")
    subject = fields.Char(string="Asunto")
    body = fields.Html(string="Cuerpo", default="{{info}}")
    target_model = fields.Selection(string="Model", selection="_reference_models")
    target_filter = fields.Text(string="Filtro", default="[('state','=','active'),('expiration_date','<',today_plus_1m)]")
    always_send = fields.Boolean(string="Siempre Enviar", default=False)

    def get_docs(self):
        self.ensure_one()
        docs = []
        if self.target_model:
            today_date = datetime.today()
            today = datetime.today().strftime("%Y-%m-%d")
            today_plus_1d = (today_date + relativedelta(days=1)).strftime("%Y-%m-%d")
            today_plus_10d = (today_date + relativedelta(days=10)).strftime("%Y-%m-%d")
            today_plus_30d = (today_date + relativedelta(days=30)).strftime("%Y-%m-%d")
            today_plus_1w = (today_date + relativedelta(weeks=1)).strftime("%Y-%m-%d")
            today_plus_2w = (today_date + relativedelta(weeks=2)).strftime("%Y-%m-%d")
            today_plus_1m = (today_date + relativedelta(months=1)).strftime("%Y-%m-%d")
            today_plus_2m = (today_date + relativedelta(months=2)).strftime("%Y-%m-%d")
            today_plus_3m = (today_date + relativedelta(months=3)).strftime("%Y-%m-%d")

            today_minus_1d = (today_date - relativedelta(days=1)).strftime("%Y-%m-%d")
            today_minus_10d = (today_date - relativedelta(days=10)).strftime("%Y-%m-%d")
            today_minus_30d = (today_date - relativedelta(days=30)).strftime("%Y-%m-%d")
            today_minus_1w = (today_date - relativedelta(weeks=1)).strftime("%Y-%m-%d")
            today_minus_2w = (today_date - relativedelta(weeks=2)).strftime("%Y-%m-%d")
            today_minus_1m = (today_date - relativedelta(months=1)).strftime("%Y-%m-%d")
            today_minus_2m = (today_date - relativedelta(months=2)).strftime("%Y-%m-%d")
            today_minus_3m = (today_date - relativedelta(months=3)).strftime("%Y-%m-%d")

            if self.target_filter:
                try:
                    docs = self.env[self.target_model].search(eval(self.target_filter))
                except ValueError as e:
                    raise exceptions.Warning(_("Filter is invalid for this model"))
            else:
                docs = self.env[self.target_model].search([])

        return docs

    def parse_body(self, docs):
        self.ensure_one()
        info = "<ul>"
        for doc in docs:
            if hasattr(doc, "html_info"):
                info += "<li>" + doc.html_info + "</li>"
            else:
                info += "<li>" + doc.name + "</li>"
        info += "</ul>"

        body_html = self.body
        body_html = body_html.replace("{{info}}", info)
        return body_html

    def send(self):
        self.ensure_one()
        docs = self.get_docs()

        if not self.always_send and not len(docs):
            return

        email_array = self.to_other and self.to_other or ""
        for user in self.to:
            if user.email:
                email_array += user.email + ","

        company_id = self.env["res.company"]._company_default_get("partner.contract")
        company = self.env["res.company"].search([("id", "=", company_id.id)])
        email_from = company.email

        dicc = {}
        # dicc.update({'type': 'email'})
        dicc.update({"email_from": email_from})
        dicc.update({"reply_to": email_from})
        dicc.update({"email_to": email_array})
        dicc.update({"subject": self.subject})
        dicc.update({"body_html": self.parse_body(docs)})
        self.env["mail.mail"].create(dicc)


class MailAlerter(models.Model):
    _name = "partner.contract.mail.alerter"
    _description = "Contracts Mail Alerter"

    def send_alert_mails(self):
        alert_ids = self.env["partner.contract.mail.alert"].search([("active", "=", True)])
        alerts = self.env["partner.contract.mail.alert"].browse(alert_ids)
        for alert in alerts:
            alert.send()

        return True


class AutoCloser(models.Model):
    _name = "partner.contract.auto.closer"
    _description = "Contracts Auto Closer"
    _inherit = ["mail.thread"]

    def auto_close(self):
        classes = ["partner.purchase.frame.contract", "partner.purchase.contract", "partner.purchase.supplement", "partner.sale.frame.contract", "partner.sale.contract", "partner.sale.supplement"]
        for model in classes:
            today = datetime.today().strftime("%Y-%m-%d")
            model_ids = self.env[model].search([("state", "=", "active"), ("expiration_date", "<=", today), ("term_action", "=", "close")])
            self.env[model].write({"state": "done", "close_date": today})
            if model_ids:
                self.env[model].message_post(body=_("Closed by system"))

            model_ids2 = self.env[model].search([("state", "=", "active"), ("expiration_date", "<=", today), ("term_action", "=", "extend")])
            self.env[model].extend(model_ids2)

        return True
