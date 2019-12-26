from datetime import datetime
import pandas as pd
import os
import calendar
import math

################
### BUILDERS ###
################

def month_mapping_builder():
    month_map = {}
    for month in range(1, 13):
        # month = datetime.strptime(str(i), '%m').strftime('%b')
        month_map[month] = {}
    print('[INFO] Finished building {month : {} } mapping.\n')
    return month_map


def expense_to_category_and_category_mapping_builder(exp_to_cat_filename='expToCatMapping.txt'):
    exp_to_cat_filename_with_path = 'src/' + exp_to_cat_filename

    categories = set()
    exp_to_cat_mapping = {}

    if os.path.exists(exp_to_cat_filename_with_path):
        df = pd.read_csv(exp_to_cat_filename_with_path, sep=':')
        for index, entry in df.iterrows():
            expense = entry[0]
            category = entry[1]

            # {category} set
            if category not in categories:
                categories.add(category)
            # {expense : category} mapping
            if expense not in exp_to_cat_mapping:
                exp_to_cat_mapping[expense] = category
    else:
        print('[DEBUG] Failed to find file', exp_to_cat_filename_with_path, '.\n')

    print('[INFO] Finished building {expense : category} mapping and {category : 0} mapping.\n')
    return categories, exp_to_cat_mapping


def builder():
    months_mapping = month_mapping_builder()
    categories, exp_to_cat_mapping = expense_to_category_and_category_mapping_builder()

    for month in months_mapping.keys():
        months_mapping[month] = {}
        for category in categories:
            months_mapping[month][category] = 0
    print('[INFO] Finished building {month_name : {category : 0} } mapping, categories set, {expense : category} mapping.\n')
    return months_mapping, categories, exp_to_cat_mapping


###############
### HELPERS ###
###############

def prompt_for_cols(filename, headers=None):
    print('Given the following headers in the file', filename, '\n', headers)
    exp_name = input('Which column should be used for the expense name? ')
    exp_amount = input('Which column should be used for the expense amount? ')
    exp_date = input('Which column should be used for the expense date? ')
    return exp_name, exp_amount, exp_date


def list_files(path=''):
    print('\nThere are the following files in the data/ directory.')
    print(os.listdir(path))
    bank_filename = path + input('What is the name of the file containing your data? ')
    rows_to_skip = int(input('How many rows, if any, should be skipped to obtain the headers of your file? '))
    return bank_filename, rows_to_skip


def update_monthly_mappings(df, name, amount, date, updated_mappings, categories, exp_to_cat_mapping):

    for index, row in df.iterrows():
        row = df.loc[index]
        exp_name = row[name]
        exp_amount = row[amount] * -1   # values in banking records are shown (properly) as negatives
        exp_month = row[date].month

        print()
        print(index, exp_name, exp_amount, exp_month, sep='\t')
        print()

        if math.isnan(exp_amount):
            print('[INFO] Skipping update.', exp_name, 'has an amount with value NaN.')
        elif exp_name in exp_to_cat_mapping:
            exp_category = exp_to_cat_mapping[exp_name]
            updated_mappings[exp_month][exp_category] += exp_amount
            print('[INFO] autoupdate amount.')
        else:
            print('Categories are:',updated_mappings[exp_month].keys())
            exp_category = input('Category for [' + exp_name + "] [from above list, enter a new one, or 'n' to ignore]: ")
            if not exp_category.__eq__('skip'):
                exp_to_cat_mapping[exp_name] = exp_category
                if exp_category not in updated_mappings[exp_month]:
                    updated_mappings[exp_month][exp_category] = 0
                updated_mappings[exp_month][exp_category] += exp_amount
                print(
                    '[INFO] Updated {month : {category : $} } mapping for month: ['
                    + str(exp_month) + '] category: ['
                    + exp_category + '] amount: ['
                    + str(exp_amount) + ']'
                    + ' -> New total: ['
                    + str(updated_mappings[exp_month][exp_category]) + ']'
                )
            else:
                print("[INFO] Skipping update. Option 'skip' input. ")
    return updated_mappings, exp_to_cat_mapping


###############
### READERS ###
###############

def reader(month_cat_amt_mapping, categories, exp_to_cat_mapping):
    # TODO: make date column selectable PRIOR to read_csv NOT after
    # TODO: Explore potential to wrap all reader functions into loop
    # TODO: Enable reading in 'Credit' column on credit card statement to illuminate returns/payments
    # updated_mapping, exp_to_cat_mapping = bank_reader(basic_mapping, categories, exp_to_cat_mapping)
    # updated_mapping, exp_to_cat_mapping = credit_card_reader(basic_mapping, categories, exp_to_cat_mapping)
    # updated_mapping, exp_to_cat_mapping = rent_and_utility_reader(basic_mapping, categories, exp_to_cat_mapping)

    num_files = int(input('How many files would you like to import? '))
    if num_files > 0:
        for i in range(num_files):
            filename, rows_to_skip = list_files('data/')
            df = pd.read_csv(filename, skiprows=rows_to_skip, parse_dates=['Date'])
            name, amount, date = prompt_for_cols(
                filename,
                df.keys()
            )
            month_cat_amt_mapping, exp_to_cat_mapping = update_monthly_mappings(
                df,
                name,
                amount,
                date,
                month_cat_amt_mapping,
                categories,
                exp_to_cat_mapping
            )
    print('[INFO] Finished reading all data.\n')
    return month_cat_amt_mapping, exp_to_cat_mapping


###############
### WRITERS ###
###############


def expense_to_category_writer(exp_to_cat_mapping, filename='expToCatMapping.txt'):
    filepath = 'src/' + filename
    with open(filepath, "w") as f:
        for expense, category in exp_to_cat_mapping.items():
            f.write(expense + ':' + category + '\n')
    print('[INFO] Finished writing {expense : category} mapping.\n')
    return


def enriched_mapping_writer(enriched_mapping, filename='budget_report'):
    current_date = datetime.now()
    current_month = current_date.strftime('%B').lower()
    current_year = current_date.year
    filepath = 'src/' + filename + '_' + current_month + '_' + str(current_year) + '.txt'
    with open(filepath, "w") as f:
        annual_total = 0
        for month, categories in enriched_mapping.items():
            f.write(calendar.month_name[month] + ':\n')
            month_total = 0
            for category, amt in categories.items():
                if not (category is 'income' or category is 'skip'):     # 'income' and 'n' categories are to be ignored ('n' is ignore)
                    month_total += amt
                    category_summary = '\t' + category + ': ' + str(round(amt, 2)) + '\n'
                    f.write(category_summary)
            annual_total += month_total
            month_summary = 'Total: $' + str(round(month_total, 2)) + '\n'
            f.write(month_summary)
        f.write('\nAnnual total: $' + str(round(annual_total, 2)))
    print('[INFO] Finished writing enriched {month_name : {category : $} } mapping data.\n')
    return


def writer(enriched_mapping, exp_to_cat_mapping):
    expense_to_category_writer(exp_to_cat_mapping)
    enriched_mapping_writer(enriched_mapping)

    print('[INFO] Finished writing all data.\n')
    return


if __name__ == '__main__':
    basic_mappings, category_set, expense_to_category_mapping = builder()
    enriched_mappings, expense_to_category_mapping = reader(basic_mappings, category_set, expense_to_category_mapping)
    writer(enriched_mappings, expense_to_category_mapping)