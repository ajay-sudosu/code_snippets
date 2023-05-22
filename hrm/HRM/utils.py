from datetime import datetime


def change_date(date):
    changed_date = datetime.strptime(date, '%Y-%m-%d').date()
    return changed_date


def change_time(time):
    changed_time = datetime.strptime(time, '%H:%M').time()
    time_value_12hr = changed_time.strftime('%I:%M %p')
    return time_value_12hr
