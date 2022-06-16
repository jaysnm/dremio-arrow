--8<-- "docs/usage.md"


## Using `class DremioArrowClient`

The class method is very useful for big applications where re-use of client parameters such as authentication token and workload management queues is important.

```bash
from dremioarrow import DremioArrowClient # (1)

client = DremioArrowClient(
    host='dremio-server-host-ip/fqdn',
    port='dremio-flight-server-port',
    username='dremio-account-username',
    password='dremio-account-password'
) # (2)

sql = 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 10' # (3)

data = client.query(sql) # (4)

# preview result data from dremio flight server
data # (5)
```

1. :material-import: First step is to import `DremioArrowClient`. This makes the client available on our working environment.

2. :material-star-four-points: Initialize the client with dremio flight server connection credentials. These are the credentials you use to access your dremio engine.

3. :material-flag-outline: Here you define SQL query string with data fetch instructions. The table name path must exist, whether as phisical or virtual dataset.

4. :material-lightning-bolt: We now execute our SQL query against dremio flight server.

5. :material-table-large: This step is not necessary but a way to preview the dataset we just fetched. Form here you have your data as a `pandas.DataFrame` and thus can proceed with analysis, processing and reporting bit.

!!! hint "'`Cleaner`' Credentials Provision"
    Dremio flight server connection parameters can be supplied using environment variables. In that case, it is not necessary to supply the credentials when initializing the client.

    === "Define Environment Variables"

        Either export the variables in current terminal session or persist them on `~/.profile` (ubuntu) or `~/.zshrc` (Mac). To define the virables on current terminal session, execute below commands replacing placeholder texts with actual credential value.

        ```bash
        export DREMIO_FLIGHT_SERVER_HOST='dremio-server-host-ip/fqdn'
        export DREMIO_FLIGHT_SERVER_PORT='dremio-flight-server-port'
        export DREMIO_FLIGHT_SERVER_USERNAME='dremio-account-username'
        export DREMIO_FLIGHT_SERVER_PASSWORD='dremio-account-password'
        ```

        To persist the environment variables, write them into `~/.profile` (ubuntu) or `~/.zshrc` (Mac).

        ```bash
        vi ~/.zshrc # (1)

        source ~/.zshrc # (2)

        ```

        1. :material-content-copy: Copy the enviroment variables into the file replacing placeholder texts with actual credential value.
        ```bash
        export DREMIO_FLIGHT_SERVER_HOST='dremio-server-host-ip/fqdn'
        export DREMIO_FLIGHT_SERVER_PORT='dremio-flight-server-port'
        export DREMIO_FLIGHT_SERVER_USERNAME='dremio-account-username'
        export DREMIO_FLIGHT_SERVER_PASSWORD='dremio-account-password'
        ```

        2. :octicons-sync-16: Refresh active terminal session variables. This step may deactivate the virtual environment variable depending on your OS platform. If this happens, re-activate the virtual environment. By persisting the variables, you are assured your project will work even after a restart of the machine. In addition, chances of commiting secret tokens into VCS spontaneously reduce!

    === "Refactor Client Access Code"

        ```python
        from dremioarrow import DremioArrowClient
        # note that we are nolonger setting connection parameters
        client = DremioArrowClient()

        sql = 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 10'

        data = client.query(sql)

        data
        ```

        With the environment variables correctly set, we nolonger need to set connection credentials. The client is smart enough to extract the variables from the environmet!



If we had a second query to execute, we would just have reused the client with a different SQL query string.

```python
# new SQL query with data fetch instructions
sql = 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 100'

# execute the SQL query against dremio flight server
data = client.query(sql) # (1)

# preview result data from dremio flight server
data
```

!!! note "We didn't create a new client"

    In this repeat operation, we did not create a new client object, instead we reused the one we earlier created above!

???+ "Getting Help"
    For more information on client usage, see [API Reference] or run below chunk in your python interpreter.

    ```
    from dremioarrow import DremioArrowClient

    help(DremioArrowClient)
    ```


## Using  `function dremio_query`

This function is very useful when we are interested in executing a single query and are not sure when a second query might be executed. The method takes authentication credentials and returns data. In essence, this is to mean session bearer token cannot be re-used because we are not using the client directly!

```python
from dremioarrow import dremio_query # (1)

# SQL query with data fetch instructions
sql = 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 10' # (2)

# execute the query
data = dremio_query(
    sql=sql,
    host='dremio-server-host-ip/fqdn',
    port='dremio-flight-server-port',
    username='dremio-account-username',
    password='dremio-account-password'
) # (3)

# preview data
data
```

1. :material-import: First step is to import `dremio_query` function.

2. :material-flag-outline: Define SQL query string with data fetch instructions.

3. :material-lightning-bolt: Execute the SQL query string against dremio flight server.

With credentials defined as environment variables, the above is refactired to:

```python
# import dremio_query method
from dremioarrow import dremio_query

# SQL query with data fetch instructions
sql = 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 10'

# execute the query
data = dremio_query(sql=sql)

# preview data
data
```

???+ "Getting Help"
    For more information on the function usage, see [API Reference] or run below chunk in your python interpreter.

    ```python
    from dremioarrow import dremio_query

    help(dremio_query)
    ```
