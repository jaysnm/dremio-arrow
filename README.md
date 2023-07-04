# Dremio SQL Lakehouse Arrow Flight Client

![Python3.10](https://img.shields.io/badge/python-3.10-brightgreen?style=flat&logo=python)
![Python3.11](https://img.shields.io/badge/python-3.11-blue?style=flat&logo=python)

Arrow Flight is a high-speed, distributed protocol designed to handle big data, providing increase in throughput between client applications and Dremio.
This Dremio Arrow Flight Client is based on [python official examples](https://github.com/dremio-hub/arrow-flight-client-examples/tree/main/python).

> Disclaimer: This project is not affliated to [dremio](https://dremio.com) in any way. It is a tool that I developed while at CIFOR-ICRAF and now we have decided to open source it for wider community use. While I may not have enough time to actively maintain it, the tool is stable enough to sustain future use cases. Besides, community contribution is warmly welcome in form of PRs and forks.


* Documentation: <https://jaysnm.github.io/dremio-arrow/>
* GitHub: <https://github.com/jaysnm/dremio-arrow>
* PyPI: <https://pypi.org/project/dremio-arrow/>
* Free software: Apache-2.0


## Flight Basics

The Arrow Flight libraries provide a development framework for implementing a service that can send and receive data streams. A Flight server supports several basic kinds of requests:

- **Handshake**: a simple request to determine whether the client is authorized and, in some cases, to establish an implementation-defined session token to use for future requests
- **ListFlights**: return a list of available data streams
- **GetSchema**: return the schema for a data stream
- **GetFlightInfo**: return an “access plan” for a dataset of interest, possibly requiring consuming multiple data streams. This request can accept custom serialized commands containing, for example, your specific application parameters.
- **DoGet**: send a data stream to a client
- **DoPut**: receive a data stream from a client
- **DoAction**: perform an implementation-specific action and return any results, i.e. a generalized function call
- **ListActions**: return a list of available action types

> More details can be found [here](https://arrow.apache.org/blog/2019/10/13/introducing-arrow-flight/)

![Illustration](https://arrow.apache.org/img/20191014_flight_simple.png)


## Installation

Please see installation notes [here](https://jaysnm.github.io/dremio-arrow/installation/)
