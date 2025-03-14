from flask import request, jsonify, current_app

def authenticate_request():
    """
    Authenticates incoming requests using the API key stored in app.config.
    """
    print("Authenticate function called.")

    auth_header = request.headers.get('Authorization')
    expected_key = current_app.config['API_KEY']
    print(f"Authorization Header: {auth_header}")
    print(f"Expected API Key: {expected_key}")

    if not auth_header:
        return jsonify({'error': 'Authorization header is missing'}), 401

    parts = auth_header.split()
    if len(parts) != 2 or parts[0] != 'Bearer':
        return jsonify({'error': 'Invalid Authorization header format'}), 401

    token = parts[1]
    if token != expected_key:
        return jsonify({'error': 'Unauthorized access'}), 401

    return None

