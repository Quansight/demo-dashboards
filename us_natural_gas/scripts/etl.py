import json
import os
import re
import pandas as pd

# find root category


def get_root_category(categories_by_id):
    root_cat_id = None
    for c in categories_by_id.values():
        if c['parent_category_id'] not in categories_by_id:
            root_cat_id = c['parent_category_id']
            break
    return root_cat_id

# For a given parent category id, returns the list of children categories


def get_sub_categories_ids(parent_cat_id, categories_by_id):
    result = []
    for c in categories_by_id.values():
        if c['parent_category_id'] == parent_cat_id:
            result.append(c['category_id'])
    return result


# returns a dict of pandas df.
# Keys can be A (Annual) or M (Monthly)
def df_for_cat_id(cat_id, categories_by_id, series_by_id):

    df_per_timeframe = {}
    for s_id in categories_by_id[cat_id]['childseries']:

        timeframe = series_by_id[s_id]['f']

        if timeframe not in df_per_timeframe:
            df_per_timeframe[timeframe] = []

        for period, value in series_by_id[s_id]['data']:

            if 'iso3166' not in series_by_id[s_id]:
                # happens for Offshore places
                continue

            df_per_timeframe[timeframe].append({
                'iso3166': series_by_id[s_id]['iso3166'],
                'geography': series_by_id[s_id]['geography'],
                'units': series_by_id[s_id]['units'],
                'unitsshort': series_by_id[s_id]['unitsshort'],
                'period': period,
                'value': value
            })

    for timeframe in df_per_timeframe:
        df_per_timeframe[timeframe] = pd.DataFrame(df_per_timeframe[timeframe])

    return df_per_timeframe


if __name__ == "__main__":

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # load the data
    with open("../data/raw/NG.txt") as f:
        raw_data = [json.loads(l) for l in f.readlines()]

    # Build two big dictionnarie, indexed by ids
    series_by_id = {}
    categories_by_id = {}

    for r in raw_data:
        if 'series_id' in r:
            series_by_id[r['series_id']] = r
        elif 'category_id' in r:
            categories_by_id[r['category_id']] = r

    root_cat_id = get_root_category(categories_by_id)
    print("root_cat_id : ", root_cat_id)

    # now we're going to browse the data sub category by sub category,
    # create directories and the dataframes in the end
    cat_level1 = get_sub_categories_ids(root_cat_id, categories_by_id)
    for cat1_id in cat_level1:
        print(cat1_id, categories_by_id[cat1_id]['name'])
        main_cat = categories_by_id[cat1_id]['name']
        for cat2_id in get_sub_categories_ids(cat1_id, categories_by_id):
            print("\t", cat2_id,  categories_by_id[cat2_id]['name'])

            for cat3_id in get_sub_categories_ids(cat2_id, categories_by_id):

                # We're aggregating data "by Data Series", meaning we
                #  assemble data of the same topic, originally spread around multiplie rows, one row per state.
                # 1 topic -> N states
                if categories_by_id[cat3_id]['name'] != "by Data Series":
                    continue
                # Also possible : aggregate "by Area", if we need to assemble data or various topics for each state
                # (1 state -> N topics)

                #  Create the directory only once we know there are data "by data series".
                main_cat = re.sub(r'[\\/*?:"<>|]', "", main_cat.strip())
                cat2_path = os.path.join("../data/etl", main_cat,
                                         categories_by_id[cat2_id]['name'].strip())
                os.makedirs(cat2_path, exist_ok=True)

                for cat4_id in get_sub_categories_ids(cat3_id, categories_by_id):
                    dataset_name = categories_by_id[cat4_id]['name']
                    dataset_name = re.sub(r'[\\/*?:"<>|]', "", dataset_name)

                    dfs = df_for_cat_id(
                        cat4_id, categories_by_id, series_by_id)

                    for timeframe in dfs:
                        df_path = "%s/%s_%s.csv" % (cat2_path,
                                                    dataset_name, timeframe)
                        dfs[timeframe].to_csv(df_path, index=False)

                    print("\t\t", len(dfs), dataset_name)
