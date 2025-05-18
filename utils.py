from datetime import date, timedelta


def end_of_previous_quarter(for_date=None):
    for_date = for_date or date.today()
    q_start_month = (for_date.month - 1) // 3 * 3 + 1
    q_start = for_date.replace(month=q_start_month, day=1)
    return q_start - timedelta(days=1)
