from odoo import fields, models


class PropertyTag(models.Model):
    _name = "property_tag"
    _description = "Property tags"

    name = fields.Char(required=True)

    _sql_constraints = [
        ("check_tag_uniqueness", "UNIQUE(name)", "Tag name must be unique")
    ]
