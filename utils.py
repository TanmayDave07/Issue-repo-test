def divide(a, b):
    if b == 0:
        return 0
    return a / b


def get_user_name(user):
    return user.get("name", "")


def parse_age(age):
    try:
        return int(age)
    except:
        return 0
