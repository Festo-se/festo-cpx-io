# CLI

## festo-cpx-io 

### cpx-e

#### read
Read channel value. For example read channel 1 from 16DI Module:
`festo-cpx-io -i 192.168.0.2 cpx-e -t 60E-EP-M read -c 1`

#### write
Write channel value. For example write channel 1 from 8DO Module:
`festo-cpx-io -i 192.168.0.2 cpx-e -t 60E-EP-L write -c 1 True`

### cpx-ap

#### system state
Print the system state to the console.
`festo-cpx-io -i 192.168.0.2 -q cpx-ap -ss`

#### system information
Print the system information to the console.
`festo-cpx-io cpx-ap -si`

#### read
Read channel value. For example read channel 0 from module 1:
`festo-cpx-io -i 192.168.1.13 cpx-ap read -m 1 -c 0`

#### write
Write channel value. For example write channel 0 of module 1 with value 1:
`festo-cpx-io -i 192.168.1.13 cpx-ap write -m 1 -c 0 1`
