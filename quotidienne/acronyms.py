import re

from pampy import _, match


# Parse the aconym form email addresses
def get_acronym(email):
    return match(
        email,
        re.compile(r".* <(\w{4}\d{0,2})@premiertech.com>"),
        lambda acro: acro.upper(),
        _,
        None,
    )


def mapping_with_acronyms(team):
    acros = [get_acronym(id) for id in team]
    return dict(zip(team, acros))

