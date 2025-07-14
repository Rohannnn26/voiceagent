# integrations/date_utils.py
from datetime import date, timedelta

def get_current_fy_dates():
    current_year = date.today().year
    start = date(current_year, 4, 1)
    end = date(current_year + 1, 3, 31)
    return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")

def get_previous_fy_dates():
    today = date.today()
    start = date(today.year - 1, 4, 1)
    end = date(today.year, 3, 31)
    return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")

def get_financial_year(dt):
    """Return the start and end date of the financial year for a given date."""
    if dt.month >= 4:
        start = date(dt.year, 4, 1)
        end = date(dt.year + 1, 3, 31)
    else:
        start = date(dt.year - 1, 4, 1)
        end = date(dt.year, 3, 31)
    return start, end

def get_last_n_months_dates(n):
    end = date.today()
    start = end - timedelta(days=30 * n)
    fy_start, fy_end = get_financial_year(end)
    if fy_start <= start <= fy_end:
        return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")
    else:
        print("Start and end dates must be within the same financial year.")
        start = fy_start
        return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")



def get_current_fy_fixed():
    """
    Returns start and end dates for the current financial year based on today's date.
    """
    current_year = date.today().year
    start = date(current_year - 1, 4, 1)
    end = date(current_year, 3, 31)
    return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")

def get_previous_fy_fixed():
    """
    Returns start and end dates for the previous financial year as:
    04/01/(current_year-2) to 03/31/(current_year-1)
    Example: If current year is 2025, returns 04/01/2023 to 03/31/2024
    """
    current_year = date.today().year
    start = date(current_year - 2, 4, 1)
    end = date(current_year - 1, 3, 31)
    return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")

def date_range(type):
    if type == '3_month':
        return get_last_n_months_dates(3)
    elif type == '6_month':
        return get_last_n_months_dates(6)
    elif type in 'current_fy':
        return get_current_fy_dates()
    elif type in ['current_fy_itr',"current_fy_stt_ctt"]:
        return get_current_fy_fixed()
    elif type in ['previous_fy_itr', 'previous_fy_stt_ctt']:
        return get_previous_fy_fixed()
    elif type in 'previous_fy':
        return get_previous_fy_dates()
    else:
        return None,None



