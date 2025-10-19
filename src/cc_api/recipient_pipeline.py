import pandas as pd
from src.cc_api.client import extract_cc_data
from src.cc_api.areas_builder import transform_area_columns
from src.utils import clean_data

def get_recipient_data(recipient_grants, recipients_info, areas):

	#convert recipients to list
	c_nums = list(recipient_grants[recipient_grants["recipient_id"].str.isdigit()]["recipient_id"])

	recipient_df = extract_cc_data(c_nums)

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
		next_area_id = areas["area_id"].max() + 1
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