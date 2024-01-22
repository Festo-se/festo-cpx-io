# festo-cpx-io
`festo-cpx-io` is a python package which bundles python modules to facilitate operation of Festo CPX systems.

Documentation can be found [here](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/) and in the [examples](./examples) directory.

## Installation
### Release

The latest release is available in a non-public PyPi repo. 
The URL can be added to your pip.ini in order to make it known to your pip instance.

1. Find your `pip.ini`:
```
pip config debug
```

1. Add the following line:
```
extra-index-url = https://adeartifactory1.de.festo.net/artifactory/api/pypi/electricdrives-python-dev-local/simple
```

1. Install via pip:
```
pip install festo-cpx-io
```

### From git repo
You can also install directly from the git repo.

1. Clone the repository

```
git clone <git-url> <destination>
```

2. Change into the clone directory
```
cd <destination>
```

3. Install via pip
```
pip install .
```

## Usage
### [CLI](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/features/cli.html) - [`cli`](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/cpx_io.cli.html#module-cpx_io.cli.cli)
`festo-cpx-io` is the main entry point to the CLI.
It supports various subcommands which execute some basic functions.

For more information use the help flag  (`festo-cpx-io -h`).

#### Subcommands
- [`cpx-e`](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/features/cli.html#cpx-e) is a subcommand to execute commands on CPX-E devices