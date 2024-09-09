import json
import sys
import tempfile
from pathlib import Path

import requests

from fastagency.openapi.client import Client
from fastagency.openapi.security import APIKeyHeader


def test_secure_app_openapi(secure_fastapi_url: str) -> None:
    expected_openapi_json_path = Path(__file__).parent / "expected_openapi.json"
    with expected_openapi_json_path.open() as f:
        expected_openapi_json = json.loads(
            f.read().replace("http://localhost:9999", secure_fastapi_url)
        )

    resp = requests.get(f"{secure_fastapi_url}/openapi.json")
    assert resp.status_code == 200
    actual_openapi_json = resp.json()
    assert actual_openapi_json == expected_openapi_json


def test_generate_client(secure_fastapi_url: str) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        td = Path(temp_dir) / "gen"

        openapi_json_path = Path(__file__).parent / "expected_openapi.json"
        with openapi_json_path.open() as f:
            openapi_json = f.read()
            openapi_json.replace("http://localhost:9999", secure_fastapi_url)

        main_name = Client.generate_code(
            input_text=openapi_json,
            output_dir=td,
        )
        assert main_name == "main_gen"
        assert (td / "main_gen.py").exists()
        assert (td / "models_gen.py").exists()

        with (td / "main_gen.py").open() as f:
            actual_main_gen = f.readlines()[4:]
        actual_main_gen_txt = "\n".join(actual_main_gen)

        with (td / "models_gen.py").open() as f:
            actual_models_gen = f.readlines()[4:]

        expected_main_gen_path = Path(__file__).parent / "expected_main_gen.txt"
        with expected_main_gen_path.open() as f:
            expected_main_gen = f.readlines()[4:]
        expected_main_gen_txt = "\n".join(expected_main_gen)
        expected_main_gen_txt.replace("http://localhost:9999", secure_fastapi_url)

        expected_models_gen_path = Path(__file__).parent / "expected_models_gen.txt"
        with expected_models_gen_path.open() as f:
            expected_models_gen = f.readlines()[4:]

        assert actual_main_gen_txt == expected_main_gen_txt
        assert actual_models_gen == expected_models_gen


def test_import_and_call_generate_client(secure_fastapi_url: str) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        td = Path(temp_dir) / "gen"

        resp = requests.get(f"{secure_fastapi_url}/openapi.json")
        assert resp.status_code == 200
        openapi_json = resp.json()

        main_name = Client.generate_code(
            input_text=json.dumps(openapi_json),
            output_dir=td,
        )
        assert main_name == "main_gen"

        sys.path.insert(1, str(td))

        from main_gen import app as generated_client_app
        from main_gen import read_items_items__get

        assert generated_client_app.security != {}, generated_client_app.security

        # set global security params for all methods
        # generated_client_app.set_security_params(APIKeyHeader.Parameters(value="super secret key"))

        # or set security params for a specific method
        generated_client_app.set_security_params(
            APIKeyHeader.Parameters(value="super secret key"),
            "read_items_items__get",
        )

        # no security params added to the signature of the method
        client_resp = read_items_items__get(city="New York")
        assert client_resp == {"is_authenticated": True}
