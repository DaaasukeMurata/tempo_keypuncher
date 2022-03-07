#!/bin/bash

export no_proxy=${no_proxy},.fujitsu.co.jp,.fujitsu.com,.denso-ten.com

usage() {
    cat <<EOF

Usage: 
    $0 --user ${username} --password "${password}" -Y ${year} -M ${month}
EOF
}

for OPT in "$@"; do
    case "$OPT" in
    '-h' | '--help')
        usage
        exit 1
        ;;

    '--year' | '-Y')
        if [[ -z "$2" ]] || [[ "$2" =~ ^-+ ]]; then
            echo "$PROGNAME: option requires an argument -- $1" 1>&2
            exit 1
        fi
        year="$2"
        shift 2
        ;;

    '--month' | '-M')
        if [[ -z "$2" ]] || [[ "$2" =~ ^-+ ]]; then
            echo "$PROGNAME: option requires an argument -- $1" 1>&2
            exit 1
        fi
        month="$2"
        shift 2
        ;;

    '--user')
        if [[ -z "$2" ]] || [[ "$2" =~ ^-+ ]]; then
            echo "$PROGNAME: option requires an argument -- $1" 1>&2
            exit 1
        fi
        username="$2"
        shift 2
        ;;

    '--password')
        if [[ -z "$2" ]] || [[ "$2" =~ ^-+ ]]; then
            echo "$PROGNAME: option requires an argument -- $1" 1>&2
            exit 1
        fi
        password="$2"
        shift 2
        ;;

    '--' | '-')
        shift 1
        param+=("$@")
        break
        ;;
    -*)
        echo "$PROGNAME: illegal option -- '$(echo $1 | sed 's/^-*//')'" 1>&2
        exit 1
        ;;

    *)
        if [[ ! -z "$1" ]] && [[ ! "$1" =~ ^-+ ]]; then
            param+=("$1")
            shift 1
        fi
        ;;
    esac
done

if [ -z "${password}" ]; then
    read -s -p "Password: " password
    echo
fi

url_login="https://cws.local.denso-ten.com/cws/cws"
url_get_worktime="https://cws.local.denso-ten.com/cws/cws"

html=$(curl -X GET -k -s -w "%{url_effective}\n" -L "${url_login}")
url_redirect=$(echo -n "${html}" | tail -n 1)

target=$(echo -n "${html}" | grep -o '<input.*TARGET.*>' | sed -E "s/.*value=\"(.*)\".*/\1/g")
sm_auth_reason=$(echo -n "${html}" | grep -o '<input.*SMAUTHREASON.*>' | sed -E "s/.*value=\"(.*)\".*/\1/g")
sm_agent_name=$(echo -n "${html}" | grep -o '<input.*SMAGENTNAME.*>' | sed -E "s/.*value=\"(.*)\".*/\1/g")
post_preservation_data=$(echo -n "${html}" | grep -o '<input.*POSTPRESERVATIONDATA.*>' | sed -E "s/.*value=\"(.*)\".*/\1/g")
sm_enc=$(echo -n "${html}" | grep -o '<INPUT.*SMENC.*>' | sed -E "s/.*VALUE=\"(.*)\".*/\1/g")
sm_locale=$(echo -n "${html}" | grep -o '<INPUT.*SMLOCALE.*>' | sed -E "s/.*value=\"(.*)\".*/\1/g")

# login with SSOID
curl -X POST -L -k -s -c .cookie.worktime \
    -A 'User-Agent: Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1)' \
    --data-urlencode "TARGET=${target}" \
    --data-urlencode "SMAUTHREASON=${sm_auth_reason}" \
    --data-urlencode "SMAGENTNAME=${sm_agent_name}" \
    --data-urlencode "POSTPRESERVATIONDATA=${post_preservation_data}" \
    --data-urlencode "USER=${username}" \
    --data-urlencode "PASSWORD=${password}" \
    --data-urlencode "SMENC=${sm_enc}" \
    --data-urlencode "SMLOCALE=${sm_locale}" \
    "${url_redirect}" >/dev/null

sleep 2

# Get worktime
curl -X POST -k -s -b .cookie.worktime \
    -A 'User-Agent: Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1)' \
    --data-urlencode "@SID=" \
    --data-urlencode "@SQ=4" \
    --data-urlencode "@SN=root.cws.shuro.personal.aero_personal.aero_personal_menu006" \
    --data-urlencode "@FN=-1688251548" \
    --data-urlencode "@FS=I" \
    --data-urlencode "@SRACT=ExecuteAeroAction" \
    --data-urlencode "@SRSNDF=FormAeroMenu" \
    --data-urlencode "@SRSNDC=NONE" \
    --data-urlencode "@SRCMD0=NONE" \
    --data-urlencode "@SRCMD1=NONE" \
    --data-urlencode "@SRCMD2=NONE" \
    --data-urlencode "@SRCMD3=NONE" \
    --data-urlencode "@SRCMD4=NONE" \
    --data-urlencode "posX=0" \
    --data-urlencode "posY=0" \
    --data-urlencode "TCDR_NTYEAR=${year}" \
    --data-urlencode "TCDR_NTMONTH=${month}" \
    --data-urlencode "dummy=" \
    "${url_get_worktime}" |
    tr -d '\n ' |
    sed -r -e 's@<table[^>]*>@\n@gi' -e 's@</table[^>]*>@\n@gi' |
    grep "勤務名称" |
    sed -r -e 's@</td[^>]*>@,@gi' -e 's@,</tr[^>]*>@\n@gi' -e 's@<[^>]*>@@gi' -e 's@\&nbsp;@ @gi' |
    grep -v "合計"

# logout
rm .cookie.worktime
