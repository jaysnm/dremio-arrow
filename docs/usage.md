# API Overview

`dremio-arrow` package is a single module {++Python API++} that exposes two methods; a class `DremioArrowClient` and a function `dremio_query`. `DremioArrowClient` class implements flight middlewares and is the gateway to dremio flight server. `dremio_query` function is a shorthand to `DremioArrowClient` and a very fast way to invoke the client especially when re-use of client parameters is not useful!
