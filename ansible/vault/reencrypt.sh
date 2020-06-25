#!/bin/bash
cd $(dirname $0)

KEYHOLDERS=$(cat keyholders | cut -d ' ' -f 1)

for key in $KEYHOLDERS; do
        expiration_date=$(gpg --list-keys $key | grep "\[expire" | cut -d ":" -f 2 | cut -d " " -f 2 | cut -d "]" -f 1 | head -n 1)
        if [ "" != "$expiration_date" ]; then
                today=$(date +%s)
                expires=$(date -d $expiration_date +%s)

                if [ $expires -ge $today ]; then
                        echo "${key} expires on ${expiration_date}."
                else
                        echo "${key} expired on ${expiration_date}."
                        sed -i "/^${key}.*/d" ./keyholders
                        echo "DELETED ${key} from keyholders"
                fi
        fi
done

KEY=$(gpg -d ./vault_passphrase.asc)
if [ -z "$KEY" ]
then
        printf "\nDecrypting ./vault_passphrase.asc failed.\n"
        echo -n "Please enter password: "
        read KEY
fi

CMDLINE=""

for i in $KEYHOLDERS
do
        CMDLINE="$CMDLINE -r $i"
done

echo $KEY | gpg -vvvv -e -a $CMDLINE > vault_passphrase.asc
