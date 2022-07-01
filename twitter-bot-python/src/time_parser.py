from datetime import datetime, timedelta


class TimeParser:

    @staticmethod
    def get_time(string_value):
        date_time = TimeParser._safe_parse(string_value, "%Y-%m-%dT%H:%M:%S.%f")
        if date_time is not None:
            return date_time
        date_time = TimeParser._safe_parse(string_value, "%Y-%m-%dT%H:%M:%S")
        if date_time is not None:
            return date_time
        date_time = TimeParser._safe_parse(string_value, "%Y-%m-%dT%H:%M")
        if date_time is not None:
            return date_time
        date = TimeParser._safe_parse(string_value, "%Y-%m-%d")
        if date is not None:
            return date + timedelta(days=1)
        return None

    @staticmethod
    def _safe_parse(string_value, format_string):
        try:
            date_time = datetime.strptime(string_value, format_string)
            return date_time
        except ValueError:
            pass
        try:
            date_time = datetime.strptime(string_value, format_string + 'Z')
            return date_time
        except ValueError:
            pass
        return None
