#!/bin/bash
set -euxo pipefail
lxc-stop shell-agent
lxc-destroy shell-agent
lxc-create shell-agent -t download -- -d debian -r trixie -a amd64
lxc-start shell-agent
lxc-attach shell-agent -- mkdir ~
