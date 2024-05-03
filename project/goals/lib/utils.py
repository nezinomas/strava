def convert_seconds_to_hours_and_minutes(seconds):
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60

    return hours, minutes


def convert_seconds_to_hours(seconds):
    hours, minutes = convert_seconds_to_hours_and_minutes(seconds)
    return hours + minutes / 60


def get_month(month: int):
    month_list = {
        1: "Sausis",
        2: "Vasaris",
        3: "Kovas",
        4: "Balandis",
        5: "Gegužė",
        6: "Birželis",
        7: "Liepa",
        8: "Rugpjūtis",
        9: "Rugsėjis",
        10: "Spalis",
        11: "Lapkritis",
        12: "Gruodis",
    }
    return month_list.get(month, 'Sausis')