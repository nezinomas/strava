def convert_seconds(seconds):
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60

    return hours, minutes