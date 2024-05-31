from odoo import fields, models

class PropertyTag(models.Model):
    _name = "property_tag"
    _description = "Property tags"

    name = fields.Char(required=True)
