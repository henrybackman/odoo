from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class Property(models.Model):
    _name = "property"
    _description = "Estate properties for tutorial"
    _order = "id desc"

    name = fields.Char(required=True, copy=False)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=fields.Date.add(fields.Date.today(), months=3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string="Type",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        help="Garden orientation",
    )
    active = fields.Boolean(default=True, string="Available")
    state = fields.Selection(
        required=True,
        string="Status",
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        copy=False,
        default="new",
    )
    property_type_id = fields.Many2one("property_type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one(
        "res.users", string="Sales person", default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many("property_tag", string="Property Tags")
    offer_ids = fields.One2many("property_offer", "property_id", string="Offers")
    total_area = fields.Integer(compute="_compute_total_area", store=True)
    best_price = fields.Float(readonly=True, compute="_compute_best_price")

    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price > 0)",
            "Expected price must be strictly positive",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price >= 0)",
            "Selling price must be positive",
        ),
        ("name_uniq", "UNIQUE(name)", "Property name must be unique"),
    ]

    # if either expected price or selling price is changed
    # constraint to check the selling price is at least 90% of the expected
    # price
    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            if not record.selling_price or not record.expected_price:
                continue
            if record.selling_price < record.expected_price * 0.9:
                raise ValidationError(
                    _(
                        "The selling price cannot be less than 90% of the \
                        expected price."
                    )
                )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.mapped("offer_ids.price") or [0]

            record.best_price = max(prices)

    @api.onchange("garden")
    def _onchange_garden(self):
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden_orientation = "north"
            else:
                record.garden_area = 0
                record.garden_orientation = False

    def action_sell_property(self):
        for record in self:
            if record.state == "canceled":
                raise UserError(_("You cannot sell a canceled property."))
            record.write({"state": "sold"})
        return True

    def action_cancel_property(self):
        for record in self:
            if record.state == "sold":
                raise UserError(_("You cannot cancel a sold property."))
            record.write({"state": "canceled"})
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        for record in self:
            if record.state not in ["new", "canceled"]:
                raise UserError(
                    _(
                        "You cannot delete a property that is not new or \
                      canceled."
                    )
                )
