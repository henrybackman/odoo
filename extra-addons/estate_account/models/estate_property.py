from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = "estate_property"
    _inherit = "estate.estate_property"
    _description = "Estate properties for tutorial"
    _order = "id desc"