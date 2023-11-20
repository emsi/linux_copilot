import json

import pyperclip


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


ngrok_url = input("Enter ngrok URL: ")
# read input schema from terminal
openai_schema = json.loads(input("Enter OpenAPI schema: "))

gpts_schema = json.dumps(
    process_openapi_spec(openai_schema=openai_schema, ngrok_url=ngrok_url), indent=2
)
print(gpts_schema)
# copy to clipboard
print("*** Schema copied to clipboard ***")
pyperclip.copy(gpts_schema)
