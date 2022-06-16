"""Dremio Arrow Flight Client Main Module.

This client draws heavily from official [Python Arrow Flight Client Application Example]
(https://github.com/dremio-hub/arrow-flight-client-examples/tree/main/python).

The Client negotiates request methods provided by flight server to retrive data.

Arrow Flight Server Request Methods:
    Handshake: a simple request to determine whether the client is authorized
    ListFlights: return a list of available data streams
    GetSchema: return the schema for a data stream
    GetFlightInfo: return an “access plan” for a dataset of interest
    DoGet: send a data stream to a client
    DoPut: receive a data stream from a client
    DoAction: perform an implementation-specific action and return any results
    ListActions: return a list of available action types

More Details:
    Please see README.md file and [official docs](https://docs.dremio.com/software/drivers/arrow-flight/).
"""
import os
from datetime import date
from typing import Optional

import pandas as pd
from pyarrow import flight


class DremioClientAuthMiddlewareFactory(flight.ClientMiddlewareFactory):
    """A factory that creates DremioClientAuthMiddleware(s)."""

    def __init__(self):
        """Initialize Dremio Client Auth Middleware with empty credential values!"""
        self.call_credential = []

    def start_call(self, info):
        """Called at the start of an RPC.

        Creates client factory! This must be thread-safe and must not raise exceptions.

        Args:
            info: flight.CallInfo - Information about the call
        Returns: flight.ClientMiddleware - An instance of ClientMiddleware, or None if this call is not intercepted.
        """
        return DremioClientAuthMiddleware(self)

    def set_call_credential(self, call_credential):
        """Set credentials to extracted tokens!"""
        self.call_credential = call_credential


class DremioClientAuthMiddleware(flight.ClientMiddleware):
    """Client-side middleware for a call, instantiated per RPC.

    The middleware extracts the bearer token from the authorization header.

    Methods:
        - `call_completed(self, exception)` - A callback when the call finishes.
        - `received_headers(self, headers)` -  A callback when headers are received.
        - `sending_headers(self)` - A callback before headers are sent.
    """

    def __init__(self, factory: DremioClientAuthMiddlewareFactory):
        """Initialize middleware with DremioClientAuthMiddlewareFactory class object.

        Args:
            factory: DremioClientAuthMiddlewareFactory
                The factory to set call credentials if an authorization header
                with bearer token is returned by the Dremio server.
        """
        self.factory = factory

    def received_headers(self, headers):
        """Extract tokens from request headers!"""
        auth_header_key = 'authorization'
        if auth_header_key in headers.keys():
            authorization_header = headers.get(auth_header_key)
        else:
            raise Exception('Did not receive authorization header back from server.')
        self.factory.set_call_credential([b'authorization', authorization_header[0].encode("utf-8")])


