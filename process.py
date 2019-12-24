from datetime import datetime
import pandas as pd
import os

################
### BUILDERS ###
################

def month_mapping_builder():
    month_map = {}
    for i in range(1, 13):
        month = datetime.strptime(str(i), '%m').strftime('%b')
        month_map[month] = {}
    print('[INFO] Finished building {month : {} } mapping.\n')
    return month_map


def expense_to_category_and_category_mapping_builder(exp_to_cat_filename='expToCatMapping.txt'):
    exp_to_cat_filename_with_path = 'src/' + exp_to_cat_filename

    category_mapping = {}
    exp_to_cat_mapping = {}

    if os.path.exists(exp_to_cat_filename_with_path):
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
    months_mapping = month_mapping_builder()
    category_mapping, exp_to_cat_mapping = expense_to_category_and_category_mapping_builder()

    for month in months_mapping.keys():
        months_mapping[month] = {}
        for category in category_mapping.keys():
            months_mapping[month][category] = 0
    print('[INFO] Finished building {month_name : {category : 0} } mapping.\n')
    return months_mapping, category_mapping


###############
### HELPERS ###
###############

def prompt_for_cols(filename, headers=None):
    print('Given the following headers in the file', filename, '\n', headers)
    exp_name = input('Which column should be used for the expense name? ')
    exp_amount = input('Which column should be used for the expense amount? ')
    exp_date = input('Which column should be used for the expense date? ')
    return exp_name, exp_amount, exp_date


def list_files(file_history_type, path=''):
    print('There are the following files in the data/ directory.')
    print(os.listdir(path))
    bank_filename = path + '/' + input('What is the name of the file containing your', file_history_type, ' history? ')
    rows_to_skip = int(input('How many rows, if any, should be skipped to obtain the headers of your file? '))
    return bank_filename, rows_to_skip

def update_monthly_mappings(df, name, amount, date, updated_mappings, category_mapping):
    pass


###############
### READERS ###
###############

def bank_reader(updated_mappings, category_mapping):
    # TODO: Ignore water, trash, electric, internet (utilities are covered under credit card) and credit card payments
    bank_filename, rows_to_skip = list_files('bank', 'data')

    # TODO: make date column selectable PRIOR to read_csv NOT after
    df = pd.read_csv(bank_filename, skiprows=rows_to_skip, parse_dates=['Date'])
    name, amount, date = prompt_for_cols(bank_filename, df.keys())

    # updated_mappings, category_mapping = update_monthly_mappings(df, name, amount, date, updated_mappings, category_mapping)

    print('[INFO] Finished reading bank data.\n')
    return updated_mappings, category_mapping


def credit_card_reader(updated_mappings, category_mapping):
    bank_filename, rows_to_skip = list_files('credit card', 'data')

    # updated_mappings, category_mapping = update_monthly_mappings(df, name, amount, date, updated_mappings, category_mapping)

    print('[INFO] Finished reading credit card data.\n')
    return updated_mappings, category_mapping


def rent_and_utility_reader(updated_mappings, category_mapping):
    bank_filename, rows_to_skip = list_files('rent and utility', 'data')

    # updated_mappings, category_mapping = update_monthly_mappings(df, name, amount, date, updated_mappings, category_mapping)

    print('[INFO] Finished reading rent and utility data.\n')
    return updated_mappings, category_mapping


def reader(basic_mapping, category_mapping):
    updated_mapping, category_mapping = bank_reader(basic_mapping, category_mapping)
    updated_mapping, category_mapping = credit_card_reader(basic_mapping, category_mapping)
    updated_mapping, _ = rent_and_utility_reader(basic_mapping, category_mapping)

    print('[INFO] Finished reading all data.\n')
    return updated_mapping


###############
### WRITERS ###
###############S

def writer(final_mappings):
    pass


if __name__ == '__main__':
    basic_mappings, category_mappings = builder()
    enriched_mappings = reader(basic_mappings, category_mappings)
    writer(enriched_mappings)