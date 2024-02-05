#!/bin/bash

# k get --namespace extdns service extdns-coredns -o jsonpath={'.status.loadBalancer.ingress[0].ip'}
# 10.164.10.4

apt update && apt install dnsutils -y

# echo "nameserver 10.164.10.4" > /etc/resolv.conf
# dig tango-databaseds.ci-ska-mid-itf-at-1838-update-main.svc.miditf.internal.skao.int

export TANGO_HOST=tango-databaseds.ci-ska-mid-itf-at-1838-update-main.svc.miditf.internal.skao.int:10000

poetry run python3 -m src.ska_mid_itf_engineering_tools.talon_on