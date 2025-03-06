# text_utility.py
import json
import time
import requests

# ✅ Configurations
MAX_INPUT_LENGTH = 100  # Maximum allowed input length for the search query
REQUESTS_PER_MINUTE = 25  # Rate limit: maximum number of requests per minute
user_requests = {}  # Dictionary to track user request timestamps for rate limiting

# ✅ Function: Rate Limiting
def is_rate_limited(ip: str) -> bool:
    """
    Checks if an IP address has exceeded the allowed request limit per minute.

    Args:
        ip (str): The IP address of the user.

    Returns:
        bool: True if the IP has exceeded the limit, False otherwise.
    """
    now = time.time()
    requests = user_requests.get(ip, [])

    # Remove outdated requests (older than 60 seconds)
    requests = [t for t in requests if now - t < 60]

    # Check if the request count exceeds the limit
    if len(requests) >= REQUESTS_PER_MINUTE:
        return True

    # Store the current request timestamp
    requests.append(now)
    user_requests[ip] = requests
    return False

# ✅ Function: Perform a Google Search using SerpApi with dynamic settings
def google_search(query, api_key, hl="nl", gl="nl", num_results=10):
    """
    Executes a Google Search using SerpApi and retrieves search results.

    Args:
        query (str): The search query.
        api_key (str): The API key for SerpApi.
        hl (str): Language setting for search results (default: "nl" for Dutch).
        gl (str): Geolocation/country code for search results (default: "nl" for Netherlands).
        num_results (int): Number of search results to retrieve (default: 10).

    Returns:
        list[dict]: A list of search result dictionaries containing title, link, and snippet.
    """
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "hl": hl,   # Language
        "gl": gl,   # Country
        "num": num_results,  # Number of results
        "api_key": api_key
    }

    response = requests.get(url, params=params)

    # Handle API errors
    if response.status_code != 200:
        return {"error": f"Google API error: {response.status_code}", "details": response.text}

    data = response.json()
    search_results = []

    # Extract search results
    if "organic_results" in data:
        for result in data["organic_results"]:
            search_results.append({
                "title": result.get("title", "No Title"),
                "link": result.get("link", "No Link"),
                "snippet": result.get("snippet", "No Description")
            })

    return search_results

def object_to_dict(obj):
    """Zet een object met attributen om naar een dictionary."""
    if hasattr(obj, '__dict__'):
        return {key: object_to_dict(value) if hasattr(value, '__dict__') else value
                for key, value in obj.__dict__.items()}
    return obj  # Als het al een dictionary is, verander niets

# ✅ Main Serverless Function
def main(args):
    """
    Main entry point for the serverless function.

    This function processes incoming requests, applies rate limiting,
    validates input parameters, and performs a Google Search if requested.

    Args:
        args (dict): Dictionary containing request parameters.

    Returns:
        dict: JSON response containing search results or error messages.
    """
    start_time = time.perf_counter()

    # Extract IP address from headers for rate limiting
    ip = args.get("__ow_headers", {}).get("x-forwarded-for", "unknown")

    # ✅ Enforce rate limiting
    if is_rate_limited(ip):
        return {
            "body": json.dumps({
                "error": "Too many requests. Try again later.",
                "retry_after": 60  # Retry after 60 seconds
            }),
            "statusCode": 429
        }

    # ✅ Extract search query from arguments
    text = args.get("text")
    if not text:
        return {"body": json.dumps({"error": "No valid text provided!"}), "statusCode": 400}

    if not isinstance(text, str):
        return {"body": json.dumps({"error": "Expected a string!"}), "statusCode": 400}

    # ✅ Validate action type
    action = args.get("action")
    if action != "google_search":
        return {"body": json.dumps({"error": f"Action {action} is not valid!"}), "statusCode": 400}

    # ✅ Extract API key
    #api_key = args.get("api_key")
    api_key = "900be7c9de6f6de853b821e996b6363db00b0523e3bb71572282cd6a4c156f79"
    if not api_key:
        return {"body": json.dumps({"error": "Missing API key for Google search!"}), "statusCode": 400}

    # ✅ Extract optional search parameters (fallback to default values)
    hl = args.get("hl", "nl")  # Language, default: Dutch
    gl = args.get("gl", "nl")  # Country, default: Netherlands
    num_results = int(args.get("num_results", 10))  # Number of results, default: 10

    if num_results >= 31:
         num_results = 30

    # ✅ Perform Google Search
    result = google_search(text, api_key, hl=hl, gl=gl, num_results=num_results)

    # ✅ Calculate processing time
    total_time = round((time.perf_counter() - start_time) * 1000, 2)

    # ✅ Return JSON response
    return {
        "body": json.dumps({f"{action}": result, "processing_time_ms": total_time}),
        "statusCode": 200
    }

if __name__ == "__main__":

    class ArgsObject:
        def __init__(self):
            self.__ow_headers = {"x-forwarded-for": "192.168.1.1"}
            self.url = "https://example.com"

    local_args = ArgsObject()
    args = object_to_dict(local_args)