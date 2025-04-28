from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models

AVAILABLE_STATES = [
    ("draft", "Borrador"),
    ("proform", "Proforma"),
    ("approved", "Aprobado"),
    ("rejected", "Rechazado"),
    ("active", "Activo"),
    ("done", "Cerrado"),
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


class SaleSupplement(models.Model):
    """Sale Supplement"""

    _name = "partner.sale.supplement"
    _description = "Sale Supplement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "emission_date desc, number desc"

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

    def get_warnings(self):
        for i in self:
            i.is_late = False
            i.warning_msg = ""
            if i.state == "proform":
                delta = (i.emission_date - date.today()).days
                if delta < -14:
                    i.is_late = True
                    i.warning_msg = """Este documento fue enviado
hace %s días y aun no se ha obtenido respuesta.""" % str(
                        abs(delta)
                    )
            if i.state == "approved":
                delta = (i.approved_date - date.today()).days
                if delta < -7:
                    i.is_late = True
                    i.warning_msg = (
                        "Este documento fue aprobado hace %s días y aun no se ha activado."
                        % str(abs(delta))
                    )
            if i.state == "active" and i.expiration_date:
                delta = (i.expiration_date - date.today()).days
                if delta < 30 and delta >= 0:
                    i.is_late = True
                    i.warning_msg = "Este documento expira en %s días." % str(
                        abs(delta)
                    )
                elif delta < 0:
                    i.is_late = True
                    i.warning_msg = "Este documento expiró hace %s días." % str(
                        abs(delta)
                    )

    is_late = fields.Boolean("Tarde", compute=get_warnings)
    warning_msg = fields.Text("Advertencias", compute=get_warnings)

    def _html_info(self):
        data = (
            self.name
            + ", "
            + _("número: ")
            + self.number
            + ", "
            + _("cliente: ")
            + self.partner_id.name
        )
        if self.state == "active":
            if self.expiration_date:
                delta = relativedelta(
                    datetime.strptime(self.expiration_date, "%Y-%m-%d"),
                    datetime.today(),
                )
                if delta.days >= 0:
                    data += (
                        ", "
                        + _("expira en ")
                        + str(delta.days + (delta.months * 31) + (delta.years * 365))
                        + _(" días")
                    )
                else:
                    data += (
                        ", "
                        + _("ha expirado hace ")
                        + str(
                            (delta.days + (delta.months * 31) + (delta.years * 365))
                            * -1
                        )
                        + _(" días")
                    )
            else:
                data += ", " + _("no expira")
        if self.state == "proform":
            delta = relativedelta(
                datetime.today(), datetime.strptime(self.emission_date, "%Y-%m-%d")
            )
            data += (
                ", "
                + _("creado hace")
                + str(delta.days + (delta.months * 31) + (delta.years * 365))
                + _(" días")
            )
        if self.state == "approved":
            delta = relativedelta(
                datetime.today(), datetime.strptime(self.approved_date, "%Y-%m-%d")
            )
            data += (
                ", "
                + _("aprobado hace ")
                + str(delta.days + (delta.months * 31) + (delta.years * 365))
                + _(" días")
            )

        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        self.html_info = (
            data
            + ' <a href="'
            + str(web_base_url)
            + "/web#id="
            + str(self.id)
            + '&view_type=form&model=partner.sale.supplement">ver</a>'
        )

    name = fields.Char(
        "Nombre",
        required=True,
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)], "proform": [("readonly", False)]},
    )
    user_id = fields.Many2one("res.users", "Usuario", index=True, readonly=True)
    message_ids = fields.One2many(
        "mail.message", "res_id", "Mensajes", domain=[("model", "=", _name)]
    )
    number = fields.Char(
        "Número",
        size=64,
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)], "proform": [("readonly", False)]},
        default="/",
        help="Número único del documento, "
        "calculado automáticamente cuando se aprueba el documento.",
    )
    currency_id = fields.Many2one(
        "res.currency", "Moneda", related="company_id.currency_id"
    )
    add_currency_id = fields.Many2one(
        "res.currency", "Moneda Ad.", related="company_id.add_currency_id"
    )
    html_info = fields.Text(compute=_html_info, string="HTML Representation")
    company_id = fields.Many2one(
        "res.company",
        "Compañía",
        required=True,
        default=lambda s: s.env.user.company_id.id,
        states={
            "draft": [("readonly", False)],
            "proform": [("readonly", False)],
            "approved": [("readonly", True)],
            "active": [("readonly", True)],
            "rejected": [("readonly", True)],
            "done": [("readonly", True)],
        },
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Cliente",
        ondelete="restrict",
        track_visibility="onchange",
        index=True,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    client_ref = fields.Char("Referencia cliente", size=256, help="Customer Reference")
    emission_date = fields.Date(
        "Fecha de emisión",
        readonly=True,
        default=lambda s: fields.Date.today(),
        states={"draft": [("readonly", False), ("required", True)]},
    )
    approved_date = fields.Date(
        "Fecha de aprobación",
        help="Fecha de aprobación",
        readonly=True,
        states={"proform": [("readonly", False)]},
    )
    activation_date = fields.Date(
        "Fecha de activación", readonly=True, states={"approved": [("readonly", False)]}
    )
    expiration_date = fields.Date("Fecha de expiración", readonly=True)
    rejected_date = fields.Date(
        "Fecha de rechazo",
        readonly=True,
        invisible=True,
        states={
            "proform": [("invisible", False), ("readonly", False)],
            "rejected": [("invisible", False), ("readonly", True)],
        },
    )
    close_date = fields.Date(
        "Fecha de cierre",
        invisible=True,
        readonly=True,
        states={
            "draft": [("invisible", True), ("readonly", True)],
            "proform": [("invisible", True), ("readonly", True)],
            "approved": [("invisible", True), ("readonly", True)],
            "active": [("invisible", True), ("readonly", True)],
            "rejected": [("invisible", True), ("readonly", True)],
            "done": [("invisible", False), ("readonly", True)],
        },
    )

    state = fields.Selection(
        AVAILABLE_STATES,
        "Estado",
        size=16,
        readonly=True,
        default="draft",
        track_visibility="onchange",
    )
    description = fields.Text("Notas")
    amount = fields.Float(
        string="Importe",
        readonly=True,
        states={"draft": [("readonly", False)], "proform": [("readonly", False)]},
    )
    additional_amount = fields.Float(
        string="Importe Ad.",
        readonly=True,
        states={"draft": [("readonly", False)], "proform": [("readonly", False)]},
    )
    frame_parent_id = fields.Many2one(
        "partner.sale.frame.contract",
        "Contrato marco padre",
        default=lambda self: self.env.context["frame_parent_id"]
        if "frame_parent_id" in self.env.context
        else False,
        readonly=True,
        states={"draft": [("readonly", False)], "proform": [("readonly", False)]},
    )
    parent_id = fields.Many2one(
        "partner.sale.contract",
        "Contrato padre",
        default=lambda self: self.env.context["parent_id"]
        if "parent_id" in self.env.context
        else False,
        readonly=True,
        states={"draft": [("readonly", False)], "proform": [("readonly", False)]},
    )
    contract_type_id = fields.Many2one(
        "partner.contract.type",
        "Tipo de contrato",
        readonly=True,
        states={"draft": [("readonly", False)], "proform": [("readonly", False)]},
    )
    validity_date_progress = fields.Float(
        compute=_expiration_date_progress, string="Progreso"
    )
    term = fields.Integer(
        "Plazo",
        required=False,
        readonly=True,
        default=1,
        states={"draft": [("readonly", False)]},
    )
    term_date = fields.Date(
        "Fecha de término",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    term_type = fields.Selection(
        TERM_TYPE,
        "Término",
        required=True,
        readonly=True,
        default="fixed",
        states={"draft": [("readonly", False)]},
    )
    term_uom = fields.Selection(
        TERM_UOM,
        "Término (UdM)",
        required=False,
        readonly=True,
        default="year",
        states={"draft": [("readonly", False)]},
    )
    term_action = fields.Selection(
        TERM_ACTION,
        "Acción al terminar",
        required=True,
        readonly=False,
        default="close",
        states={"rejected": [("readonly", True)], "done": [("readonly", True)]},
    )
    supplement_cause = fields.Selection(
        [
            ("execution", "Ejecución"),
            ("extension", "Extensión"),
            ("reduction", "Reducción"),
        ],
        "Causa del suplemento",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "proform": [("readonly", False)]},
    )
    update_parent_validity = fields.Boolean(
        "Actualizar validez del padre",
        help="Actualizar validez del padre",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "proform": [("readonly", False)],
            "approved": [("readonly", False)],
        },
    )

    @api.onchange("term_type", "term_date", "term", "term_uom", "activation_date")
    def onchange_term(self):
        self.expiration_date = False

        if self.term_type == "until":
            self.expiration_date = self.term_date
        if self.term_type == "fixed":
            if self.activation_date:
                activation_date = self.activation_date
                if self.term_uom == "year":
                    self.expiration_date = activation_date + relativedelta(
                        years=int(self.term)
                    )
                if self.term_uom == "month":
                    self.expiration_date = activation_date + relativedelta(
                        months=int(self.term)
                    )
                if self.term_uom == "week":
                    self.expiration_date = activation_date + relativedelta(
                        weeks=int(self.term)
                    )
                if self.term_uom == "day":
                    self.expiration_date = activation_date + relativedelta(
                        days=int(self.term)
                    )

    @api.onchange("parent_id")
    def onchange_parent_id(self):
        if not self.parent_id and not self.frame_parent_id:
            self.partner_id = False
            self.contract_type_id = False
        if self.parent_id:
            self.frame_parent_id = False
            self.partner_id = self.parent_id.partner_id.id
            self.contract_type_id = self.parent_id.contract_type_id.id

    @api.onchange("frame_parent_id")
    def onchange_frame_parent_id(self):
        if not self.parent_id and not self.frame_parent_id:
            self.partner_id = False
            self.contract_type_id = False
        if self.frame_parent_id:
            self.parent_id = False
            self.partner_id = self.frame_parent_id.partner_id.id
            self.contract_type_id = False

    @api.model
    def create(self, vals):
        vals.update({"user_id": self._uid})
        frame_parent_id = vals.get("frame_parent_id", False)
        if frame_parent_id:
            frame_parent = self.env["partner.sale.frame.contract"].search(
                [("id", "=", frame_parent_id)]
            )
            if frame_parent.state not in ("approved", "active"):
                raise exceptions.Warning(
                    _("El contrato padre debe estar aprobado o activado")
                )
            if vals.get("emission_date") < frame_parent.emission_date.strftime(
                "%Y-%m-%d"
            ):
                raise exceptions.Warning(
                    _(
                        """La fecha de emisión no
puede ser menor que la fecha de emisión del padre"""
                    )
                )

        parent_id = vals.get("parent_id", False)
        if parent_id:
            parent = self.env["partner.sale.contract"].search([("id", "=", parent_id)])
            if parent.state not in ("approved", "active"):
                raise exceptions.Warning(
                    _("El contrato padre debe estar aprobado o activado")
                )
            if vals.get("emission_date") < parent.emission_date.strftime("%Y-%m-%d"):
                raise exceptions.Warning(
                    _(
                        """La fecha de emisión no
puede ser menor que la fecha de emisión del padre"""
                    )
                )
        if vals.get("emission_date") > date.today().strftime("%Y-%m-%d"):
            raise exceptions.Warning(
                _("La fecha de emisión no puede ser mayor que hoy")
            )
        if parent_id and frame_parent_id:
            raise exceptions.Warning(
                _(
                    """Los suplementos no pueden
ser hijos de un Contrato Marco y de un Contrato a la vez"""
                )
            )
        if not parent_id and not frame_parent_id:
            raise exceptions.Warning(_("Los suplementos deben tener un padre"))
        return super(SaleSupplement, self).create(vals)

    def unlink(self):
        if self.state != "draft":
            raise exceptions.Warning(
                _("No puede eliminar un suplemento sino está en estado Borrador.")
            )

        return super(SaleSupplement, self).unlink()

    def extend(self):
        if self.state == "active" and self.term_action == "extend":
            if self.term_type == "fixed":
                if self.expiration_date and self.term and self.term_uom:
                    expiration_date = datetime.strptime(
                        self.expiration_date, "%Y-%m-%d"
                    )
                    if self.term_uom == "year":
                        new_expiration_date = expiration_date + relativedelta(
                            years=int(self.term)
                        )
                    if self.term_uom == "month":
                        new_expiration_date = expiration_date + relativedelta(
                            months=int(self.term)
                        )
                    if self.term_uom == "week":
                        new_expiration_date = expiration_date + relativedelta(
                            weeks=int(self.term)
                        )
                    if self.term_uom == "day":
                        new_expiration_date = expiration_date + relativedelta(
                            days=int(self.term)
                        )

                    self.write({"expiration_date": new_expiration_date})
                    message = _("El suplemento '%s' ha sido extendido hasta %s.") % (
                        self.name,
                        new_expiration_date.strftime("%Y-%m-%d"),
                    )
                    self.message_post(body=message)
        return True

    def write(self, vals):
        if self.state in ("active", "done", "cancel"):
            return super(SaleSupplement, self).write(vals)

        emission_date = vals.get(
            "emission_date", self.emission_date.strftime("%Y-%m-%d")
        )
        self._validate_emission_date(emission_date)

        frame_parent = self.env["partner.sale.frame.contract"].search(
            [("id", "=", vals.get("frame_parent_id", self.frame_parent_id.id))]
        )
        parent = self.env["partner.sale.contract"].search(
            [("id", "=", vals.get("parent_id", self.parent_id.id))]
        )

        self._validate_contract(frame_parent, emission_date, _("contrato marco"))
        self._validate_contract(parent, emission_date, _("contrato padre"))

        self._check_parent_and_frame_parent(frame_parent, parent)
        self._check_at_least_one_parent(frame_parent, parent)

        activation_date = self._get_activation_date(vals)
        term_type = vals.get("term_type", self.term_type)
        term_date = vals.get("term_date", self.term_date)
        term = vals.get("term", self.term)
        term_uom = vals.get("term_uom", self.term_uom)

        expiration_date = self._compute_expiration_date(
            term_type, term_date, activation_date, term, term_uom
        )
        if expiration_date is not None:
            vals["expiration_date"] = expiration_date

        return super(SaleSupplement, self).write(vals)

    def _validate_emission_date(self, emission_date):
        if emission_date > date.today().strftime("%Y-%m-%d"):
            raise exceptions.Warning(
                _("La fecha de emisión no puede ser mayor que hoy")
            )

    def _validate_contract(self, contract, emission_date, contract_type_label):
        if not contract:
            return

        if contract.state not in ("approval", "active"):
            raise exceptions.Warning(
                _("El %s debe estar aprobado o activo") % contract_type_label
            )

        contract_emission_date = contract.emission_date.strftime("%Y-%m-%d")
        if emission_date < contract_emission_date:
            raise exceptions.Warning(
                _("La fecha de emisión no puede ser menor que la del %s")
                % contract_type_label
            )

    def _check_parent_and_frame_parent(self, frame_parent, parent):
        if frame_parent and parent:
            raise exceptions.Warning(
                _(
                    """Los suplementos no pueden ser hijos
                    de un Contrato Marco y de un Contrato a la vez"""
                )
            )

    def _check_at_least_one_parent(self, frame_parent, parent):
        if not frame_parent and not parent:
            raise exceptions.Warning(_("Los suplementos deben tener un padre"))

    def _get_activation_date(self, vals):
        activation_date = vals.get("activation_date")
        return (
            fields.Date.from_string(activation_date)
            if activation_date
            else self.activation_date
        )

    def _compute_expiration_date(
        self, term_type, term_date, activation_date, term, term_uom
    ):
        if term_type == "until":
            return term_date
        if term_type == "none":
            return False
        if term_type == "fixed" and activation_date and term and term_uom:
            return self._calculate_fixed_term_expiration(
                activation_date, term, term_uom
            )
        return None

    def _calculate_fixed_term_expiration(self, activation_date, term, term_uom):
        deltas = {
            "year": relativedelta(years=int(term)),
            "month": relativedelta(months=int(term)),
            "week": relativedelta(weeks=int(term)),
            "day": relativedelta(days=int(term)),
        }
        return activation_date + deltas.get(term_uom, relativedelta())

    def case_reset(self):
        self.ensure_one()
        self.write(
            {
                "activation_date": False,
                "approved_date": False,
                "rejected_date": False,
                "state": "draft",
            }
        )

    def case_proform(self):
        template = self.env.ref(
            "alastor_partner_contract.email_template_sale_supplement_proform",
            raise_if_not_found=False,
        )
        for it in self:
            if it.state == "draft":
                it.write({"state": "proform"})
                if template:
                    it.with_context(force_send=True).message_post_with_template(
                        template.id
                    )

    def case_approved(self):
        template = self.env.ref(
            "alastor_partner_contract.email_template_sale_supplement_approved",
            raise_if_not_found=False,
        )

        for it in self:
            if it.state in ("proform"):
                if not it.approved_date:
                    raise exceptions.Warning(
                        _(
                            "Debe establecer la fecha de aprobación para aprobar el documento"
                        )
                    )
                if it.approved_date < it.emission_date:
                    raise exceptions.Warning(
                        _(
                            "La fecha de aprobación no puede ser menor que la fecha de emisión"
                        )
                    )
                if it.approved_date > fields.Date.today():
                    raise exceptions.Warning(
                        _("La fecha de aprobación no puede ser mayor que hoy")
                    )
                if it.parent_id and it.parent_id.approved_date > it.approved_date:
                    raise exceptions.Warning(
                        _(
                            """La fecha de aprobación no
puede ser menor que la fecha de aprobación del padre"""
                        )
                    )
                if (
                    it.frame_parent_id
                    and it.frame_parent_id.approved_date > it.approved_date
                ):
                    raise exceptions.Warning(
                        _(
                            """La fecha de aprobación no
puede ser menor que la fecha de aprobación del padre"""
                        )
                    )

                # set the number by the sequence
                if it.number == "" or it.number == "/":
                    seq = self.env["ir.sequence"].next_by_code(
                        "partner.supplement.sales"
                    )
                    it.write({"number": seq})

                it.write({"state": "approved"})
                if template:
                    it.with_context(force_send=True).message_post_with_template(
                        template.id
                    )

    def case_rejected(self):
        for it in self:
            if it.state == "proform":
                if not it.rejected_date:
                    raise exceptions.Warning(
                        _(
                            "Debe establecer la fecha de rechazo para rechazar el documento"
                        )
                    )
                if it.rejected_date < it.emission_date:
                    raise exceptions.Warning(
                        _(
                            "La fecha de rechazo no puede ser menor que la fecha de emisión"
                        )
                    )
                if it.rejected_date > fields.Date.today():
                    raise exceptions.Warning(
                        _("La fecha de rechazo no puede ser mayor que hoy")
                    )

                it.write({"state": "rejected"})

    def case_active(self):
        template = self.env.ref(
            "alastor_partner_contract.email_template_sale_supplement_active",
            raise_if_not_found=False,
        )

        for supplement in self:
            if supplement.state != "approved":
                continue

            self._validate_activation_requirements(supplement)
            self._check_activation_dates(supplement)
            self._validate_expiration_date(supplement)
            self._handle_parent_updates(supplement)

            supplement.write({"state": "active"})
            self._send_activation_email(supplement, template)

    def _validate_activation_requirements(self, supplement):
        if not supplement.activation_date:
            raise exceptions.Warning(
                _("Debe establecer la fecha de activación para activar el documento")
            )

        if supplement.term_type == "until" and not supplement.term_date:
            raise exceptions.Warning(
                _("Debe establecer la fecha de término para activar el documento")
            )

        if supplement.term_type == "fixed":
            if not supplement.term:
                raise exceptions.Warning(
                    _("Debe establecer un término para activar el documento")
                )
            if not supplement.term_uom:
                raise exceptions.Warning(
                    _(
                        """Debe establecer la unidad de medida
                        del término para activar el documento"""
                    )
                )

    def _check_activation_dates(self, supplement):
        if supplement.activation_date < supplement.approved_date:
            raise exceptions.Warning(
                _(
                    """La fecha de activación no puede ser
                    menor que la fecha de aprobación"""
                )
            )
        if supplement.activation_date > fields.Date.today():
            raise exceptions.Warning(
                _("La fecha de activación no puede ser mayor que hoy")
            )

    def _validate_expiration_date(self, supplement):
        if (
            supplement.expiration_date
            and supplement.activation_date > supplement.expiration_date
        ):
            raise exceptions.Warning(
                _(
                    """La fecha de expiración no puede ser
                    menor que la fecha de activación"""
                )
            )

    def _handle_parent_updates(self, supplement):
        if not supplement.update_parent_validity:
            return

        for parent in [supplement.frame_parent_id, supplement.parent_id]:
            if not parent:
                continue
            self._update_parent_expiration(supplement, parent)

    def _update_parent_expiration(self, supplement, parent):
        if not supplement.expiration_date:
            parent.write({"expiration_date": False})
            return

        parent_exp_date = parent.expiration_date
        new_exp_date = supplement.expiration_date

        if (
            supplement.supplement_cause == "extension"
            and parent_exp_date < new_exp_date
        ):
            parent.write({"expiration_date": new_exp_date})
        elif (
            supplement.supplement_cause == "reduction"
            and parent_exp_date > new_exp_date
        ):
            parent.write({"expiration_date": new_exp_date})

    def _send_activation_email(self, supplement, template):
        if template:
            supplement.with_context(force_send=True).message_post_with_template(
                template.id
            )

    def case_close(self):
        template = self.env.ref(
            "alastor_partner_contract.email_template_sale_supplement_closed",
            raise_if_not_found=False,
        )

        for it in self:
            if it.state == "active":
                it.write(
                    {"close_date": date.today().strftime("%Y-%m-%d"), "state": "done"}
                )

                message = _("El suplemento '%s' ha sido cerrado.") % it.name
                it.message_post(body=message)
                it.write(
                    {"close_date": date.today().strftime("%Y-%m-%d"), "state": "done"}
                )
                if template:
                    it.with_context(force_send=True).message_post_with_template(
                        template.id
                    )

    def name_get(self):
        if self._context.get("full_name", False):
            result = []
            for record in self:
                result.append(
                    (
                        record.id,
                        record.number
                        + " - "
                        + record.name
                        + " ("
                        + record.partner_id.name
                        + ")",
                    )
                )
            return result

        return super(SaleSupplement, self).name_get()

    @api.model
    def name_search(
        self, name="", args=None, operator="ilike", limit=100, context=None
    ):
        if context is None:
            context = {}
        ids = self.env["partner.sale.supplement"].search(
            ["|", ("number", operator, name), ("name", operator, name)] + args
        )
        return ids.name_get()
