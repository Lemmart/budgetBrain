from datetime import datetime
import pandas as pd
from os import path


def monthMappingBuilder():
    month_map = {}
    for i in range(1, 13):
        month = datetime.strptime(str(i), '%m').strftime('%b')
        month_map[month] = {}
    print('[INFO] Finished building {month : {} } mapping.\n')
    return month_map


def expenseToCategoryAndCategoryMappingBuilder(exp_to_cat_filename='expToCatMapping.txt'):
    exp_to_cat_filename_with_path = 'src/' + exp_to_cat_filename

    category_mapping = {}
    exp_to_cat_mapping = {}

    if path.exists(exp_to_cat_filename_with_path):
        df = pd.read_csv(exp_to_cat_filename_with_path, sep=':')
        for index, entry in df.iterrows():
            expense = entry[0]
            category = entry[1]

            if category not in category_mapping:
                category_mapping[category] = 0
            if expense not in exp_to_cat_mapping:
                exp_to_cat_mapping[expense] = category
    else:
        print('[DEBUG] Failed to find file', exp_to_cat_filename_with_path, '.\n')

    print('[INFO] Finished building {expense : category} mapping and {category : 0} mapping.\n')
    return category_mapping, exp_to_cat_mapping


def builder():
    months_mapping = monthMappingBuilder()
    category_mapping, exp_to_cat_mapping = expenseToCategoryAndCategoryMappingBuilder()

    for month in months_mapping.keys():
        months_mapping[month] = {}
        for category in category_mapping.keys():
            months_mapping[month][category] = 0
    print('[INFO] Finished building {month_name : {category : 0} } mapping.\n')
    return months_mapping, category_mapping


def bankReader(updated_mappings, category_mapping):
    pass


def creditCardReader(updated_mappings, category_mapping):
    pass


def rentAndUtilityReader(updated_mappings, category_mapping):
    pass


def reader(basic_mapping, category_mapping):
    updated_mapping = bankReader(basic_mapping, category_mapping)
    updated_mapping = creditCardReader(basic_mapping, category_mapping)
    updated_mapping = rentAndUtilityReader(basic_mapping, category_mapping)
    return updated_mapping


def writer(final_mappings):
    pass


if __name__ == '__main__':
    basic_mappings, category_mappings = builder()
    enriched_mappings = reader(basic_mappings, category_mappings)
    writer(enriched_mappings)