class DremioArrowClient:
    """Create a Client capable of running queries on Dremio Flight Server."""

    def __init__(
        self,
        host: Optional[str] = os.environ.get('DREMIO_FLIGHT_SERVER_HOST', '127.0.0.1'),
        port: Optional[str] = os.environ.get('DREMIO_FLIGHT_SERVER_PORT', '32010'),
        username: Optional[str] = os.environ.get('DREMIO_FLIGHT_SERVER_USERNAME', '<username>'),
        password: Optional[str] = os.environ.get('DREMIO_FLIGHT_SERVER_PASSWORD', '<password>'),
    ):
        """Initialize Dremio Flight Client with authentication credentials!

        You can opt to manually provide credentials or let the factory extract them from environment variables.

        Args:
            host: string
                Dremio Flight Server IP address, defaults to DREMIO_FLIGHT_SERVER_HOST environment variable
            port: string
                Dremio Flight Server port, defaults to DREMIO_FLIGHT_SERVER_PORT environment variable
            username: string
                Dremio Flight Server username, defaults to DREMIO_FLIGHT_SERVER_USERNAME environment variable
            password: string
                Dremio Flight Server password, defaults to DREMIO_FLIGHT_SERVER_PASSWORD environment variable
        """
        # ensure the client was initialized with valid arguments
        if host is None:
            raise ValueError("A valid dremio server host IP/FQDN is required and cannot be None!")
        if port is None:
            raise ValueError("A valid dremio flight server port is required and cannot be None!")
        if username is None or username == "<username>":
            raise ValueError("A valid dremio server account username is required!")
        if password is None or password == "<password>":
            raise ValueError("A valid dremio server account password is required!")
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def create_flight_client(self, scheme: str = "grpc+tcp", connection_args: dict = {}):
        """Create a Dremio Flight Client!

        Args:
            scheme: string
                Dremio Flight Server connection scheme, defaults to grpc+tcp (unencrypted TCP connection)
            connection_args: dict
                Dremio Flight Server connection arguments, defaults to empty dictionary

        Action:
            Creates a dremio flight client capable of negotiating request methods!
        """
        self.client = flight.FlightClient(
            f"{scheme}://{self.host}:{self.port}", middleware=[DremioClientAuthMiddlewareFactory()], **connection_args
        )

    def authenticate(self, routing_tag: Optional[str] = None, routing_queue: Optional[str] = None):
        """Generate Dremio Flight Server Authentication Token!

        Args:
            routing_tag: str
            routing_queue: str

        These are `Dremio Enterprise Only Features` useful for workload management.
        The two workload management settings can be provided upon initial authneitcation.
        See [official docs](https://docs.dremio.com/advanced-administration/workload-management/) for more details.

        For dremio community edition, these settings are not useful. The default settings are sensible enough.
        Read https://docs.dremio.com/software/advanced-administration/job-queues/ for more details.

        Action:
            Sets client access token that can be used to query flight server!

        """
        headers = []
        if routing_tag is not None and routing_queue is not None:
            headers = [(b'routing-tag', str.encode(routing_tag)), (b'routing-queue', str.encode(routing_queue))]
        initial_options = flight.FlightCallOptions(headers=headers)

        try:
            # Authenticate user session.
            token = self.client.authenticate_basic_token(self.username, self.password, initial_options)
        except flight.FlightUnavailableError as err:
            raise ConnectionError(f'Server connection failed with Error: {err}')
        except flight.FlightUnauthenticatedError as err:
            raise ConnectionError(f"Failed to authenticate user account with Error: {err}")
        else:
            self.flight_options = flight.FlightCallOptions(headers=[token])

    def retrieve_ticket(self, sql: str):
        """Get Dremio Flight Info!

        Args:
            sql: str
                SQL query to run on Dremio Flight Server

        Action:
            Generates a FlightInfo message to retrieve the Ticket corresponding to query result set
        """
        try:
            self.ticket_info = self.client.get_flight_info(
                flight.FlightDescriptor.for_command(sql), self.flight_options
            )
        except Exception as error:
            raise SyntaxError(f"Failed to retrieve flight ticket info: {error}")

    def query(self, sql: str, ts_col: Optional[str] = None, ts_format: Optional[str] = None) -> pd.DataFrame:
        """Execute SQL command against Dremio Arrow Flight Server!

        Args:
            sql: str
                SQL query string to run on Dremio Engine
            ts_col: Optional[str]
                Date/DateTime column name. Useful for data conversions when fetching data for use in R environment.
            ts_format: Optional[str]
                Date/DateTime column output format. The ts_col data is converted to ts_format string. \
                    This can later be converted to R Timestamp data objects from the char type!
        Returns:
            data: pd.DataFrame
        """
        # create arrow flight client only if it's first time
        if not hasattr(self, 'client'):
            self.create_flight_client()
            # authenticate user session
            self.authenticate()
        # generate flight ticket
        self.retrieve_ticket(sql)
        try:
            # Retrieve the result set as a stream of Arrow record batches.
            reader = self.client.do_get(self.ticket_info.endpoints[0].ticket, self.flight_options)
        except Exception as error:
            raise Exception(f"Failed to read query results from Dremio: {error}")
        else:
            # convert arrow flight bytes stream to pandas dataframe
            df: pd.DataFrame = reader.read_pandas()
            # if ts_col and ts_format are defined, transform data types
            if ts_col is not None:
                if ts_col not in df.columns:
                    raise ValueError(
                        f'''
                    {ts_col} is not a valid column name in the dataframe!
                    ts_col parameter should be one of {list(df.columns)}
                    '''
                    )
                elif type(df[ts_col].iloc[0]) == pd.Timestamp or type(df[ts_col].iloc[0]) == date:
                    if ts_format is not None:
                        df[ts_col] = df[ts_col].apply(lambda ts: ts.strftime(ts_format))
                    else:
                        raise ValueError(
                            "ts_format parameter is required when using ts_col to convert DateTime column to string!"
                        )
                else:
                    raise TypeError(
                        f'''
                    {ts_col} column is of invalid type {type(df[ts_col].iloc[0])}.
                    Expected a valid pandas.Timestamp, date or datetime type!
                    '''
                    )
            return df


def dremio_query(
    sql: str,
    host: Optional[str] = None,
    port: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    ts_col: Optional[str] = None,
    ts_format: Optional[str] = None,
) -> pd.DataFrame:
    """Convenience method to run SQL query on Dremio Flight Server!

    Args:
        sql: str
            SQL query to run on Dremio Flight Server
        host: str
            Dremio Flight Server IP address, defaults to DREMIO_FLIGHT_SERVER_HOST environment variable
        port: int
            Dremio Flight Server port, defaults to DREMIO_FLIGHT_SERVER_PORT environment variable
        username: str
            Dremio Flight Server username, defaults to DREMIO_FLIGHT_SERVER_USERNAME environment variable
        password: str
            Dremio Flight Server password, defaults to DREMIO_FLIGHT_SERVER_PASSWORD environment variable
        ts_col: Optional[str]
            Date/DateTime column name. Useful for data conversions when fetching data for use in R environment.
        ts_format: Optional[str]
            Date/DateTime column output format. The ts_col data is converted to ts_format string. \
                This can later be converted to R Timestamp data objects from the char type!

    Return:
        pd.DataFrame: Pandas DataFrame containing SQL query results
    """
    # connection parameters from function
    params = {"host": host, "port": port, "username": username, "password": password}
    # exclude unset parameters
    args = {key: params.get(key) for key, value in params.items() if value is not None}
    flight_ = DremioArrowClient(**args)
    return flight_.query(sql, ts_col=ts_col, ts_format=ts_format)
