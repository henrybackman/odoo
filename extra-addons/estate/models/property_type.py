from odoo import fields, models


class PropertyType(models.Model):
    _name = "property_type"
    _description = "Property types for tutorial"
    _order = "name"

    name = fields.Char(required=True)
    property_ids = fields.One2many(
        "estate_property", "property_type_id", string="Properties"
    )
    offer_ids = fields.One2many("property_offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(compute="_compute_offer_count")
    sequence = fields.Integer(default=10)

    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

        return True

    def action_property_type_offers(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Offers",
            "res_model": "property_offer",
            "view_mode": "tree,form",
            "domain": [("property_id", "=", self.property_id.id)],
            "context": {"default_property_id": self.property_id.id},
        }
