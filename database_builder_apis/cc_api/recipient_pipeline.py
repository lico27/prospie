import pandas as pd
from cc_api.client import extract_cc_data
from cc_api.areas_builder import transform_area_columns
from utils import clean_data

def get_recipient_data(recipient_grants, recipients_info, areas):

	#handle empty recipient_grants
	if recipient_grants.empty or len(recipient_grants) == 0:
		empty_recipients = pd.DataFrame(columns=["recipient_id", "recipient_name", "recipient_activities"])
		empty_recipient_areas = pd.DataFrame(columns=["recipient_id", "area_id"])
		return empty_recipients, empty_recipient_areas, areas

	#convert recipients to list
	c_nums = list(recipient_grants[recipient_grants["recipient_id"].notna() & recipient_grants["recipient_id"].str.isdigit()]["recipient_id"])

	#handle empty c_nums
	if not c_nums or len(c_nums) == 0:
		#return non-charity recipients directly
		non_charity_recipients = recipients_info.copy()
		empty_recipient_areas = pd.DataFrame(columns=["recipient_id", "area_id"])
		return non_charity_recipients, empty_recipient_areas, areas

	recipient_df = extract_cc_data(c_nums)

	#handle empty recipient_df
	if recipient_df.empty or len(recipient_df) == 0:
		non_charity_recipients = recipients_info.copy()
		empty_recipient_areas = pd.DataFrame(columns=["recipient_id", "area_id"])
		return non_charity_recipients, empty_recipient_areas, areas

	#rename and prepare for area extraction
	recipient_df = recipient_df.rename(columns={
		"reg_charity_number": "registered_num",
		"CharityAoOCountryContinent": "country_continent",
		"CharityAoOLocalAuthority": "local_authority",
		"CharityAoORegion": "region"
	})

	#extract area names from recipient data
	_, recipient_all_areas = transform_area_columns(recipient_df)
	recipient_all_areas = recipient_all_areas.drop_duplicates()

	#find new areas that don't exist in the areas table yet
	existing_areas = areas.rename(columns={"area_level": "area_type"})
	new_areas = recipient_all_areas[["area_name", "area_type"]].drop_duplicates()
	new_areas = new_areas.merge(
		existing_areas[["area_name", "area_type"]],
		on=["area_name", "area_type"],
		how="left",
		indicator=True
	)
	new_areas = new_areas[new_areas["_merge"] == "left_only"][["area_name", "area_type"]]

	#add new areas to the areas table with new IDs
	if len(new_areas) > 0:
		#handle empty areas table
		if areas.empty or len(areas) == 0:
			next_area_id = 1
		else:
			next_area_id = int(areas["area_id"].max()) + 1
		new_areas["area_id"] = range(next_area_id, next_area_id + len(new_areas))
		new_areas = new_areas.rename(columns={"area_type": "area_level"})
		areas = pd.concat([areas, new_areas], ignore_index=True)

	#merge with updated areas table to get area IDs
	recipient_areas = recipient_all_areas.merge(
		areas.rename(columns={"area_level": "area_type"}),
		on=["area_name", "area_type"]
	)[["registered_num", "area_id"]].drop_duplicates()
	recipient_areas = recipient_areas.rename(columns={"registered_num": "recipient_id"})

	#build recipient table
	recipients = recipient_df[["registered_num", "charity_name", "activities"]]
	recipients = recipients.rename(columns={"registered_num": "recipient_id", "charity_name": "recipient_name", "activities": "recipient_activities"})

	#clean data
	cc_recipient_tables = [recipients, recipient_areas]
	clean_tables_recipients = clean_data(cc_recipient_tables, ["recipient_name"], ["recipient_activities"], [])
	recipients, recipient_areas = clean_tables_recipients

	#add non-charity recipients using actual data from 360Giving API
	existing_recipient_ids = set(recipients["recipient_id"])
	all_recipient_ids = set(recipient_grants["recipient_id"].dropna())
	missing_recipient_ids = all_recipient_ids - existing_recipient_ids

	if len(missing_recipient_ids) > 0:
		#filter recipients_info to only include missing (non-charity) recipients
		non_charity_recipients = recipients_info[recipients_info["recipient_id"].isin(missing_recipient_ids)].copy()
		recipients = pd.concat([recipients, non_charity_recipients], ignore_index=True)

	return recipients, recipient_areas, areas