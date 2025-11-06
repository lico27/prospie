import urllib.request
import json
import os
import pandas as pd
import time
from dotenv import load_dotenv

#get key from env
load_dotenv()
api_key = os.getenv("API_KEY")

def call_cc_api(operation, hdr, c_nums, charity_data, columns, df_rows):

	"""
	Calls the Charity Commission API to get data for a list of charity numbers.

	Parameters
	----------
	operation : list of API operations to call for each charity number.
	hdr : dictionary of headers to use for the API request.
	c_nums : list of charity numbers to get data for.
	charity_data : dictionary to store the data for each charity number.
	columns : list of the columns/variables required from the API.
	df_rows : list to store the data for each charity number per row.

	Returns a dataframe containing the data for each charity number.
	"""

	for num in c_nums:
		charity_data[num] = {}
		api_call_failed = False

		#get data from each api operation
		for op in operation:
			url = f"https://api.charitycommission.gov.uk/register/api/{op}/{num}/0"
			try:
				req = urllib.request.Request(url, headers=hdr)
				req.get_method = lambda: 'GET'
				response = urllib.request.urlopen(req, timeout=30)

				data = json.load(response)
				response.close()

				#get relevant columns from operation and add to charity data
				for col in columns:
					if col in data and data[col] is not None:
						charity_data[num][col] = data[col]

				#limit requests
				time.sleep(0.5)

			except Exception as e:
				print(f"Error with {op}/{num}: {e}. Skipping this organisation.")
				api_call_failed = True
				break

		#if api call failed, remove this org from the data
		if api_call_failed:
			del charity_data[num]

	#get relevant data and combine into one row per charity
	for num, data in charity_data.items():
		row = {col: data.get(col, None) for col in columns}
		row["reg_charity_number"] = num
		df_rows.append(row)

	#convert to dataframe
	try:
		df = pd.DataFrame(df_rows)
	except Exception as e:
		print(f"Error creating dataframe: {e}")
		raise

	return df

def call_financial_history_api(c_nums):
	"""
	Calls the Charity Commission API to get financial history data for a list of charity numbers.
	Returns raw financial data with minimal processing.

	Parameters
	----------
	c_nums : list of charity numbers to get data for.

	Returns a list of dictionaries containing raw financial data from the API.
	"""

	hdr = {
		"Cache-Control": "no-cache",
		"Ocp-Apim-Subscription-Key": f"{api_key}",
	}

	financial_data = []

	for num in c_nums:
		url = f"https://api.charitycommission.gov.uk/register/api/charityfinancialhistory/{num}/0"
		try:
			req = urllib.request.Request(url, headers=hdr)
			req.get_method = lambda: 'GET'
			response = urllib.request.urlopen(req, timeout=30)

			data = json.load(response)
			response.close()

			#iterate to get each year
			if isinstance(data, list):
				for year_data in data:
					row = {
						"reg_charity_number": num,
						"financial_period_end_date": year_data.get("financial_period_end_date"),
						"income": year_data.get("income"),
						"expenditure": year_data.get("expenditure")
					}
					financial_data.append(row)

			#limit requests
			time.sleep(0.5)

		except Exception as e:
			print(f"Error with charityfinancialhistory/{num}: {e}. Skipping this organisation.")
			continue

	return financial_data

def extract_cc_data(c_nums):

	#define api variables
	hdr ={
		"Cache-Control": "no-cache",
		"Ocp-Apim-Subscription-Key": f"{api_key}",
		}
	operation = ["allcharitydetailsV2", "charityoverview", "charitygoverningdocument"]
	charity_data = {}
	columns = ["reg_charity_number", "charity_name", "web", "activities", "charitable_objects", "latest_income", "latest_expenditure", "who_what_where", "CharityAoOCountryContinent", "CharityAoOLocalAuthority", "CharityAoORegion"]
	df_rows = []

	#call api
	df = call_cc_api(operation, hdr, c_nums, charity_data, columns, df_rows)

	return df
