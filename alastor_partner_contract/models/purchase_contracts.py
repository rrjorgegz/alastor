# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo import _, api, exceptions, fields, models
from odoo.tools.misc import format_date, formatLang, get_lang

AVAILABLE_STATES = [
    ("received", "Recivido"),  # we receive a proforma (1 or 2 days)
    ("scheduled", "Planificado"),  # the contract is ready to be aproved or not
    ("approved", "Aprobado"),  # the contract is approved
    ("rejected", "Rechazado"),  # the contract is not approved
    ("resent", "Reenviado"),  # the contract is re sent to supplier to final signing
    ("active", "Activo"),  # the contract has came back and is active
    ("done", "Cerrado"),  # the contract is done
]

TERM_UOM = [
    ("year", "Año"),
    ("month", "Mes"),
    ("week", "Semana"),
    ("day", "Día"),
]

TERM_ACTION = [("close", "Cerrar"), ("extend", "Extender"), ("none", "Nada")]


TERM_TYPE = [
    ("fixed", "Fijo"),
    ("until", "Hasta"),
    ("none", "Nada"),
]


class PurchaseContract(models.Model):
    """Purchase Contract"""

    _name = "partner.purchase.contract"
    _description = "Contrato de compras"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "reception_date desc, number desc"

    def _expiration_date_progress(self):
        today = fields.Date.today()
        for i in self:
            if i.state == "active" and not i.expiration_date:
                i.validity_date_progress = 100
                return
            if not i.activation_date or not i.expiration_date:
                i.validity_date_progress = 0
                return

            total_days = i.expiration_date - i.activation_date
            init_date = today
            if today < i.activation_date:
                init_date = i.activation_date
            current_days = i.expiration_date - init_date
            current_days_number = current_days.days

            if current_days_number < 0:
                current_days_number = 0
            if total_days.days == 0:
                i.validity_date_progress = 0
            else:
                i.validity_date_progress = current_days_number * 100 / total_days.days

    def _get_supplement_count(self):
        self.supplement_count = len(self.supplement_ids)

    def get_warnings(self):
        for i in self:
            i.is_late = False
            i.warning_msg = ""
            if i.state == "received":
                delta = (i.reception_date - date.today()).days
                if delta < -7:
                    i.is_late = True
                    i.warning_msg = "Este documento fue recibido hace %s días y aun no se ha planificado su aprobación." % str(abs(delta))
            if i.state == "scheduled":
                delta = (i.scheduled_date - date.today()).days
                if delta < -2:
                    i.is_late = True
                    i.warning_msg = "Este documento estaba planificado para hace %s días y aun no se ha aprobado o rechazado." % str(abs(delta))
            if i.state == "approved" or i.state == "resent":
                delta = (i.approved_date - date.today()).days
                if delta < -7:
                    i.is_late = True
                    i.warning_msg = "Este documento fue aprobado hace %s días y aun no se ha activado." % str(abs(delta))
            if i.state == "active" and i.expiration_date:
                delta = (i.expiration_date - date.today()).days
                if delta < 30 and delta >= 0:
                    i.is_late = True
                    i.warning_msg = "Este documento expira en %s días." % str(abs(delta))
                elif delta < 0:
                    i.is_late = True
                    i.warning_msg = "Este documento expiró hace %s días." % str(abs(delta))

    is_late = fields.Boolean("Tarde", compute=get_warnings)
    warning_msg = fields.Text("Advertencias", compute=get_warnings)

    def _html_info(self):
        data = self.name + ", " + _("number: ") + self.number + " (Ref: " + self.supplier_ref + "), " + _("supplier: ") + self.partner_id.name
        if self.state == "active":
            if self.expiration_date:
                delta = (self.expiration_date - date.today()).days
                if delta.days >= 0:
                    data += ", " + _("expira en ") + str(delta) + _(" days")
                else:
                    data += ", " + _("ha expirado hace ") + str(abs(delta)) + _(" days")
            else:
                data += ", " + _("no expira")
        if self.state == "scheduled" or self.state == "received":
            delta = (date.today() - self.reception_date).days
            data += ", " + _("creado hace ") + str(delta) + _(" días")
        if self.state == "approved":
            delta = (date.today() - self.approved_date).days
            data += ", " + _("aprobado ") + str(delta) + _(" días")

        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        self.html_info = data + ' <a href="' + str(web_base_url) + "/web#id=" + str(self.id) + '&view_type=form&model=partner.purchase.contract">ver</a>'

    name = fields.Char("Nombre", required=True, index=True, readonly=True, states={"received": [("readonly", False)], "scheduled": [("readonly", False)]})
    user_id = fields.Many2one("res.users", "Usuario", index=True, help="User of the contract.", readonly=True, default=lambda s: s.env.user.id)
    message_ids = fields.One2many("mail.message", "res_id", "Mensajes", domain=[("model", "=", _name)])
    number = fields.Char(
        "Número",
        size=64,
        index=True,
        readonly=True,
        states={"received": [("readonly", False)], "scheduled": [("readonly", False)]},
        default="/",
        help="Número único del documento, " "calculado automáticamente cuando se aprueba.",
    )
    company_id = fields.Many2one(
        "res.company",
        "Compañía",
        required=True,
        default=lambda s: s.env.user.company_id.id,
        states={
            "received": [("readonly", False)],
            "scheduled": [("readonly", False)],
        },
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Proveedor",
        ondelete="restrict",
        track_visibility="onchange",
        index=True,
        required=True,
        readonly=True,
        states={"received": [("readonly", False)], "scheduled": [("readonly", False)]},
    )
    supplier_ref = fields.Char("Referencia proveedor", size=256, help="Referencia del proveedor", required=True)

    reception_date = fields.Date(
        "Fecha de recepción",
        readonly=True,
        default=lambda s: fields.Date.today(),
        states={"received": [("readonly", False), ("required", True)], "scheduled": [("readonly", False), ("required", True)]},
    )
    scheduled_date = fields.Date("Fecha planificada", readonly=True, states={"received": [("readonly", False), ("required", False)], "scheduled": [("readonly", False), ("required", True)]})

    currency_id = fields.Many2one("res.currency", "Moneda", related="company_id.currency_id")
    add_currency_id = fields.Many2one("res.currency", "Moneda Ad.", related="company_id.add_currency_id")
    html_info = fields.Text(compute=_html_info, string="HTML Representation")
    approved_date = fields.Date("Fecha de aprobación", readonly=True, states={"received": [("readonly", False)], "scheduled": [("readonly", False)]})
    activation_date = fields.Date(
        "Fecha de activación",
        invisible=True,
        readonly=True,
        states={
            "received": [("invisible", True), ("readonly", True)],
            "scheduled": [("invisible", True), ("readonly", True)],
            "approved": [("invisible", False), ("readonly", False)],
            "resent": [("invisible", False), ("readonly", False)],
            "active": [("invisible", False), ("readonly", True)],
            "rejected": [("invisible", False), ("readonly", True)],
            "done": [("invisible", False), ("readonly", True)],
        },
    )
    expiration_date = fields.Date(
        "Fecha de expiración",
        invisible=True,
        readonly=False,
        states={
            "received": [("invisible", True), ("readonly", True)],
            "scheduled": [("invisible", True), ("readonly", True)],
            "approved": [("invisible", False), ("readonly", True)],
            "resent": [("invisible", False), ("readonly", True)],
            "active": [("invisible", False), ("readonly", True)],
            "rejected": [("invisible", False), ("readonly", True)],
            "done": [("invisible", False), ("readonly", True)],
        },
    )
    close_date = fields.Date(
        "Fecha de cierre",
        invisible=True,
        readonly=True,
        states={
            "received": [("invisible", True), ("readonly", True)],
            "scheduled": [("invisible", True), ("readonly", True)],
            "approved": [("invisible", True), ("readonly", True)],
            "active": [("invisible", True), ("readonly", True)],
            "rejected": [("invisible", True), ("readonly", True)],
            "done": [("invisible", False), ("readonly", True)],
        },
    )
    state = fields.Selection(AVAILABLE_STATES, "Estado", size=16, readonly=True, default="received", track_visibility="onchange")
    amount = fields.Monetary(string="Importe", readonly=True, states={"received": [("readonly", False)], "scheduled": [("readonly", False)]})

    additional_amount = fields.Monetary(string="Importe Ad.", readonly=True, states={"received": [("readonly", False)], "scheduled": [("readonly", False)]})
    description = fields.Text("Notas")
    parent_id = fields.Many2one("partner.purchase.frame.contract", "Contrato padre", readonly=True, states={"received": [("readonly", False)], "scheduled": [("readonly", False)]})
    contract_type_id = fields.Many2one("partner.contract.type", "Tipo de contrato", readonly=True, states={"received": [("readonly", False)], "scheduled": [("readonly", False)]})
    supplement_ids = fields.One2many("partner.purchase.supplement", "parent_id", "Suplementos")
    supplement_count = fields.Integer(compute=_get_supplement_count, string="Número de suplementos")
    validity_date_progress = fields.Float(compute=_expiration_date_progress, string="Progreso")
    term = fields.Integer(
        "Plazo",
        required=False,
        readonly=False,
        default=1,
        states={
            "received": [("readonly", False)],
            "scheduled": [("readonly", False)],
            "approved": [("readonly", False)],
            "resent": [("readonly", False)],
            "active": [("readonly", True)],
            "rejected": [("readonly", True)],
            "done": [("readonly", True)],
        },
    )
    term_date = fields.Date("Fecha de término", required=False, readonly=False, states={"done": [("readonly", True)]})
    term_type = fields.Selection(
        TERM_TYPE, "Término", required=True, readonly=False, default="fixed", states={"active": [("readonly", True)], "rejected": [("readonly", True)], "done": [("readonly", True)]}
    )
    term_uom = fields.Selection(
        TERM_UOM,
        "Término (UdM)",
        required=False,
        readonly=False,
        default="year",
        states={
            "received": [("readonly", False)],
            "scheduled": [("readonly", False)],
            "approved": [("readonly", False)],
            "resent": [("readonly", False)],
            "active": [("readonly", True)],
            "rejected": [("readonly", True)],
            "done": [("readonly", True)],
        },
    )
    term_action = fields.Selection(
        TERM_ACTION,
        "Acción al terminar",
        required=True,
        readonly=False,
        default="close",
        states={
            "received": [("invisible", False)],
            "scheduled": [("readonly", False)],
            "approved": [("readonly", False)],
            "resent": [("readonly", False)],
            "active": [("readonly", False)],
            "rejected": [("readonly", True)],
            "done": [("readonly", True)],
        },
    )
    authorized_signature_ids = fields.One2many("authorized.signature", "partner_purchase_contract_id", store=True, string="Firmas autorizadas", required=True)
    organism_id = fields.Many2one("organism", "Organismo", required=True, store=True)

    @api.onchange("term_type", "term_date", "term", "term_uom", "activation_date")
    def onchange_term(self):
        self.expiration_date = False

        if self.term_type == "until":
            self.expiration_date = self.term_date
        if self.term_type == "fixed":
            if self.activation_date:
                activation_date = self.activation_date
                if self.term_uom == "year":
                    self.expiration_date = activation_date + relativedelta(years=int(self.term))
                if self.term_uom == "month":
                    self.expiration_date = activation_date + relativedelta(months=int(self.term))
                if self.term_uom == "week":
                    self.expiration_date = activation_date + relativedelta(weeks=int(self.term))
                if self.term_uom == "day":
                    self.expiration_date = activation_date + relativedelta(days=int(self.term))

    @api.onchange("parent_id")
    def onchange_parent_id(self):
        self.partner_id = False
        if self.parent_id:
            self.partner_id = self.parent_id.partner_id.id

    @api.model
    def create(self, vals):
        vals.update({"user_id": self._uid})
        parent_id = vals.get("parent_id", False)
        if parent_id:
            parent = self.env["partner.purchase.frame.contract"].search([("id", "=", parent_id)])
            if parent.state not in ("approved", "active"):
                raise exceptions.Warning(_("El contrato padre debe estar aprobado o activado"))
            if vals.get("reception_date") < parent.reception_date.strftime("%Y-%m-%d"):
                raise exceptions.Warning(_("La fecha de recepción no puede ser menor que la fecha de recepción del padre"))
        if vals.get("reception_date") > fields.Date.today().strftime("%Y-%m-%d"):
            raise exceptions.Warning(_("La fecha de recepción no puede ser mayor que hoy"))
        return super(PurchaseContract, self).create(vals)

    def unlink(self):
        if self.state != "received":
            raise exceptions.Warning(_("No puede eliminar un contrato sino está en estado Recibido."))

        return super(PurchaseContract, self).unlink()

    def extend(self):
        self.ensure_one()
        if self.state == "active" and self.term_action == "extend":
            if self.term_type == "fixed":
                if self.expiration_date and self.term and self.term_uom:
                    expiration_date = datetime.strptime(self.expiration_date, "%Y-%m-%d")
                    if self.term_uom == "year":
                        new_expiration_date = expiration_date + relativedelta(years=int(self.term))
                    if self.term_uom == "month":
                        new_expiration_date = expiration_date + relativedelta(months=int(self.term))
                    if self.term_uom == "week":
                        new_expiration_date = expiration_date + relativedelta(weeks=int(self.term))
                    if self.term_uom == "day":
                        new_expiration_date = expiration_date + relativedelta(days=int(self.term))

                    self.write({"expiration_date": new_expiration_date})
                    message = _("El contrato '%s' ha sido extendido hasta %s.") % (self.name, new_expiration_date.strftime("%Y-%m-%d"))
                    self.message_post(body=message)

    def write(self, vals):
        if self.state in ("active", "done", "rejected"):
            return super(PurchaseContract, self).write(vals)
        if vals.get("reception_date", self.reception_date.strftime("%Y-%m-%d")) > date.today().strftime("%Y-%m-%d"):
            raise exceptions.Warning(_("La fecha de recepción no puede ser mayor que hoy"))
        if vals.get("parent_id", False):
            parent = self.env["partner.purchase.frame.contract"].search([("id", "=", vals.get("parent_id", False))])
            if parent.state not in ("approved", "active"):
                raise exceptions.Warning(_("El contrato padre debe estar aprobado o activo"))
            if vals.get("reception_date", self.reception_date) < parent.reception_date:
                raise exceptions.Warning(_("La fecha de recepción no puede ser menor que la fecha de recepción del padre"))

        activation_date = vals.get("activation_date", False)
        if activation_date:
            activation_date = fields.Date.from_string(activation_date)
        else:
            activation_date = self.activation_date
        term_type = vals.get("term_type", self.term_type)
        term_date = vals.get("term_date", self.term_date)
        term = vals.get("term", self.term)
        term_uom = vals.get("term_uom", self.term_uom)

        if term_type == "until":
            vals.update({"expiration_date": term_date})
        if term_type == "none":
            vals.update({"expiration_date": False})
        if term_type == "fixed":
            if activation_date and term and term_uom:
                if term_uom == "year":
                    expiration_date = activation_date + relativedelta(years=int(term))
                if term_uom == "month":
                    expiration_date = activation_date + relativedelta(months=int(term))
                if term_uom == "week":
                    expiration_date = activation_date + relativedelta(weeks=int(term))
                if term_uom == "day":
                    expiration_date = activation_date + relativedelta(days=int(term))
                vals.update({"expiration_date": expiration_date})

        return super(PurchaseContract, self).write(vals)

    def case_reset(self):
        self.ensure_one()
        self.write({"state": "received"})

    def case_resent(self):
        self.ensure_one()
        self.write({"state": "resent"})

    def case_scheduled(self):
        self.ensure_one()
        template = self.env.ref("alastor_partner_contract.email_template_purchase_contract_scheduled", raise_if_not_found=False)

        if self.state == "received":
            if not self.scheduled_date:
                raise exceptions.Warning(_("Debe establecer la fecha planificada para planificar el documento"))

            if self.scheduled_date < self.reception_date:
                raise exceptions.ValidationError(_("La fecha planificada no puede ser anterior a la fecha de recepción"))

            self.write({"state": "scheduled"})
            if template:
                self.with_context(force_send=True).message_post_with_template(template.id)

    def case_rejected(self):
        template = self.env.ref("alastor_partner_contract.email_template_purchase_contract_rejected", raise_if_not_found=False)

        for it in self:
            if it.state in ("received", "scheduled"):
                it.write({"state": "rejected"})
                if template:
                    it.with_context(force_send=True).message_post_with_template(template.id)

    def case_approved(self):
        template = self.env.ref("alastor_partner_contract.email_template_purchase_contract_approved", raise_if_not_found=False)

        for it in self:
            if it.state in ("received", "scheduled"):
                if not it.approved_date:
                    raise exceptions.Warning(_("Debe establecer la fecha de aprobación para aprobar el documento"))
                if it.approved_date < it.reception_date:
                    raise exceptions.Warning(_("La fecha de aprobación no puede ser anterior a la fecha de recepción"))
                if it.approved_date > fields.Date.today():
                    raise exceptions.Warning(_("La fecha de aprobación no puede ser mayor que hoy"))
                if it.parent_id and it.parent_id.approved_date > it.approved_date:
                    raise exceptions.Warning(_("La fecha de aprobación no puede ser menor que la fecha de aprobación del padre"))

                # set the number by the sequence
                if it.number == "" or it.number == "/":
                    seq = self.env["ir.sequence"].next_by_code("partner.contract.purchases")
                    it.write({"number": seq})

                it.write({"state": "approved"})
                if template:
                    it.with_context(force_send=True).message_post_with_template(template.id)

    def case_active(self):
        template = self.env.ref("alastor_partner_contract.email_template_purchase_contract_actived", raise_if_not_found=False)

        for it in self:
            if it.state in ("approved", "resent"):
                if not it.activation_date:
                    raise exceptions.Warning(_("Debe establecer la fecha de activación para activar el documento"))
                if it.term_type == "until":
                    if not it.term_date:
                        raise exceptions.Warning(_("Debe establecer la fecha de término para activar el documento"))
                if it.term_type == "fixed":
                    if not it.term:
                        raise exceptions.Warning(_("Debe establecer un término para activar el documento"))
                    if not it.term_uom:
                        raise exceptions.Warning(_("Debe establecer la unidad de medida del término para activar el documento"))
                if it.activation_date < it.approved_date:
                    raise exceptions.Warning(_("La fecha de activación no puede ser menor que la fecha de aprobación"))
                if it.activation_date > fields.Date.today():
                    raise exceptions.Warning(_("La fecha de activación no puede ser mayor que hoy"))
                if it.expiration_date:
                    if self.activation_date > self.expiration_date:
                        raise exceptions.Warning(_("La fecha de expiración no puede ser menor que la fecha de activación"))

                message = _("El contrato '%s' ha sido activado.") % it.name
                it.message_post(body=message)
                it.write({"state": "active"})

                if template:
                    it.with_context(force_send=True).message_post_with_template(template.id)

    def case_close(self):
        template = self.env.ref("alastor_partner_contract.email_template_purchase_contract_closed", raise_if_not_found=False)

        for it in self:
            if it.state == "active":
                list_supplements = self.env["partner.purchase.supplement"].search([("parent_id", "=", it.id), ("state", "not in", ["rejected", "done"])])
                if len(list_supplements) > 0:
                    raise exceptions.Warning(_("No puede cerrar este contrato porque tiene suplementos"))

                message = _("El contrato '%s' ha sido cerrado.") % it.name
                it.message_post(body=message)
                it.write({"close_date": date.today().strftime("%Y-%m-%d"), "state": "done"})

                if template:
                    it.with_context(force_send=True).message_post_with_template(template.id)

    def name_get(self):
        if self._context.get("full_name", False):
            result = []
            for record in self:
                result.append((record.id, record.number + " - " + record.name + " (" + record.partner_id.name + ")"))
            return result

        return super(PurchaseContract, self).name_get()

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100, context={}):
        ids = self.env["partner.purchase.contract"].search(["|", ("number", operator, name), ("name", operator, name)] + args)
        return ids.name_get()
