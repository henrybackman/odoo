from odoo import api, fields, models, _

class EstateProperty(models.Model):
    _name = 'estate_property'
    _description = 'Estate properties for tutorial'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Type',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help='Garden orientation'
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        required=True,
        string='Status',
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'),
                   ('sold', 'Sold'), ('canceled', 'Canceled')],
        copy=False,
        default='new'
    )
    property_type_id = fields.Many2one('property_type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesperson_id = fields.Many2one('res.users', string='Sales person', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('property_tag', string='Property Tags')
    offer_ids = fields.One2many('property_offer', 'property_id', string='Offers')
    total_area = fields.Integer(compute='_compute_total_area', store=True)
    best_price = fields.Float(readonly=True, compute='_compute_best_price')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            prices = record.mapped('offer_ids.price') or [0]
            record.best_price = max(prices)

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False
            return {'warning': {
                'title': _('Warning'),
                'message': ('Property without a garden won\'t sell')}}
        
