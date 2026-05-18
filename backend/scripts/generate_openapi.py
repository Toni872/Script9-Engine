"""Script para exportar el esquema OpenAPI de la aplicación a openapi.json."""

import json
from pathlib import Path


def generate_openapi() -> None:
    """Genera y guarda el esquema OpenAPI en la raíz del proyecto."""
    from app.main import app

    schema = app.openapi()
    output_path = Path(__file__).parent.parent / "openapi.json"
    output_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False))
    print(f"✅ openapi.json generado en: {output_path}")


if __name__ == "__main__":
    generate_openapi()
