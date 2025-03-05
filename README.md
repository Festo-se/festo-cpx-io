# festo-cpx-io
`festo-cpx-io` is a python package which bundles python modules to facilitate operation of Festo CPX systems.

Documentation can be found [here](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/) and in the [examples](./examples) directory.

## Installation
### Release
The latest release is available in the public PyPi repo. 
Install via pip:
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
### [CLI](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/features/cli.html) - [`cli`](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/cpx_io.cli.html#module-cpx_io.cli.cli)
`festo-cpx-io` is the main entry point to the CLI.
It supports various subcommands which execute some basic functions.

For more information use the help flag  (`festo-cpx-io -h`).
```
usage: festo-cpx-io [-h] [-v] [-i IP_ADDRESS] [-q] {cpx-e,cpx-ap} ...

options:
  -h, --help            show this help message and exit
  -v, --version         print current version
  -i IP_ADDRESS, --ip-address IP_ADDRESS
                        IP address to connect to (default: 192.168.0.1).
  -q, --quiet           remove output verbosity

subcommands:
  {cpx-e,cpx-ap}        Subcommand that should be called
```
#### Subcommands
- [`cpx-e`](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/features/cli.html#cpx-e) is a subcommand to execute commands on CPX-E devices
```
usage: festo-cpx-io cpx-e [-h] -t TYPECODE [-m MODULE_INDEX] {read,write} ...

options:
  -h, --help            show this help message and exit
  -t TYPECODE, --typecode TYPECODE
                        Typecode of the cpx setup
  -m MODULE_INDEX, --module-index MODULE_INDEX
                        Module index to read (default: 1).

action commands:
  Action to perform

  {read,write}
```
- [`cpx-ap`](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/features/cli.html#cpx-ap) is a subcommand to execute commands on CPX-AP devices
 ```
usage: festo-cpx-io cpx-ap [-h] [-si] [-ss] {read,write} ...

options:
  -h, --help            show this help message and exit
  -si, --system-information
                        Print system information
  -ss, --system-state   Print system state
  -mt, --modbus-timeout Set a modbus timeout in seconds. Minimum timeout is 0.1s (100 ms). Exception: setting timeout to 0.0s means an infinite timeout (no timeout). If you don't specify a timeout we set it internally to None and the default timeout on the device itself remains active!
action commands:
  Action to perform

  {read,write}
```

For example reading channel 2 from module 3 on a CPX-AP device with ip address 192.178.0.10:
`festo-cpx-io -i 192.178.0.10 cpx-ap read -m 3 -c 2`

### [CPX-SYSTEM](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/features/cpx_io.html) - [`cpx_system`](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/cpx_io.cpx_system.html#)
#### [CPX-E](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/cpx_io.cpx_system.cpx_e.html)
Import the library with `from cpx_io.cpx_system.cpx_e.cpx_e import CpxE`. 

Setup your system with a python context manager and print the attached modules. You can use the typecode of your system to setup all the modules, hand over a list of pre-instantiated modules in the CpxE constructor or instantiate an empty CpxE and add the modules later. In every case, the order of the modules must be consistent with the actually used hardware setup.

```
with CpxE(<typecode_string>, ip_address=<your_ip_address>) as myCPX:
    print(myCPX.modules)
```

For more information on how to setup the system and how to adress the modules read the [docs](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/features/cpx_io.html#cpx-e) see the [examples](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/examples.html#cpx-e).


#### [CPX-AP](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/cpx_io.cpx_system.cpx_ap.html)
Import the library with `from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp`.

The AP system will do all of the system setup for you. That means that you don't have to provide any more information than the ip-address. The modules are built during the runtime by a description file that will be collected directly from the modules. Since all the functionality of each module is created on your system, the documentation is also generated and stored on your device (e.g. your PC). You need to get the path by printing the system information with `CpxAp.print_system_information()`. Or just `print(CpxAp.docu_path)`

```
with CpxAp(ip_address=<your_ip_address>) as myCPX:
    myCPX.print_system_information()
```

For more information on how to setup the system and how to adress the modules, read the [docs](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/features/cpx_io.html#cpx-ap) see the [examples](https://festo-research.gitlab.io/electric-automation/festo-cpx-io/examples.html#cpx-ap).

