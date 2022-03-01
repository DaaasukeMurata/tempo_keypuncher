#!/bin/bash

curl http://www.prcd.ten.fujitsu.co.jp/

# if [ -z "${password:-""}" ]; then
# 	read -s -p "Password: " password
# 	echo
# fi

# if [[ -n ${days:-""} ]]; then
# 	days=$(echo "${days}" | awk 'BEGIN{FS=",";} {for(i=1; i<NF; i++){printf("%02d|",$i)} printf("%02d\n", $NF)}')
# fi

# # SSOID Login
# tips_login ${username} ${password} >/dev/null 2>&1

# # Get work times from the personnel system and round to 10 minutes.
# "${PATH_TOOLS}/get_worktime.sh" --user ${username} --password "${password}" -Y ${year} -M ${month} |
# 	awk -F ',' '$6~/[0-9]{2}:[0-9]{2}/ && $7~/[0-9]{2}:[0-9]{2}/{print $2, substr($6,1,4)0, substr($7,1,4)0}' |
# 	while read line; do
# 		date=$(echo "${line}" | awk '{print $1}')
# 		stime=$(echo "${line}" | awk '{print $2}')
# 		etime=$(echo "${line}" | awk '{print $3}')

# 		[[ ${date:8:2} =~ (${days:-..}) ]] || continue

# 		echo "writing data on ${date} ${stime}-${etime}"

# 		# delete the data of the day.
# 		tips_delete "${date}" >/dev/null 2>&1 &&
# 			{ printf "\t--> clear done.\n"; } ||
# 			{
# 				printf "\t--> clear failed.\n"
# 				continue
# 			}

# 		# If SubProject is none, Add project data to all day.
# 		if [[ -z ${subproject:-""} ]]; then

# 			tips_add "${employee_id}" "${date}" "${stime}" "${etime}" \
# 				"${project}" "${category}" "${task}" "${work_detail1}" "${work_detail2}" "${text}" >/dev/null 2>&1 &&
# 				{ printf "\t--> write done.\n"; } ||
# 				{
# 					printf "\t--> write failed.\n"
# 					continue
# 				}

# 		# If SubProject is set, set SubProject to AM and MainProject to PM and over time.
# 		else

# 			tips_add "${employee_id}" "${date}" "${stime}" "11:00" \
# 				"${subproject}" "${category}" "${task}" "${work_detail1}" "${work_detail2}" "${text}" >/dev/null 2>&1 &&
# 				{ printf "\t--> write SubProject done.\n"; } ||
# 				{
# 					printf "\t--> write failed.\n"
# 					continue
# 				}

# 			tips_add "${employee_id}" "${date}" "11:00" "${etime}" \
# 				"${project}" "${category}" "${task}" "${work_detail1}" "${work_detail2}" "${text}" >/dev/null 2>&1 &&
# 				{ printf "\t--> write MainProject done.\n"; } ||
# 				{
# 					printf "\t--> write failed.\n"
# 					continue
# 				}

# 		fi

# 		tips_remove_breaktime "${employee_id}" "${date}"

# 	done

# echo "All data in ${year}/${month} written."

# # SSOID Logout
# tips_logout
