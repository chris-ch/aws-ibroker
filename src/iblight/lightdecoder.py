from iblight.refibroker import Incoming


def ib_decode(message_type, fields):
    if message_type == Incoming.CONTRACT_DATA:
        iter_field = iter(fields)
        output = {
            'version': int(load_field(iter_field)),
            'req_id': int(load_field(iter_field)),
            'symbol': load_field(iter_field),
            'sec_type': load_field(iter_field),
            'last_trade_date': load_field(iter_field),
            'strike': load_field(iter_field),
            'right': load_field(iter_field),
            'exchange': load_field(iter_field),
            'currency': load_field(iter_field),
            'local_symbol': load_field(iter_field),
            'market_name': load_field(iter_field),
            'trading_class': load_field(iter_field),
            'con_id': load_field(iter_field),
            'min_tick': load_field(iter_field),
            'md_size_multiplier': load_field(iter_field),
            'multiplier': load_field(iter_field),
            'order_types': load_field(iter_field).split(','),
            'valid_exchanges': load_field(iter_field).split(','),
            'price_magnifier': load_field(iter_field),
            'under_con_id': load_field(iter_field),
            'long_name': load_field(iter_field),
            'primary_exchange': load_field(iter_field),
            'contract_month': load_field(iter_field),
            'industry': load_field(iter_field),
            'category': load_field(iter_field),
            'subcategory': load_field(iter_field),
            'time_zone_id': load_field(iter_field),
            'trading_hours': load_field(iter_field).split(';'),
            'liquid_hours': load_field(iter_field).split(';'),
            'ev_rule': load_field(iter_field),
            'ev_multiplier': load_field(iter_field),
        }

        sec_id_list_count = int(load_field(iter_field))
        sec_id_list = []
        if sec_id_list_count > 0:
            for _ in range(sec_id_list_count):
                tag = load_field(iter_field)
                value = load_field(iter_field)
                sec_id_list.append({'tag': tag, 'value': value})

        output['sec_id_list'] = sec_id_list
        output['agg_group'] = load_field(iter_field)
        output['under_symbol'] = load_field(iter_field)
        output['under_sec_type'] = load_field(iter_field)
        output['market_rule_ids'] = load_field(iter_field).split(',')
        output['real_expiration_date'] = load_field(iter_field)

    else:
        # default
        output = {message_type.name: [field.decode('utf-8') for field in fields]}

    return output


def load_field(iter_field):
    return next(iter_field).decode('utf-8')