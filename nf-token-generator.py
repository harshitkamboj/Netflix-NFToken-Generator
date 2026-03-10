import json
import re
import os

import requests

# File the script reads the Netflix cookie from.
INPUT_FILE = "input.txt"

# Netflix GraphQL endpoint used by the mobile client to request an auto-login token.
API_URL = "https://android13.prod.ftl.netflix.com/graphql"

# Request headers copied from a Netflix Android client so the request matches
# what Netflix expects for this token-generation operation.
# The important part is that this request looks like a normal mobile-app call
# instead of a random generic HTTP request.
HEADERS = {
    "User-Agent": "com.netflix.mediaclient/63884 (Linux; U; Android 13; ro; M2007J3SG; Build/TQ1A.230205.001.A2; Cronet/143.0.7445.0)",
    "Accept": "multipart/mixed;deferSpec=20220824, application/graphql-response+json, application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.netflix.com",
    "Referer": "https://www.netflix.com/",
}
PAYLOAD = {
    "operationName": "CreateAutoLoginToken",
    "variables": {"scope": "WEBVIEW_MOBILE_STREAMING"},
    "extensions": {
        "persistedQuery": {
            "version": 102,
            "id": "76e97129-f4b5-41a0-a73c-12e674896849",
        }
    },
}

# Minimum cookie values needed for Netflix to accept the token request.
# These identify the logged-in Netflix session. Without them, Netflix will
# reject the token-generation request.
REQUIRED_COOKIES = ("NetflixId", "SecureNetflixId", "nfvdid")


def ensure_input_file():
    # Create the input file on first run so the user knows where to paste the cookie.
    if not os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "w") as file_handle:
            file_handle.write("NetflixId=...; SecureNetflixId=...; nfvdid=...\n")
        print("Created input.txt")
        print("Add your cookie in input.txt and run again")
        return None

    # Read the cookie text exactly as written in input.txt.
    with open(INPUT_FILE, "r") as file_handle:
        content = file_handle.read().strip()

    if not content:
        print("input.txt is empty")
        print("Add your cookie in input.txt and run again")
        return None

    return content


def parse_netscape_cookie_line(line):
    # Support Netscape-exported cookie lines:
    # domain, flag, path, secure, expiry, name, value
    parts = line.strip().split("\t")
    if len(parts) >= 7:
        return {parts[5]: parts[6]}
    return {}


def extract_cookie_dict(text):
    # Normalize whatever is inside input.txt into one cookie dictionary.
    # This lets the script accept Netscape format, JSON, or a raw cookie string.
    cookie_dict = {}

    # Try Netscape format first.
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        cookie_dict.update(parse_netscape_cookie_line(line))

    if any(name in cookie_dict for name in REQUIRED_COOKIES):
        return cookie_dict

    # Try JSON input like {"NetflixId":"...", "SecureNetflixId":"..."}.
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None

    if isinstance(data, dict):
        for key in (*REQUIRED_COOKIES, "OptanonConsent"):
            value = data.get(key)
            if isinstance(value, str):
                cookie_dict[key] = value
        if cookie_dict:
            return cookie_dict

    # Fall back to parsing a raw cookie header string.
    for key in (*REQUIRED_COOKIES, "OptanonConsent"):
        match = re.search(rf"{re.escape(key)}=([^;\s]+)", text)
        if match:
            cookie_dict[key] = match.group(1)

    return cookie_dict


def build_cookie_header(cookie_dict):
    # Convert the parsed dictionary back into the Cookie header format
    # that Netflix expects on the request.
    return "; ".join(f"{key}={value}" for key, value in cookie_dict.items())


def build_nftoken_link(token):
    # Netflix accepts the generated token in URL form:
    # https://www.netflix.com/?nftoken=...
    # Returning the full link makes the console output directly usable.
    return "https://www.netflix.com/?nftoken=" + token


def fetch_nftoken(cookie_dict):
    # Netflix requires these session cookies before it will generate
    # an auto-login token for the account session.
    missing = [name for name in REQUIRED_COOKIES if not cookie_dict.get(name)]
    if missing:
        raise ValueError("Missing required cookies: " + ", ".join(missing))

    headers = dict(HEADERS)
    headers["Cookie"] = build_cookie_header(cookie_dict)

    # This POST asks Netflix to run the GraphQL mutation createAutoLoginToken.
    # If the cookie belongs to a valid session and the account is allowed to
    # use this flow, Netflix returns the nftoken inside:
    # data.createAutoLoginToken
    #
    # That token can then be placed into a Netflix URL as ?nftoken=...
    response = requests.post(API_URL, headers=headers, json=PAYLOAD, timeout=30)
    response.raise_for_status()

    data = response.json()
    data_block = data.get("data") or {}
    token = data_block.get("createAutoLoginToken")
    if token:
        return token

    errors = data.get("errors")
    if errors:
        raise ValueError(json.dumps(errors, ensure_ascii=True))

    raise ValueError("Token not found in response.")


def main():
    # Step 1: load the cookie text from input.txt.
    raw_cookie = ensure_input_file()
    if raw_cookie is None:
        return

    # Step 2: extract the required Netflix cookie values from that text.
    cookie_dict = extract_cookie_dict(raw_cookie)
    if not cookie_dict:
        print("No valid cookie found in input.txt.")
        return

    try:
        # Step 3: request the nftoken from Netflix.
        token = fetch_nftoken(cookie_dict)

        # Step 4: print the ready-to-use Netflix link in the console.
        print(build_nftoken_link(token))
    except requests.RequestException as exc:
        print("Request failed: " + str(exc))
    except ValueError as exc:
        print("Failed: " + str(exc))


if __name__ == "__main__":
    main()
