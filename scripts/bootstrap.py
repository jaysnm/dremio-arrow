"""Dremio test cluster bootstraping methods!"""
import json
import os
from urllib.parse import quote

import requests  # type: ignore


def create_first_user_account(base_url: str, username: str, password: str):
    """Creates initial dremio admin user account.

    See https://community.dremio.com/t/create-an-administrator-user-from-the-command-line/925/5
    """
    r = requests.put(
        f"{base_url}/apiv2/bootstrap/firstuser",
        headers={'Authorization': '_dremionull', 'Content-Type': 'application/json'},
        data=json.dumps(
            {
                "userName": username,
                "firstName": "Fist-Name",
                "lastName": "Last-Name",
                "email": "admin@example.com",
                "password": password,
            }
        ),
    )
    if r.status_code != 200:
        print(r.text)
        r.raise_for_status()
    return f"{username} account was created successfully!"


def auth_token(base_url: str, username: str, password: str):
    """Generate an authentication token!"""
    r = requests.post(f"{base_url}/apiv2/login", json={"userName": username, "password": password})
    if r.status_code != 200:
        print(r.text)
        r.raise_for_status()
    return r.json()['token']


def create_sample_data_source(base_url: str, token: str):
    """Adds dremio S3 bucket sample data source."""
    source = {
        'entityType': 'source',
        'name': 'Dremio Sample Data',
        'description': 'Dremio Sample Data',
        'type': 'S3',
        'config': {'externalBucketList': ['samples.dremio.com'], 'secure': False, 'credentialType': 'NONE'},
    }
    r = requests.post(f"{base_url}/api/v3/catalog", headers={"Authorization": f"_dremio{token}"}, json=source)
    if r.status_code != 200:
        print(r.text)
        r.raise_for_status()
    return "Sample data source was created successfully!"


def promote_file_to_dataset(base_url: str, token: str, file_path: list[str], file_id: str):
    """This API promotes a file or folder in a file-based source to a physical dataset (PDS).

    Dataset file path and ID must be known beforehand.
    There is a programmatic way of doing this, but for the moment we are going \
    to hard-code!

    Read about file promotion here https://docs.dremio.com/software/rest-api/catalog/post-catalog-id/
    """
    encoded_file_id = quote(file_id, safe="")
    dataset_info = {
        'entityType': 'dataset',
        'id': encoded_file_id,
        'path': file_path,
        'type': 'PHYSICAL_DATASET',
        'format': {'type': 'Parquet'},
    }
    r = requests.post(
        f"{base_url}/api/v3/catalog/{encoded_file_id}", headers={"Authorization": f"_dremio{token}"}, json=dataset_info
    )
    if r.status_code != 200:
        print(r.text)
        r.raise_for_status()
    return f"Dataset promoted to VDS with ID {r.json()['id']}"


if __name__ == '__main__':
    host = os.environ.get('DREMIO_FLIGHT_SERVER_HOST', 'localhost')
    ui_port = os.environ.get('DREMIO_FLIGHT_SERVER_UI_PORT', 9047)
    username = os.environ.get('DREMIO_FLIGHT_SERVER_USERNAME', 'test_username')
    password = os.environ.get('DREMIO_FLIGHT_SERVER_PASSWORD', 'test_password123')

    base_url = f"http://{host}:{ui_port}"
    # create user account
    print(create_first_user_account(base_url=base_url, username=username, password=password))
    # generate auth token
    token = auth_token(base_url=base_url, username=username, password=password)
    print(create_sample_data_source(base_url=base_url, token=token))
    # please see https://docs.dremio.com/software/rest-api/catalog/post-catalog-id/
    # There is a clean/programmatic way of doing this!
    employees_file_path = ['Dremio Sample Data', 'samples.dremio.com', 'Dremio University', 'employees.parquet']
    employees_file_id = 'dremio:/Dremio Sample Data/samples.dremio.com/Dremio University/employees.parquet'
    print(
        promote_file_to_dataset(
            base_url=base_url, token=token, file_path=employees_file_path, file_id=employees_file_id
        )
    )
    nyc_file_path = ['Dremio Sample Data', 'samples.dremio.com', 'NYC-taxi-trips', '1_0_0.parquet']
    nyc_file_id = 'dremio:/Dremio Sample Data/samples.dremio.com/NYC-taxi-trips/1_0_0.parquet'
    print(promote_file_to_dataset(base_url=base_url, token=token, file_path=nyc_file_path, file_id=nyc_file_id))
