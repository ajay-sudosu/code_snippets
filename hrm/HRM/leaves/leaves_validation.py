from datetime import datetime


def format_time(time):
    if time:
        formatted_time = datetime.strptime(time, "%H:%M").time()
    else:
        formatted_time = None
    return formatted_time


def format_date(date):
    formatted_date = datetime.strptime(date, "%Y-%m-%d")
    return formatted_date.date()


def convert_time_to_hrs_minute(time):
    converted_time = datetime.strptime(time, '%H:%M').time()
    return converted_time


def get_total_hours(hour):
    total_hours = hour
    return total_hours


def convert_into_days(hours):
    return hours / 8


def validate_leaves(leaves_list, remaining_leaves):
    half_day_hrs = 4
    short_leave_hrs = 2
    dates_list = []
    start_time_list = []
    end_time_list = []
    check = list(zip(dates_list, start_time_list, end_time_list))
    total_days_of_leave = 0
    try:
        for i in leaves_list:
            if i.get("leaveType").lower() == "shortleave":
                date = format_date(i.get("startDate"))
                print("This is short-day.")
                start_time = i.get("startTime")
                print(f"Start Time:{start_time}")
                end_time = format_time(i.get("endTime"))
                print(f"End time: {end_time}")
                start_time = convert_time_to_hrs_minute(i.get("startTime"))
                end_time = convert_time_to_hrs_minute(i.get("endTime"))
                if (date, start_time, end_time) in check:
                    return False, "You have already selected leave for the same."
                total_days_of_leave += convert_into_days(2)

            elif i.get("leaveType").lower() == "halfday":
                date = format_date(i.get("startDate"))
                print("This is half-day.")
                start_time = format_time(i.get("startTime"))
                end_time = format_time(i.get("endTime"))
                print(f"Start time- {start_time}")
                print(f"End time- {end_time}")
                # start_time = convert_time_to_hrs_minute(start_time)
                start_time = convert_time_to_hrs_minute(i.get("startTime"))
                end_time = convert_time_to_hrs_minute(i.get("endTime"))
                hour = end_time.hour - start_time.hour
                minute = end_time.minute - start_time.minute
                if (date, start_time, end_time) in check:
                    return False, "You have already selected leave for the same."
                total_days_of_leave += convert_into_days(half_day_hrs)
            else:
                print("This is full-day.")
                date = format_date(i.get("startDate"))
                if date in dates_list:
                    return False, "You have already selected leave for the day."
                else:
                    print(f"date: {date}")
                    dates_list.append(date)
                    total_days_of_leave += 1
        print(total_days_of_leave)
        if total_days_of_leave > remaining_leaves:
            return True, f"Leaves will be paid for: {total_days_of_leave - remaining_leaves} days/days"
        else:
            return True, remaining_leaves - total_days_of_leave
    except Exception as error:
        print(error)
