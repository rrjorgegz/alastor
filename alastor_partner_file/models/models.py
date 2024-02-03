from datetime import datetime
from operator import itemgetter

from openerp import _, api, exceptions, fields, models


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    def _get_client_files_count(self):
        try:
            self.client_files_count = len(self.client_file_ids)
        except exceptions.AccessError as e:
            self.client_files_count = 0

    foreign_currency_license = fields.Char(string="Licencia para operar en divisas")
    client_file_ids = fields.One2many("res.partner.file", "partner_id", "Client Files")
    client_files_count = fields.Integer(compute=_get_client_files_count, string="Fichas de cliente")


class ClientFileContactInvoice(models.Model):
    _name = "res.partner.file.contact.invoice"
    _description = "Autorizados a firmar facturas"

    client_file_id = fields.Many2one("res.partner.file", string="Client File", ondelete="cascade")
    name = fields.Char("Nombre y apellidos", required=True)
    id_number = fields.Char("CI", size=11)
    job = fields.Char("Cargo")


class ClientFileContactReconciliation(models.Model):
    _name = "res.partner.file.contact.reconciliation"
    _description = "Autorizados a firmar conciliaciones"

    client_file_id = fields.Many2one("res.partner.file", string="Client File", ondelete="cascade")
    name = fields.Char("Nombre y apellidos", required=True)
    id_number = fields.Char("CI", size=11)
    job = fields.Char("Cargo")


class ClientFile(models.Model):
    _name = "res.partner.file"
    _description = "Ficha de clientes"

    def name_get(self, cr, uid, ids, context=None):
        result = []
        for item in self.browse(cr, uid, ids, context):
            result.append((item.id, (item.initial_date and (item.initial_date) + " -> " or " ") + (item.final_date and (item.final_date) or " ")))
        return result

    partner_id = fields.Many2one("res.partner", string="Cliente", required=True, ondelete="cascade")
    initial_date = fields.Date("Fecha de inicio")
    final_date = fields.Date("Fecha de fin")
    director_name = fields.Char("Nombre y apellidos del director o equivalente")
    director_id_number = fields.Char("CI del director o equivalente")
    represent_name = fields.Char("Nombre y apellidos del representante para firmar contratos")
    represent_id_number = fields.Char("CI del representante para firmar contratos")
    represent_job = fields.Char("Cargo del representante para firmar contratos")
    state = fields.Selection([("draft", "Borrador"), ("active", "Activa"), ("cancel", "Cancelada")], string="Estado", default="draft")
    invoice_authorized_ids = fields.One2many("res.partner.file.contact.invoice", "client_file_id", string="Personas autorizadas a solicitar servicios y firmar facturas")
    reconciliation_authorized_ids = fields.One2many("res.partner.file.contact.reconciliation", "client_file_id", string="Personas autorizadas a firmar conciliaciones")

    def case_activate(self):
        # verify if it has some mandatory fields
        if not self.initial_date:
            raise exceptions.Warning(_("Debe proveer una fecha de inicio antes de activar la ficha de cliente"))
        self.write({"state": "active"})
        return True

    def case_cancel(self):
        if not self.final_date:
            raise exceptions.Warning(_("Debe proveer una fecha de fin antes de cancelar la ficha de cliente"))
        self.write({"state": "cancel"})
        return True

    def unlink(self):
        if self.state not in ("draft",):
            raise exceptions.Warning(_("Solo se pueden eliminar las fichas de cliente en estado borrador"))
        super(ClientFile, self).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default["initial_date"] = datetime.today().strftime("%Y-%m-%d")
        default["state"] = "draft"
        res = super(ClientFile, self).copy(default)
        for ia in self.invoice_authorized_ids:
            vals = {"client_file_id": res.id, "name": ia.name, "id_number": ia.id_number, "job": ia.job}
            self.env["res.partner.file.contact.invoice"].create(vals)

        for ra in self.reconciliation_authorized_ids:
            vals = {"client_file_id": res.id, "name": ra.name, "id_number": ra.id_number, "job": ra.job}
            self.env["res.partner.file.contact.reconciliation"].create(vals)

        return res
