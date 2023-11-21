import json

import pyperclip
import requests


def process_openapi_spec(openai_schema, ngrok_url):
    """Process an OpenAPI specification to add default values"""
    # Default structure for the output
    output_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "Untitled",
            "description": "Your OpenAPI specification",
            "version": "v1.0.0",
        },
        "servers": [{"url": ""}],
        "paths": {},
        "components": {"schemas": {}},
    }

    # Update the fields from the input specification
    output_spec["openapi"] = openai_schema.get("openapi", output_spec["openapi"])
    output_spec["info"] = openai_schema.get("info", output_spec["info"])
    output_spec["paths"] = openai_schema.get("paths", output_spec["paths"])
    output_spec["components"] = openai_schema.get("components", output_spec["components"])

    # Setting a default URL (can be modified as needed)
    output_spec["servers"][0]["url"] = ngrok_url

    return output_spec


def fetch_openapi_json(url):
    """Fetch an OpenAPI specification from a URL"""
    response = requests.get(f"{url}/openapi.json")
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    url = input("Enter URL: ")

    if url.endswith("/openapi.json"):
        url = url[:-13]
    if url.endswith("/openapi.yaml"):
        url = url[:-13]
    if url.endswith("/"):
        # remove all trailing slashes
        url = url.rstrip("/")

    try:
        openai_schema = fetch_openapi_json(url)
    except Exception as e:
        print(f"Could not fetch OpenAPI schema from URL: {url}/openapi.json")
        print("Make sure the URL is correct and the server is running.")
        raise e

    gpts_schema = json.dumps(
        process_openapi_spec(openai_schema=openai_schema, ngrok_url=url), indent=2
    )
    print(gpts_schema)
    # copy to clipboard
    print("*** GPTs action schema copied to clipboard ***")
    pyperclip.copy(gpts_schema)
