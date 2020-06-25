#!/bin/sh
set -e -u
have() {
	command -v "$1" >/dev/null
}
if have gpg2; then
	GPG="gpg2"
else
	GPG="gpg"
fi
exec "$GPG" --batch --use-agent --decrypt --quiet $(dirname $0)/vault_passphrase.asc