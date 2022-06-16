#!/usr/bin/env python
"""Tests for `dremioarrow` package."""

import os
from datetime import datetime

import pandas
import pytest
from pyarrow import flight

from dremioarrow import DremioArrowClient, dremio_query


@pytest.fixture
def flight_credentials():
    """Generate flight server connection parameters from environment variables."""
    return {
        'host': os.environ.get('DREMIO_FLIGHT_SERVER_HOST', 'localhost'),
        'port': os.environ.get('DREMIO_FLIGHT_SERVER_PORT', 32010),
        'username': os.environ.get('DREMIO_FLIGHT_SERVER_USERNAME', 'test_username'),
        'password': os.environ.get('DREMIO_FLIGHT_SERVER_PASSWORD', 'test_password123'),
    }


@pytest.fixture
def invalid_sql():
    """An invalid path to dremio dataset!"""
    return os.environ.get(
        'DREMIO_FLIGHT_TEST_INVALID_SQL',
        'SELECT * FROM "Dremio Sample Data"."samples.dremio.com"."Dremio University"."employees" LIMIT 5',
    )


@pytest.fixture
def valid_sql():
    """Valid SQL string pointing to dremio sample data."""
    return os.environ.get(
        'DREMIO_FLIGHT_TEST_VALID_SQL',
        'SELECT * FROM "Dremio Sample Data"."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 5',
    )


@pytest.fixture
def timestamped_data_sql():
    """SQL query string pointing to NYC taxi trips data which has a datetime column `pickup_datetime`."""
    return os.environ.get(
        'DREMIO_FLIGHT_TEST_TS_DATA_SQL',
        'SELECT * FROM "Dremio Sample Data"."samples.dremio.com"."NYC-taxi-trips"."1_0_0.parquet" LIMIT 5',
    )


@pytest.fixture
def unknown_ts_col():
    """A column name not in the subject dataset."""
    return os.environ.get('UNKNOWN_TEST_TIMESTAMP_COL', 'NOT_TIMESTAMP')


@pytest.fixture
def invalid_ts_col():
    """A column in the subject dataset but of invalid data type (not date/datetime)."""
    return os.environ.get('INVALID_TEST_TIMESTAMP_COL', 'phone_number')


@pytest.fixture
def valid_ts_datetime_col():
    """A valid datetime column name."""
    return os.environ.get('VALID_TEST_TIMESTAMP_COL', 'pickup_datetime')


@pytest.fixture
def valid_ts_date_col():
    """A valid date column name."""
    return os.environ.get('VALID_TEST_DATE_COL', 'hire_date')


@pytest.fixture
def invalid_ts_format():
    """Invalid date/datetime conversion format."""
    return os.environ.get('INVALID_TEST_TIMESTAMP_FORMAT', '%x-%y-%z')


@pytest.fixture
def valid_ts_format():
    """A valid date/datetime conversion to equivalent datetime string."""
    return os.environ.get('VALID_TEST_TIMESTAMP_FORMAT', '%Y-%m-%d %H:%M:%S')


@pytest.fixture
def valid_date_format():
    """A valid date/datetime conversion to equivalent date string."""
    return os.environ.get('VALID_TEST_DATE_FORMAT', '%Y-%m-%d')


def test_init_host_empty(flight_credentials: dict):
    """Test client instatiation fails when `host` arg is not provided."""
    flight_credentials['host'] = None
    with pytest.raises(ValueError, match=r".*IP/FQDN is required.*"):
        DremioArrowClient(**flight_credentials)


def test_init_port_empty(flight_credentials: dict):
    """Test client instatiation fails when `port` arg is not provided."""
    flight_credentials['port'] = None
    with pytest.raises(ValueError, match=r".*port is required.*"):
        DremioArrowClient(**flight_credentials)


def test_init_username_empty(flight_credentials: dict):
    """Test client instatiation fails when `username` arg is set to None/Empty."""
    flight_credentials['username'] = None
    with pytest.raises(ValueError, match=r".*username is required.*"):
        DremioArrowClient(**flight_credentials)


def test_init_username_default(flight_credentials: dict):
    """Test client instatiation fails when `username` arg is left unset."""
    flight_credentials['username'] = '<username>'
    with pytest.raises(ValueError, match=r".*username is required.*"):
        DremioArrowClient(**flight_credentials)


def test_init_password_empty(flight_credentials: dict):
    """Test client instatiation fails when `port` arg is set to None/Empty."""
    flight_credentials['password'] = None
    with pytest.raises(ValueError, match=r".*password is required.*"):
        DremioArrowClient(**flight_credentials)


def test_init_password_default(flight_credentials: dict):
    """Test client instatiation fails when `username` arg is left unset."""
    flight_credentials['password'] = '<password>'
    with pytest.raises(ValueError, match=r".*password is required.*"):
        DremioArrowClient(**flight_credentials)


def test_create_client(flight_credentials: dict):
    """Test we can create flight server client with invalid credentials!

    Invalid credentials in this matters means host and port refer to non-existent flight server!
    We are able to create a client object with invalid parameters because \
    no connection to flight server is established at this stage.
    """
    # change flight port to non-standard
    flight_credentials['port'] = 10010
    flight_ = DremioArrowClient(**flight_credentials)
    flight_.create_flight_client()
    assert type(flight_.client) == flight.FlightClient, 'Flight client creation could not be handled correctly.'


def test_flight_server_connection(flight_credentials: dict):
    """The client negotiates handshake connection when we invoke basic auth method.

    Test connection fails when using invalid host/port.
    """
    flight_credentials['port'] = 10010
    flight_ = DremioArrowClient(**flight_credentials)
    flight_.create_flight_client()
    with pytest.raises(ConnectionError, match=r'.*connection failed.*'):
        flight_.authenticate()


