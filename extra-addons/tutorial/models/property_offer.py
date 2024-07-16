from odoo import api, fields, models
from odoo.exceptions import UserError

class PropertyOffer(models.Model):
    _name = 'property_offer'
    _description = 'Property offers for tutorial'
    _order = 'price desc'

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
    property_type_id = fields.Many2one('property_type', related='property_id.property_type_id', string='Property Type')

    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0)', 'Property offer prices must be strictly positive')
    ]

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
                record.date_deadline = fields.Datetime.add(offer_created, days=validity_day)

    @api.depends('validity', 'date_deadline', 'create_date')
    def _set_validity(self):
        for record in self:
            offer_created = record.create_date
            if not offer_created:
                offer_created = fields.Datetime.now()
            if record.date_deadline:
                record.validity = (record.date_deadline - offer_created).days

    def action_refuse_offer(self):
        for record in self:
            record.write({'status': 'refused'})

    @api.depends('status', 'estate_property', 'partner_id')
    def action_accept_offer(self):
        for record in self:
            record.write({'status': 'accepted'})
            # update the parent property
            record.property_id.write({
                'state': 'offer_accepted',
                'buyer_id': record.partner_id,
                'selling_price': record.price
            })

    @api.model
    def create(self, vals):
        property = self.env['estate_property'].browse(vals.get('property_id'))
        # raise error if a higher offer has been received
        if property.best_price >= vals.get('price'):
            raise UserError('The offer price is not higher than the best offer received.')
        # set property state to offer_received
        property.write({'state': 'offer_received'})
        return super().create(vals)
