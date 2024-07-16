from odoo import fields, models


class PropertyTag(models.Model):
    _name = "property_tag"
    _description = "Property tags"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ("check_tag_uniqueness", "UNIQUE(name)", "Tag name must be unique")
    ]
