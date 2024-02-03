# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError, _logger
from odoo.tools.misc import format_date, formatLang, get_lang


class AuthorizedSignature(models.Model):
    _name = "organism"
    _rec_name = "name"

    name = fields.Char("Nombre", required=True)

    _sql_constraints = [("name", "unique(name)", "Ya existe ese organismo")]
