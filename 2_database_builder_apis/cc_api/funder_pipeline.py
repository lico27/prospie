from cc_api.client import extract_cc_data
from cc_api.classifications_builder import build_classifications_tables
from cc_api.areas_builder import build_areas_tables
from utils import clean_data

def get_funder_data(c_nums):

	df = extract_cc_data(c_nums)

	#rename columns to match schema
	df = df.rename(columns={
		"reg_charity_number": "registered_num",
		"charity_name": "name",
		"web": "website",
		"charitable_objects": "objectives",
		"latest_income": "income",
		"latest_expenditure": "expenditure",
		"who_what_where": "classifications",
		"CharityAoOCountryContinent": "country_continent",
		"CharityAoOLocalAuthority": "local_authority",
		"CharityAoORegion": "region"
	})

	#build funders table
	funders = df.drop(columns=["classifications", "country_continent", "local_authority", "region"])

	#build beneficiaries and causes tables and join tables
	beneficiaries, funder_beneficiaries, causes, funder_causes = build_classifications_tables(df)

	#build areas table and join table
	funder_areas, areas = build_areas_tables(df)

	#clean data
	cc_funder_tables = [funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas]
	clean_tables_funders = clean_data(cc_funder_tables, ["name"], ["activities", "objectives"], [])
	funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas = clean_tables_funders

	return funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas
