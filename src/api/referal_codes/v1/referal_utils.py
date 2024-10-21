def validate_referal_code(code):
    str_code = str(code)
    if not str_code.isdigit() or len(str_code) != 4:
        return False
    return True
