from odoo import _, api, exceptions, fields, models


class PartnerContractMailAlert(models.Model):
    _name = "partner.contract.mail.alert"
    _description = "Contracts Mail Alert"
    _inherit = ["mail.thread"]

    @api.model
    def _reference_models(self):
        models = self.env["ir.model"].search([("state", "!=", "manual")])
        return [
            (model.model, model.name)
            for model in models
            if model.model.startswith("partner.")
        ]

    name = fields.Char(string="Nombre", required=True)
    active = fields.Boolean("Activa", default=True)
    to = fields.Many2many(
        "res.users", "res_user_mail_alert_rel", "user_id", "alert_id", "Para"
    )
    to_other = fields.Char(
        "Para (adicional)", help="Lista separada por comas de direcciones de email"
    )
    subject = fields.Char(string="Asunto")
    body = fields.Html(string="Cuerpo", default="{{info}}")
    target_model = fields.Selection(string="Model", selection="_reference_models")
    target_filter = fields.Text(
        string="Filtro",
        default="[('state','=','active'),('expiration_date','<',today_plus_1m)]",
    )
    always_send = fields.Boolean(string="Siempre Enviar", default=False)

    def get_docs(self):
        self.ensure_one()
        docs = []
        if self.target_model:
            if self.target_filter:
                try:
                    docs = self.env[self.target_model].search(self.target_filter)
                except ValueError:
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
