from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # add field property_ids to res.users
    property_ids = fields.One2many(
        "estate_property", "salesperson_id", string="Properties"
    )
