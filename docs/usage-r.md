--8<-- "docs/usage.md"

!!! abstract "Using the client in R environment"
    While the client is developed in `python`, it can be used to interact with dremio flight engine; thanks to [reticulate](https://github.com/rstudio/reticulate).

    From `{reticulate}`s official documentation, the reticulate package provides a comprehensive set of tools for interoperability between Python and R. The package includes facilities for:


    - [x] Calling Python from R in a variety of ways including R Markdown, sourcing Python scripts, importing Python modules, and using Python interactively within an R session.

    - [x] Translation between R and Python objects (for example, between R and Pandas data frames, or between R matrices and NumPy arrays).

    - [x] Flexible binding to different versions of Python including virtual environments and Conda environments.

    Given that the client outputs a `pandas.DataFrame` data, `reticulate` can conveniently convert the data to native `R data.frame` outside the box (no hacks whatsoever).

???+ danger "Handling python datetime objects"
    At the moment, conversion between `python datetime` and `R timestamp` is not well covered in `reticulate`. The client provides `ts_col` and `ts_fmt` extra options during query operation to enable conversion of `python datetime` to string counterpart.

## Working Environment

This example assumes you have `python3`, a virtual environment created and the client installed in the virtual environment. If this is not the case, See [Python Downloads](https://www.python.org/downloads/) for python installation and [Client Installation](installation.md) for virtual environment creation and client installation.

### Install reticulate

`reticulate` is a `R` package and thus should be installed in `R` environment. Below commands can be executed in a `Rmarkdown`, `R script` or `R interpreter/terminal`.


```r

install.packages("reticulate", repos="https://cran.r-project.org", deps=TRUE) # (1)

library(reticulate) # (2)

use_virtualenv("/path/to/vertual/environment") # (3)
```

1. Install required `R` package {reticulate} alongside its dependencies.

2. Load `reticulate` package into working environment

3. Set path to `python interpreter`. The `/path/to/vertual/environment` can be absolute or relative and should not include `bin/python` part. The path points to directory containing `bin/python`.

Now that we have the environment set, it is time to rea some data from dremio engine!

### using `class DremioArrowClient`

```r
dremio_client <- import("dremioarrow") # (1)

client <- dremio_client$DremioArrowClient(
    host='dremio-server-host-ip/fqdn',
    port='dremio-flight-server-port',
    username='dremio-account-username',
    password='dremio-account-password'
) # (2)

sql <- 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 10' # (3)

data <- dremio_client$client.query(sql) # (4)

data # (5)
```


1. :material-import: First step is to import dremio client package into `R`. This makes the client available in our working environment.

2. :material-star-four-points: Initialize the client with dremio flight server connection credentials. These are the credentials you use to access your dremio engine.

3. :material-flag-outline: Here we define SQL query string with data fetch instructions. The table name path must exist, whether as phisical or virtual dataset.

4. :material-lightning-bolt: We now execute our SQL query against dremio flight server.

5. :material-table-large: This step is not necessary but a way to preview the dataset we just fetched. Form here you have your data as a `pandas.DataFrame` and thus can proceed with analysis, processing and reporting bit.


!!! hint "'`Cleaner`' Credentials Provision"
    Dremio flight server connection parameters can be supplied using environment variables. In that case, it is not necessary to supply the credentials when initializing the client.

    === "Define Environment Variables"

        The environment variables can be defined by either exporting the variables in current terminal session (We can use them only if running R from the terminal), persist them on `~/.Renviron`, `~/.Rprofile`, `~/.profile` (ubuntu) or `~/.zshrc` (Mac).

        ##### Write the variables into `/.Renviron`
        {==
        .Renviron is a user-controllable file that can be used to create environment variables. This is especially useful to avoid including credentials like API keys inside R scripts. This file is written in a key-value format, so environment variables are created in the format:
        ==}

        ```r
        DREMIO_FLIGHT_SERVER_HOST='dremio-server-host-ip/fqdn'
        DREMIO_FLIGHT_SERVER_PORT='dremio-flight-server-port'
        DREMIO_FLIGHT_SERVER_USERNAME='dremio-account-username'
        DREMIO_FLIGHT_SERVER_PASSWORD='dremio-account-password'
        ```

        ##### Write the variables into `/.Rprofile`
        {==
        R will source only one .Rprofile file. So if you have both a project-specific .Rprofile file and a user .Rprofile file that you want to use, you explicitly source the user-level .Rprofile at the top of your project-level .Rprofile with source("~/.Rprofile").

        .Rprofile files are sourced as regular R code, so setting environment variables must be done inside a Sys.setenv(key = "value") call.
        ==}

        ```r
        export DREMIO_FLIGHT_SERVER_HOST='dremio-server-host-ip/fqdn'
        export DREMIO_FLIGHT_SERVER_PORT='dremio-flight-server-port'
        export DREMIO_FLIGHT_SERVER_USERNAME='dremio-account-username'
        export DREMIO_FLIGHT_SERVER_PASSWORD='dremio-account-password'
        ```

        ##### Define the virables on current terminal session
        ==Execute below commands replacing placeholder texts with actual credential value.==

        ```bash
        export DREMIO_FLIGHT_SERVER_HOST='dremio-server-host-ip/fqdn'
        export DREMIO_FLIGHT_SERVER_PORT='dremio-flight-server-port'
        export DREMIO_FLIGHT_SERVER_USERNAME='dremio-account-username'
        export DREMIO_FLIGHT_SERVER_PASSWORD='dremio-account-password'
        ```

        ##### Write the variables into `~/.profile` (ubuntu) or `~/.zshrc` (Mac).

        ```bash
        vi ~/.zshrc # (1)
        ```

        1. :material-content-copy: Copy the enviroment variables into the file replacing placeholder texts with actual credential value.
        ```bash
        export DREMIO_FLIGHT_SERVER_HOST='dremio-server-host-ip/fqdn'
        export DREMIO_FLIGHT_SERVER_PORT='dremio-flight-server-port'
        export DREMIO_FLIGHT_SERVER_USERNAME='dremio-account-username'
        export DREMIO_FLIGHT_SERVER_PASSWORD='dremio-account-password'
        ```

        Once done, exit all running applications and logout or restart the computer for the changes to take effect.

    === "Refactor Client Access Code"

        ```r
        # import client package
        dremio_client <- import("dremioarrow")

        # instatiate the client
        client <- dremio_client$DremioArrowClient()

        # define SQL query string
        sql <- 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 10'

        # fetch data
        data <- dremio_client$client.query(sql)

        # preview data
        data
        ```

        With the environment variables correctly set, we nolonger need to set connection credentials. The client is smart enough to extract the variables from the environmet!



If we had a second query to execute, we would just have reused the client with a different SQL query string.

```r
# define new SQl query string
sql <- 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 100'

# fetch data
data <- dremio_client$client.query(sql) # 1

# preview data
data
```
!!! note "We didn't create a new client"

    In this repeat operation, we did not create a new client object, instead we reused the one we earlier created above!



### Using  `function dremio_query`

This function is very useful when we are interested in executing a single query and are not sure when a second query might be executed. The method takes authentication credentials and returns data. In essence, this is to mean session bearer token cannot be re-used because we are not using the client directly!

```r
dremio_client <- import("dremioarrow") # (1)

# SQL query with data fetch instructions
sql <- 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 10' # (2)

# execute the query
data <- dremio_client$dremio_query(
    sql=sql,
    host='dremio-server-host-ip/fqdn',
    port='dremio-flight-server-port',
    username='dremio-account-username',
    password='dremio-account-password'
) # (3)

# preview data
data
```

1. :material-import: First step is to import the client package.

2. :material-flag-outline: Define SQL query string with data fetch instructions.

3. :material-lightning-bolt: Execute the SQL query string against dremio flight server.

With credentials defined as environment variables, the above is refactired to:

```r
# import client package
dremio_client <- import("dremioarrow")

# SQL query with data fetch instructions
sql <- 'SELECT * FROM Samples."samples.dremio.com"."Dremio University"."employees.parquet" LIMIT 10'

# execute the query
data <- dremio_client$dremio_query()

# preview data
data
```
