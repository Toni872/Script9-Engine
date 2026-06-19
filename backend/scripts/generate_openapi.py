"""Generate OpenAPI schema from FastAPI app."""
import json
import sys
sys.path.insert(0, "/app")

from app.main import app

if __name__ == "__main__":
    openapi_schema = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("openapi.json generated")
