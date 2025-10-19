import pandas as pd
from giving360_api.client import call_360_api
from utils import clean_data

def get_grant_data(c_nums):

        """
        Gets data from the 360Giving API.
        Returns dataframes to be piped to database, containing information about grants reported to 360Giving.
        Also builds join tables to deal with many-to-many relationships in the database.
        """

        try:
                #call api and normalise data from lists into required columns
                grants = call_360_api(c_nums)

                #handle empty grants list
                if not grants or len(grants) == 0:
                        empty_grants = pd.DataFrame(columns=["grant_id", "grant_title", "grant_desc", "amount", "currency", "year"])
                        empty_funder_grants = pd.DataFrame(columns=["grant_id", "registered_num"])
                        empty_recipient_grants = pd.DataFrame(columns=["grant_id", "recipient_id"])
                        empty_recipients_info = pd.DataFrame(columns=["recipient_id", "recipient_name", "recipient_activities"])
                        return empty_grants, empty_funder_grants, empty_recipient_grants, empty_recipients_info

                df = pd.json_normalize(grants)
                grant_columns = ["grant_id", "funder_registered_num", "data.title", "data.description", "data.amountAwarded", "data.currency", "data.awardDate", "data.recipientOrganization"]
                grant_df = df[grant_columns]
        except Exception as e:
                print(f"Error with initial API call: {e}")
                raise

        try:
                #explode recipient list and normalise into columns
                exploded_df_recipients = grant_df.explode("data.recipientOrganization")
                recipients_df = pd.json_normalize(exploded_df_recipients["data.recipientOrganization"])
                recipients_df.columns = ["recipient_" + col for col in recipients_df.columns]

                #reset indexes and combine
                exploded_df_recipients = exploded_df_recipients.reset_index(drop=True)
                recipients_df = recipients_df.reset_index(drop=True)
                grants = pd.concat([exploded_df_recipients, recipients_df], axis=1)

        except Exception as e:
                print(f"Error processing recipient data: {e}")
                raise

        try:
                #finalise and tidy grants table
                grants = grants[["grant_id", "data.title", "data.description", "data.amountAwarded", "data.currency", "data.awardDate", "recipient_id", "recipient_name", "recipient_description"]]
                grants.loc[:, 'data.awardDate'] = grants['data.awardDate'].astype(str).str.strip().str[:4]
                grants = grants.rename(columns={"data.title": "grant_title",
                                                "data.description": "grant_desc",
                                                "data.amountAwarded": "amount",
                                                "data.currency": "currency",
                                                "data.awardDate": "year"
                                                })
                grants["recipient_id"] = grants["recipient_id"].str.replace("^GB-CHC-", "", regex=True)
                grants = grants.rename(columns={"recipient_description": "recipient_activities"})

                #build join tables
                funder_grants = grant_df[["grant_id", "funder_registered_num"]].rename(columns={"funder_registered_num": "registered_num"})
                recipient_grants = grants[["grant_id", "recipient_id"]]

                #build recipients info table for non-charity recipients
                #keep first occurrence of each recipient_id to avoid duplicates
                recipients_info = grants[["recipient_id", "recipient_name", "recipient_activities"]].drop_duplicates(subset=["recipient_id"], keep="first")

                #drop unnecessary columns from grants table
                grants = grants.drop(columns=["recipient_id", "recipient_name", "recipient_activities"])

        except Exception as e:
                print(f"Error building tables: {e}")
                raise

        #clean data
        g360_tables = [grants, funder_grants, recipient_grants, recipients_info]
        clean_tables_grants = clean_data(g360_tables, ["grant_title", "recipient_name"], ["grant_desc", "recipient_activities"], ["year"])
        grants, funder_grants, recipient_grants, recipients_info = clean_tables_grants

        return grants, funder_grants, recipient_grants, recipients_info
