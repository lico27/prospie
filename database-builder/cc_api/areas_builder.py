import pandas as pd
from cc_api.transformers import ensure_area_columns

def transform_area_columns(df):

    """
    Transforms area lists into separate columns.
    """

    expected_columns = {
        "country_continent": ["country", "continent"],
        "local_authority": ["local_authority", "metropolitan_county"],
        "region": ["region"]
    }

    #explode areas and normalise into columns
    exploded_df_country_continent = df.explode("country_continent")
    country_continent_df = ensure_area_columns(
        exploded_df_country_continent, "country_continent",
        expected_columns["country_continent"]
    )

    exploded_df_local_authority = df.explode("local_authority")
    local_authority_df = ensure_area_columns(
        exploded_df_local_authority, "local_authority",
        expected_columns["local_authority"]
    )

    exploded_df_region = df.explode("region")
    region_df = ensure_area_columns(
        exploded_df_region, "region",
        expected_columns["region"]
    )

    #rest indexes and combine
    exploded_df_country_continent = exploded_df_country_continent.reset_index(drop=True)
    country_continent_df = country_continent_df.reset_index(drop=True)

    exploded_df_local_authority = exploded_df_local_authority.reset_index(drop=True)
    local_authority_df = local_authority_df.reset_index(drop=True)

    exploded_df_region = exploded_df_region.reset_index(drop=True)
    region_df = region_df.reset_index(drop=True)

    areas_df = pd.concat([exploded_df_country_continent, country_continent_df,
                        local_authority_df, region_df], axis=1)

    #drop unnecessary columns and rows
    areas_df = areas_df.drop(columns=["name", "website", "activities", "objectives",
                                      "income", "expenditure", "classifications",
                                      "country_continent", "local_authority", "region",
                                      "area_welsh_ind"], errors="ignore")
    areas_df.columns = [col.replace("area_", "") for col in areas_df.columns]

    area_columns = ["country", "continent", "region", "local_authority", "metropolitan_county"]

    #tidy empty/nan values
    for col in area_columns:
        if col in areas_df.columns:
            areas_df[col] = areas_df[col].apply(lambda x: None if x == [] or pd.isna(x) else x)

    area_types = {
        "local_authority": "local_authority",
        "metropolitan_county": "metropolitan_county",
        "region": "region",
        "country": "country",
        "continent": "continent"
    }

    #pivot to create area-charity combinations
    areas = []
    for _, row in areas_df.iterrows():
        #skip rows with null registered_num
        if pd.isna(row.get("registered_num")) or not row.get("registered_num"):
            continue

        for column, area_type in area_types.items():
            if column in areas_df.columns and pd.notna(row[column]) and row[column]:
                areas.append({
                    "registered_num": row["registered_num"],
                    "area_name": row[column],
                    "area_type": area_type
                })

    #build dataframe with everything
    all_areas = pd.DataFrame(areas)

    #drop unnecessary columns
    areas = all_areas[["area_name", "area_type"]].drop_duplicates().reset_index(drop=True)
    areas = areas.rename(columns={"area_type": "area_level"})

    return areas, all_areas

def build_areas_tables(df):

    areas, all_areas = transform_area_columns(df)

    #create unique ids for areas
    areas["area_id"] = range(401, 401 + len(areas))

    #build join table
    funder_areas = all_areas.merge(
        areas.rename(columns={"area_level": "area_type"}),
        on=["area_name", "area_type"]
    )[["registered_num", "area_id"]].drop_duplicates()

    return funder_areas, areas
