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

### [CPX-SYSTEM](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/features/cpx_io.html) - [`cpx_system`](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/cpx_io.cpx_system.html#)
#### [CPX-E](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/cpx_io.cpx_system.cpx_e.html)
Import the library with `from cpx_io.cpx_system.cpx_e.cpx_e import CpxE`. 

Setup your system with a python context manager and print the attached modules. You can use the typecode of your system to setup all the modules, hand over a list of pre-instantiated modules in the CpxE constructor or instantiate an empty CpxE and add the modules later. In every case, the order of the modules must be consistent with the actually used hardware setup.

```
with CpxE(<typecode_string>, ip_address=<your_ip_address>) as myCPX:
    print(myCPX.modules)
```

For more information on how to setup the system and how to adress the modules read the [docs](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/features/cpx_io.html#cpx-e) see the [examples](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/examples.html#cpx-e).


#### [CPX-AP](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/cpx_io.cpx_system.cpx_ap.html)
Import the library with `from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp`.

The AP system will do all of the system setup for you. That means that you don't have to provide any more information than the ip-address. The modules are built during the runtime by a description file that will be collected directly from the modules. Since all the functionality of each module is created on your system, the documentation is also generated and stored on your device (e.g. your PC). You need to get the path by printing the system information with `CpxAp.print_system_information()`. Or just `print(CpxAp.docu_path)`

```
with CpxAp(<typecode_string>, ip_address=<your_ip_address>) as myCPX:
    myCPX.print_system_information()
```

For more information on how to setup the system and how to adress the modules, read the [docs](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/features/cpx_io.html#cpx-ap) see the [examples](https://festo.gitlab-pages.festo.company/electric-automation/remote-io/festo-cpx-io/examples.html#cpx-ap).

