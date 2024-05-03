def convert_seconds(seconds: int) -> tuple[int, int, int]:
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60

    return hours, minutes, seconds


def convert_seconds_to_hours(seconds):
    hours, minutes, seconds = convert_seconds(seconds)
    return hours + minutes / 60 + seconds / 3600


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