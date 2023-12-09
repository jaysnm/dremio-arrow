# Dremio SQL Lakehouse Arrow Flight Client Installation Guide

Arrow Flight is a high-speed, distributed protocol designed to handle big data, providing increase in throughput between client applications and Dremio.

This Dremio Arrow Flight Client is based on [python Official examples](https://github.com/dremio-hub/arrow-flight-client-examples/tree/main/python).

> Disclaimer: This project is not affliated to [dremio](https://dremio.com) in any way. It is a tool that I developed while at CIFOR-ICRAF and now we have decided to open source it for wider community use. While I may not have enough time to actively maintain it, the tool is stable enough to sustain future use cases. Besides, community contribution is warmly welcome in form of PRs and forks.

`dremio-arrow` package is available on [PyPI](https://pypi.org/project/dremio-arrow/) and can be installed with `pip`, `poetry`, `conda` or from [GitHub](https://github.com/jaysnm/dremio-arrow)

[![python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)](https://pypi.org/project/dremio-arrow/)


## Installation Requirements

- A package manger :-> [Pip](https://pip.pypa.io), [Poetry](https://python-poetry.org/docs/master/#installation) or [Conda](https://conda.io/docs/user-guide/install/index.html)
- [Python](http://docs.python-guide.org/en/latest/starting/installation/) (any of 3.9 through 3.11)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) if installing from source

???+ hint "Experimental Git Branches"

    :octicons-git-branch-16: The default ==main branch== contains stable release. Please install the latest release on pypi or use code from the main branch when in doubt. For experimentations, feel free to use any branch accessible to you :smile:


## Installing the package

!!! danger "Supported Python Versions"

    This package is thorougly tested against `python3.7`, `python3.8`, `python3.9` or `python3.10`. Other python3 versions might work but just note they have not been tested.

!!! info "Virtual Environment or Install on OS Filesystem?"

    Personally I discourage installation on the python base libraries path. I consider it an `evil act` because it may cause unprecedented issues if the package is compromised (we are always onlook for security vulnerabilities but it is always good to be prepared for unexpected eventualities).
    In my opinion therefore, it is better to install the package (not just this but also all other packages that you use) in a virtual environment.
    Using a virtual environment also allows one to experiment with different python and/or package versions. If you are curious about this, please look at [pyenv](https://github.com/pyenv/pyenv).

### Installing from PyPI (recomended)

Create a virtual environment and activate it.

- Using [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)

```bash
virtualenv -p python3 venv
source venv/bin/activate
```

- Using python3's [venv](https://docs.python.org/3/library/venv.html)

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the package using pip

```bash
pip install dremio-arrow
```

Install the package using poetry

```bash
poetry add dremio-arrow
```

Install the package using conda

    - Create a conda environment
    ```bash
    conda create -n myenv python=3.10
    source activate myenv
    ```

    - Install the package
    ```bash
    conda install dremio-arrow
    ```

### Installing from github source

Clone the repository

```bash
git clone https://github.com/jaysnm/dremio-arrow.git
```

Change to the source directory
```bash
cd dremio-arrow
```

Install the package using pip
```bash
pip install -e .
```
Install the package using poetry
```bash
poetry install
```

!!! note "Not using Linux or MacOS?"

    :fontawesome-solid-circle-info: This example assumes you are on {++MacOSX or Linux++}. If using {--Windows--} or {--any other OS--}, kindly look for their respective documentations on how to use a virtual environment in the command prompt.

???+ hint "Development Dependencies"
    Besides `pyarrow` and `pandas`, the package ships with optional dependencies used during development. Installation of these dependencies is only required if you intend to contribute some changes into the package. Please see [Contributing Guidlines](contributing.md).
