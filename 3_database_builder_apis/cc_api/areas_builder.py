import pandas as pd
from supabase import create_client
from cc_api.transformers import ensure_area_columns

def transform_area_columns(df):

    """
    Transforms area lists into separate columns.
    """

    area_types = {
        "country": "country",
        "continent": "continent",
        "local_authority": "local_authority",
        "metropolitan_county": "metropolitan_county",
        "region": "region"
    }

    #process each charity and collect all areas
    all_areas = []

    for _, row in df.iterrows():
        registered_num = row.get("registered_num")

        if pd.isna(registered_num) or not registered_num:
            continue

        #process country_continent
        country_continent = row.get("country_continent")
        if country_continent is not None and not (isinstance(country_continent, float) and pd.isna(country_continent)):
            country_continent_list = country_continent if isinstance(country_continent, list) else [country_continent]
            for item in country_continent_list:
                if isinstance(item, dict):
                    if item.get("country"):
                        all_areas.append({
                            "registered_num": registered_num,
                            "area_name": item["country"],
                            "area_type": "country"
                        })
                    if item.get("continent"):
                        all_areas.append({
                            "registered_num": registered_num,
                            "area_name": item["continent"],
                            "area_type": "continent"
                        })

        #process local_authority
        local_authority = row.get("local_authority")
        if local_authority is not None and not (isinstance(local_authority, float) and pd.isna(local_authority)):
            local_authority_list = local_authority if isinstance(local_authority, list) else [local_authority]
            for item in local_authority_list:
                if isinstance(item, dict):
                    if item.get("local_authority"):
                        all_areas.append({
                            "registered_num": registered_num,
                            "area_name": item["local_authority"],
                            "area_type": "local_authority"
                        })
                    if item.get("metropolitan_county"):
                        all_areas.append({
                            "registered_num": registered_num,
                            "area_name": item["metropolitan_county"],
                            "area_type": "metropolitan_county"
                        })

        #process region
        region = row.get("region")
        if region is not None and not (isinstance(region, float) and pd.isna(region)):
            region_list = region if isinstance(region, list) else [region]
            for item in region_list:
                if isinstance(item, dict):
                    if item.get("region"):
                        all_areas.append({
                            "registered_num": registered_num,
                            "area_name": item["region"],
                            "area_type": "region"
                        })

    #build dataframe with everything
    all_areas = pd.DataFrame(all_areas)

    #handle empty dataframe
    if all_areas.empty:
        all_areas = pd.DataFrame(columns=["registered_num", "area_name", "area_type"])
        areas = pd.DataFrame(columns=["area_name", "area_level"])
        return areas, all_areas

    #drop unnecessary columns
    areas = all_areas[["area_name", "area_type"]].drop_duplicates().reset_index(drop=True)
    areas = areas.rename(columns={"area_type": "area_level"})

    return areas, all_areas

def build_areas_tables(df, supabase_url, supabase_key):

    areas, all_areas = transform_area_columns(df)

    #connect to supabase and query existing areas
    supabase = create_client(supabase_url, supabase_key)

    try:
        #fetch all existing areas from database
        result = supabase.table("areas").select("area_id, area_name, area_level").execute()

        if result.data and len(result.data) > 0:
            existing_areas = pd.DataFrame(result.data)
            existing_areas["area_id"] = existing_areas["area_id"].astype(int)
            max_area_id = existing_areas["area_id"].max()
            next_area_id = max_area_id + 1
        else:
            existing_areas = pd.DataFrame(columns=["area_id", "area_name", "area_level"])
            next_area_id = 1
    except Exception as e:
        print(f"ERROR: Could not fetch existing areas from database: {e}")
        raise

    #merge with existing areas to reuse IDs for duplicates
    areas = areas.merge(existing_areas, on=["area_name", "area_level"], how="left")
    new_areas_mask = areas["area_id"].isna()
    num_new_areas = new_areas_mask.sum()
    areas.loc[new_areas_mask, "area_id"] = range(next_area_id, next_area_id + num_new_areas)
    areas["area_id"] = areas["area_id"].astype(int)

    #build join table
    funder_areas = all_areas.merge(
        areas.rename(columns={"area_level": "area_type"}),
        on=["area_name", "area_type"]
    )[["registered_num", "area_id"]].drop_duplicates()

    return funder_areas, areas
