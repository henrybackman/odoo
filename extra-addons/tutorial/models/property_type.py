from odoo import fields, models

class PropertyType(models.Model):
    _name = "property_type"
    _description = "Property types for tutorial"

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate_property', 'property_type_id', string='Properties')
