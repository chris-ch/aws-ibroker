from marshmallow import Schema, fields, post_load

from iblight.model import Contract


class DeltaNeutralContractSchema(Schema):
    con_id = fields.Integer(required=False)
    delta = fields.Float(required=False)
    price = fields.Float(required=False)


class ComboLegSchema(Schema):
    con_id = fields.Integer(required=False)
    ratio = fields.Integer(required=False)
    action = fields.String(required=False)
    exchange = fields.String(required=False)
    open_close = fields.Integer(required=False)
    short_sale_slot = fields.Integer(required=False)
    designated_location = fields.String(required=False)
    exempt_code = fields.Integer(required=False)


class ContractSchema(Schema):
    con_id = fields.String(required=False)
    symbol = fields.String(required=False)
    sec_type = fields.String(required=False)
    last_trade_date_or_contract_month = fields.String(required=False)
    strike = fields.Float(required=False)
    right = fields.String(required=False)
    multiplier = fields.String(required=False)
    exchange = fields.String(required=False)
    primary_exchange = fields.String(required=False)
    currency = fields.String(required=False)
    local_symbol = fields.String(required=False)
    trading_class = fields.String(required=False)
    include_expired = fields.Boolean(required=False)
    sec_id_type = fields.String(required=False)
    sec_id = fields.String(required=False)
    combo_legs_descrip = fields.String(required=False)
    combo_legs = fields.List(fields.Nested(ComboLegSchema), required=False)
    delta_neutral_contract = fields.Nested(DeltaNeutralContractSchema, required=False)

    @post_load
    def make_object(self, attributes, **kwargs):
        if not attributes:
            return None

        contract = Contract()
        for name in attributes:
            setattr(contract, name, attributes[name])

        return contract


class ContractDescriptionSchema(Schema):
    contract = fields.Nested(ContractSchema, required=True)
    derivative_sec_types = fields.List(fields.String(), required=False)


class ContractDetailsSchema(Schema):
    contract = fields.Nested(ContractSchema, required=True)
    market_name = fields.String(required=False)
    min_tick = fields.Integer(required=False)
    order_types = fields.String(required=False)
    valid_exchanges = fields.String(required=False)
    price_magnifier = fields.Integer(required=False)
    under_con_id = fields.Integer(required=False)
    long_name = fields.String(required=False)
    contract_month = fields.String(required=False)
    industry = fields.String(required=False)
    category = fields.String(required=False)
    subcategory = fields.String(required=False)
    timezone_id = fields.String(required=False)
    trading_hours = fields.String(required=False)
    liquid_hours = fields.String(required=False)
    ev_rule = fields.String(required=False)
    ev_multiplier = fields.Integer(required=False)
    md_size_multiplier = fields.Integer(required=False)
    agg_group = fields.Integer(required=False)
    under_symbol = fields.String(required=False)
    under_sec_type = fields.String(required=False)
    market_rule_ids = fields.String(required=False)
    sec_id_list = fields.List(fields.String(), required=False)
    real_expiration_date = fields.String(required=False)
    last_trade_time = fields.String(required=False)
    cusip = fields.String(required=False)
    ratings = fields.String(required=False)
    desc_append = fields.String(required=False)
    bond_type = fields.String(required=False)
    coupon_type = fields.String(required=False)
    callable = fields.Boolean(required=False)
    putable = fields.Boolean(required=False)
    coupon = fields.Integer(required=False)
    convertible = fields.Boolean(required=False)
    maturity = fields.String(required=False)
    issue_date = fields.String(required=False)
    next_option_date = fields.String(required=False)
    next_option_type = fields.String(required=False)
    next_option_partial = fields.Boolean(required=False)
    notes = fields.String(required=False)
