from odoo import fields, models

class PropertyType(models.Model):
    _name = "property_type"
    _description = "Property types for tutorial"

    name = fields.Char(required=True)
