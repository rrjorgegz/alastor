# -*- coding: utf-8 -*-
from datetime import date, datetime, time, timedelta

from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID, _, api, exceptions, fields, models
from odoo.exceptions import ValidationError, _logger


class WorkOrder(models.Model):
    _name = "work.order"
    _rec_name = "number"

    def _client_name(self):
        try:
            self.client_name = self.ref_contract_id.partner_id.name
        except exceptions.AccessError as e:
            self.client_name = ""

    name = fields.Char("Nombre")
    number = fields.Char("Número", size=64, index=True, readonly=True, default=lambda s: s.env["ir.sequence"].next_by_code("wor.ord"), help="Número único del documento, " "calculado automáticamente.")
    bill_number = fields.Integer("Número de factura")
    cost_center_ids = fields.One2many("center.cost", "work_order_id", store=True, string=" Centros de costo", required=True)
    ref_contract_id = fields.Many2one("partner.sale.contract", "Contrato referente", required=True, store=True)
    client_name = fields.Char("Nombre de cliente", compute=_client_name)
    start_date = fields.Date("Fecha Inicio", required=True)
    end_date = fields.Date("Fecha Terminación")
    state = fields.Selection([("abierto", "Abierto"), ("cerrado", "Cerrado")], string="Estado", default="abierto", required=True)
    description = fields.Text("Observacion")
    work_activity_ids = fields.One2many("work.activity", "work_order_id", store=True, string="Actividades", required=True)

    def action_cerrado(self):
        self.state = "cerrado"

    def action_abierto(self):
        self.state = "abierto"

    def write(self, vals):
        print(vals)
        print(vals.keys())
        if self.ref_contract_id:
            print(self.ref_contract_id.state)
            if self.ref_contract_id.state not in ("approval", "active"):
                raise exceptions.Warning(_("El contrato referente debe estar aprobado o activo"))
        return super(WorkOrder, self).write(vals)

    @api.model
    def create(self, vals):
        contract = self.env["partner.sale.contract"].search([("id", "=", vals.get("ref_contract_id"))])
        if contract.state not in ("approval", "active"):
            raise exceptions.Warning(_("El contrato referente está vencido o no está activo"))
        return super(WorkOrder, self).create(vals)


class WorkActivity(models.Model):
    _name = "work.activity"
    _rec_name = "name"

    name = fields.Char("Nombre", required=True)
    number = fields.Integer("Número", required=True)
    real_time = fields.Char("Tiempo real")
    work_order_id = fields.Many2one("work.order", ondelete="cascade", string="Orden de trabajo", required=True)


class CostCenter(models.Model):
    _name = "center.cost"
    _rec_name = "name"

    name = fields.Selection(
        [
            ("Proyecto", "Proyecto"),
            ("Ingenieria", "Ingeniería"),
            ("Calentadores_Solares", "Calentadores Solares"),
            ("Instrumentacion", "Instrumentación"),
            ("Tratamiento_De_Agua", "Tratamiento de Agua"),
            ("Climat_Y_Refrig", "Climat. y Refrig."),
            ("Servicios_Energeticos", "Servicios Energéticos"),
        ],
        "Nombre",
        required=True,
    )
    number = fields.Char("Código", required=True)
    work_order_id = fields.Many2one("work.order", ondelete="cascade", string="Orden de trabajo", required=True)

    _sql_constraints = [("name", "unique(name)", "No puede existir centros de costos con el mismo nombre")]
