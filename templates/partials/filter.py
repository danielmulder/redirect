from flask import Flask

def truncate_url(url, length=35):
    if len(url) > length:
        return f"{url[:length]}..."
    return url
