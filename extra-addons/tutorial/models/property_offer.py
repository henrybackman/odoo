from odoo import api, fields, models

class PropertyOffer(models.Model):
    _name = 'property_offer'
    _description = 'Property offers for tutorial'

    price = fields.Float()
    status = fields.Selection(
        string='Status',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused'), ('pending', 'Pending')],
        default='pending'
    )
    partner_id = fields.Many2one('res.partner', string='Partner')
    property_id = fields.Many2one('estate_property', string='Property')
    validity = fields.Integer()
    date_deadline = fields.Datetime(compute='_compute_date_deadline', inverse='_set_validity', store=True)

    @api.depends('validity', 'date_deadline', 'create_date')
    def _compute_date_deadline(self):
        for record in self:
            offer_created = record.create_date
            if not offer_created:
                offer_created = fields.Datetime.now()

            validity_day = record.validity
            if not validity_day:
                validity_day = 0
                
            if record.validity:
                record.date_deadline = fields.Datetime.add(offer_created, days=record.validity)

    @api.depends('validity', 'date_deadline', 'create_date')
    def _set_validity(self):
        for record in self:
            offer_created = record.create_date
            if not offer_created:
                offer_created = fields.Datetime.now()
            if record.date_deadline:
                record.validity = (record.date_deadline - offer_created).days
