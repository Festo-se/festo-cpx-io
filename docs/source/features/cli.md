# CLI

## festo-cpx-io 

### cpx-e

#### read
`festo-cpx-io -i 192.168.0.2 cpx-e -t 60E-EP-M read -c 1`

#### write
`festo-cpx-io -i 192.168.0.2 cpx-e -t 60E-EP-L write -c 1`

### cpx-ap

#### system state
`festo-cpx-io -i 192.168.0.2 -q cpx-ap -ss`

#### system information
`festo-cpx-io cpx-ap -si`

#### read
`festo-cpx-io -i 192.168.1.13 cpx-ap read -m 1 -c 1` 

#### write
`festo-cpx-io -i 192.168.1.13 cpx-ap write -m 1 -c 1 1`
