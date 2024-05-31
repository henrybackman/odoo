from odoo import fields, models

class PropertyOffer(models.Model):
    _name = "property_offer"
    _description = "Property offers for tutorial"

    price = fields.Float()
    status = fields.Selection(
        string="Status",
        selection=[("accepted", "Accepted"), ("refused", "Refused"), ("pending", "Pending")],
        default="pending"
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate_property", string="Property")
