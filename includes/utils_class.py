import functools

# Valid date parser
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None

# 🔥 Decorator for cleaning JSON and text
def clean_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, list):
            cleaned_result = [
                {k: re.sub(r'\s+', ' ', str(v).strip()) if isinstance(v, str) else v for k, v in item.items()}
                for item in result
            ]
            return cleaned_result
        elif isinstance(result, str):
            return re.sub(r'\s+', ' ', result.strip())
        else:
            return result
    return wrapper

# Clean and cap text
@clean_data
def clean_and_truncate(text, length=200):
    if len(text) > length:
        truncated = text[:length].rsplit(' ', 1)[0] + '...'
        return truncated
    return text