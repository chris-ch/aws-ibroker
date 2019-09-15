from iblight.tools import auto_str


@auto_str
class ComboLeg(object):

    def __init__(self):
        self.con_id = 0  # type  int
        self.ratio = 0  # type  int
        self.action = ""      # BUY/SELL/SSHORT
        self.exchange = ""
        self.open_close = 0   # type  int; LegOpenClose enum values
        # for stock legs when doing short sale
        self.short_sale_slot = 0
        self.designated_location = ""
        self.exempt_code = -1


@auto_str
class DeltaNeutralContract(object):

    def __init__(self):
        self.con_id = 0   # type  int
        self.delta = 0.  # type  float
        self.price = 0.  # type  float


@auto_str
class Contract(object):

    def __init__(self):
        self.con_id = 0
        self.symbol = ""
        self.sec_type = ""
        self.last_trade_date_or_contract_month = ""
        self.strike = 0.  # float !!
        self.right = ""
        self.multiplier = ""
        self.exchange = ""
        self.primary_exchange = "" # pick an actual (ie non-aggregate) exchange that the contract trades on.  DO NOT SET TO SMART.
        self.currency = ""
        self.local_symbol = ""
        self.trading_class = ""
        self.include_expired = False
        self.sec_id_type = ""	  # CUSIP;SEDOL;ISIN;RIC
        self.sec_id = ""

        #combos
        self.combolegs_descrip = ""  # type  str,received in open order 14 and up for all combos
        self.combo_legs = None     # type  list<ComboLeg>
        self.delta_neutral_contract = None


@auto_str
class ContractDetails(object):

    def __init__(self):
        self.contract = Contract()
        self.market_name = ""
        self.min_tick = 0.
        self.order_types = ""
        self.valid_exchanges = ""
        self.price_magnifier = 0
        self.under_con_id = 0
        self.long_name = ""
        self.contract_month = ""
        self.industry = ""
        self.category = ""
        self.subcategory = ""
        self.timezone_id = ""
        self.trading_hours = ""
        self.liquid_hours = ""
        self.ev_rule = ""
        self.ev_multiplier = 0
        self.md_size_multiplier = 0
        self.agg_group = 0
        self.under_symbol = ""
        self.under_sec_type = ""
        self.market_rule_ids = ""
        self.sec_id_list = None
        self.real_expiration_date = ""
        self.last_trade_time = ""
        # BOND values
        self.cusip = ""
        self.ratings = ""
        self.desc_append = ""
        self.bond_type = ""
        self.coupon_type = ""
        self.callable = False
        self.putable = False
        self.coupon = 0
        self.convertible = False
        self.maturity = ""
        self.issue_date = ""
        self.next_option_date = ""
        self.next_optiontype = ""
        self.next_option_partial = False
        self.notes = ""


@auto_str
class ContractDescription(object):
    def __init__(self):
        self.contract = Contract()
        self.derivative_sec_types = None   # type  list of strings
