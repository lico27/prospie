from cc_api.funder_pipeline import get_funder_data
from cc_api.recipient_pipeline import get_recipient_data
from giving360_api.grants_pipeline import get_grant_data

def get_data(c_nums, supabase_url, supabase_key):

	#call charity commission api and extract data to build tables for funders
	funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas = get_funder_data(c_nums, supabase_url, supabase_key)

	#call giving360 api and extract data
	grants, funder_grants, recipient_grants, recipients_info = get_grant_data(c_nums)

	#call charity commission api and extract data to build tables for recipients and update with any new areas
	recipients, recipient_areas, areas = get_recipient_data(recipient_grants, recipients_info, areas)

	return funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas, grants, funder_grants, recipients, recipient_grants, recipient_areas