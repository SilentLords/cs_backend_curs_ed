import decimal


def convert_blockchain_value_to_decimal(value: str) -> decimal.Decimal:
    return decimal.Decimal(value) / 1000000000000000000


def convert_decimal_to_evo_int(value: decimal.Decimal) -> int:
    decimal_str = f"{str(value).replace('.', '')}00"
    return int(decimal_str)
    # return f"{round((decimal.Decimal(value) * decimal.Decimal(1000000000000000000)), 0)}"


def convert_decimal_to_evo_int_for_contract(value: decimal.Decimal) -> int:
    return int(f"{round((decimal.Decimal(value) * decimal.Decimal(1000000000000000000)), 0)}")
