def _sign_for_negative(num: int) -> str:
    return "-" if num < 0 else ""


def pretty_big_num(num: int) -> str:
    """
    Pretty-print for big numbers
    """
    if abs(num) < 1000:
        return str(num)

    k_number = abs(num) / 1000
    res = f"{_sign_for_negative(num)}{k_number:.1f}k"

    if ".0k" in res:
        res = res.replace(".0k", "k")
    return res