def test_flight_invalid_account(flight_credentials: dict):
    """When invalid username/password is used, a different exception is raised. Let's test it!"""
    flight_credentials['username'] = 'invalid_username'
    flight_ = DremioArrowClient(**flight_credentials)
    flight_.create_flight_client()
    with pytest.raises(ConnectionError, match=r'.*Failed to authenticate.*'):
        flight_.authenticate()


def test_retrive_invalid_sql_ticket(flight_credentials: dict, invalid_sql: str):
    """Test when an invalid SQL command is used to retrieve ticket!

    The SQL query string could be invalid because it refers to unreachable dremio dataset \
    or it doesn't satisfy SQL syntax!
    """
    flight_ = DremioArrowClient(**flight_credentials)
    flight_.create_flight_client()
    flight_.authenticate()
    with pytest.raises(SyntaxError, match=r'.*Failed to retrieve flight.*'):
        flight_.retrieve_ticket(invalid_sql)


def test_retrive_sql_ticket(flight_credentials: dict, valid_sql: str):
    """Test when an invalid SQL command is used to retrieve ticket!

    The SQL query string could be invalid because it refers to unreachable dremio dataset \
    or it doesn't satisfy SQL syntax!
    """
    flight_ = DremioArrowClient(**flight_credentials)
    flight_.create_flight_client()
    flight_.authenticate()
    flight_.retrieve_ticket(valid_sql)
    assert (
        type(flight_.ticket_info) == flight.FlightInfo
    ), f'Received invalid flight ticket of type {type(flight_.ticket_info)}'


def test_successful_query(flight_credentials: dict, valid_sql: str):
    """Last test in `DremioArrowClient` class.

    While the `query` method raises an exception when things go wrong during data fetch, most of time \
    the query will run successfully. We have no way to test the data fetch exception as it is \
    being raised by several factors such as timeout, client disconnection, network latency etc.
    """
    flight_ = DremioArrowClient(**flight_credentials)
    data = flight_.query(valid_sql)
    assert type(data) == pandas.DataFrame, f'Received invalid data type: {type(data)}'
    assert data.shape[0] == 5, f'Data row count not 5 as expected: {data.shape[0]}'


def test_use_of_env_vars(valid_sql: str):
    """This test seeks to confirm the client can extract connection credentials from env vars!"""
    flight_ = DremioArrowClient()
    data = flight_.query(valid_sql)
    assert type(data) == pandas.DataFrame, f'Received invalid data type: {type(data)}'
    assert data.shape[0] == 5, f'Data row count not 5 as expected: {data.shape[0]}'


def test_shorthand_query(flight_credentials: dict, valid_sql: str):
    """Test for shorthand `dremio_query` method."""
    data = dremio_query(sql=valid_sql, **flight_credentials)
    assert type(data) == pandas.DataFrame, f'Received invalid data type: {type(data)}'
    assert data.shape[0] == 5, f'Data rows count not 5 as expected: {data.shape[0]}'


def test_shorthand_env_vars_query(valid_sql: str):
    """Test for shorthand `dremio_query` method with credential extraction from env vars."""
    data = dremio_query(sql=valid_sql)
    assert type(data) == pandas.DataFrame, f'Received invalid data type: {type(data)}'
    assert data.shape[0] == 5, f'Data rows count not 5 as expected: {data.shape[0]}'


def test_unknown_ts_col_provided(valid_sql: str, unknown_ts_col: str):
    """Test for when a column name not in data is provided for ts_col variable."""
    with pytest.raises(ValueError, match=".*is not a valid.*"):
        dremio_query(valid_sql, ts_col=unknown_ts_col)


def test_invalid_ts_col_provided(valid_sql: str, invalid_ts_col: str, valid_date_format: str):
    """Test for when ts_col has invalid data type."""
    with pytest.raises(TypeError, match=".*column is of invalid type.*"):
        dremio_query(valid_sql, ts_col=invalid_ts_col, ts_format=valid_date_format)


def test_no_ts_format_provided(valid_sql: str, valid_ts_date_col: str):
    """Test when date/datetime output column format is not provided."""
    with pytest.raises(ValueError, match=".*ts_format parameter is required.*"):
        dremio_query(valid_sql, ts_col=valid_ts_date_col)


def test_date_col_conversion(valid_sql: str, valid_ts_date_col: str, valid_date_format: str):
    """A test for date column conversion to string!

    The column here should be of date type!
    """
    data = dremio_query(sql=valid_sql, ts_col=valid_ts_date_col, ts_format=valid_date_format)
    assert type(data[valid_ts_date_col].iloc[0]) == str, "Date data type conversion to string failed"
    assert (
        type(datetime.strptime(data[valid_ts_date_col].iloc[0], valid_date_format)) == datetime
    ), "Data conversion back to datetime failed. ts_format varible is likely to be invalid!"


def test_datetime_col_conversion(timestamped_data_sql: str, valid_ts_datetime_col: str, valid_ts_format: str):
    """A test for datetime column conversion to string!

    The column here should be of datetime type!
    """
    flight_ = DremioArrowClient()
    data = flight_.query(timestamped_data_sql, ts_col=valid_ts_datetime_col, ts_format=valid_ts_format)
    assert type(data[valid_ts_datetime_col].iloc[0]) == str, "Date data type conversion to string failed"
    assert (
        type(datetime.strptime(data[valid_ts_datetime_col].iloc[0], valid_ts_format)) == datetime
    ), "Data conversion back to datetime failed. ts_format varible is likely to be invalid!"
