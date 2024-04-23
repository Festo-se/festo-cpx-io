from cpx_io.cpx_system.cpx_ap.cpx_ap import CpxAp

with CpxAp(ip_address="172.16.1.41") as cpx:
    cpx.print_system_information()
