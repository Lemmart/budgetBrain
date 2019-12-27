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
        month_map[month] = {}
    print('[INFO] Finished building {month : {} } mapping.\n')
    return month_map


def expense_to_category_and_category_mapping_builder(exp_to_cat_filename='expToCatMapping.txt'):
    exp_to_cat_filename_with_path = 'src/' + exp_to_cat_filename

    categories = set()
    exp_to_cat_mapping = {}

    if os.path.exists(exp_to_cat_filename_with_path):
        with open(exp_to_cat_filename_with_path) as f:
            for line in f:
                entry = line.replace('"', '').replace('\n', '').split(':')
                entry = [0 if item == '' else item for item in entry]
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
    exp_name_backup = input('Which column should be used for the expense name if ' + exp_name + ' is empty? ')
    exp_amount = input('Which column should be used for the expense amount? ')
    exp_date = input('Which column should be used for the expense date? ')
    return exp_name, exp_name_backup, exp_amount, exp_date


def list_files(read_files, path=''):
    if len(read_files) > 0:
        print('\nThe following files have already been processed:', read_files)
    print('\nThe following files exist in the directory: data/')
    print(os.listdir(path))
    bank_filename = path + input('What is the name of the file containing your data? ')
    rows_to_skip = int(input('How many rows, if any, should be skipped to obtain the headers of your file? '))
    # Assumption: user properly enters 'y' or 'n'
    amts_are_neg = input('Are expenses listed as negatives in this file? (y/n): ')
    exp_amts_are_neg = False
    if amts_are_neg.__contains__('y'):
        exp_amts_are_neg = True

    return bank_filename, rows_to_skip, exp_amts_are_neg


def validate_exp_name(exp_name, name, name_backup, row, keys):
    if not type(exp_name) == str and math.isnan(exp_name):
        print('\n[Error] The column', name, 'is empty for entry', row)
        print(keys)
        tmp_name = input('Which column should be used for the expense name? ')
        if len(tmp_name) < 2:
            tmp_name = name_backup
        exp_name = row[tmp_name].strip()
    else:
        exp_name = exp_name.strip()
    exp_name = exp_name.replace(':', '-')
    return exp_name


def update_monthly_mappings(df, name, name_backup, amount, date, updated_mappings, exp_to_cat_mapping, exp_amts_are_neg):
    keys = df.keys()

    for index, row in df.iterrows():
        row = df.loc[index]
        exp_name = validate_exp_name(row[name], name, name_backup, row, keys)
        exp_amount = row[amount]
        if not exp_amts_are_neg:
            exp_amount *= -1
        print(row[date])

        exp_month = row[date].month

        print('\n', index, exp_name, exp_amount, exp_month, '\n', sep='\t')

        if math.isnan(exp_amount):
            print('[INFO] Skipping update.', exp_name, 'has an amount with value NaN.')
        elif exp_name in exp_to_cat_mapping:
            exp_category = exp_to_cat_mapping[exp_name]
            if exp_category not in updated_mappings[exp_month]:
                updated_mappings[exp_month][exp_category] = 0
            updated_mappings[exp_month][exp_category] += exp_amount
            print('[INFO] Autoupdate amount for', exp_name, 'in', exp_category, 'category.')
        else:
            print('Categories are:', updated_mappings[exp_month].keys())
            exp_category = input('Category for [' + exp_name + "] [from above list, enter a new one, or 'skip' to ignore]: ")

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
    return updated_mappings, exp_to_cat_mapping


###############
### READERS ###
###############

def reader(month_cat_amt_mapping, exp_to_cat_mapping):
    # TODO: make date column selectable PRIOR to read_csv NOT after
    # TODO: Enable reading in 'Credit' column on credit card statement to illuminate returns/payments

    read_files = []
    num_files = int(input('How many files would you like to import? '))
    if num_files > 0:
        for i in range(num_files):
            filename, rows_to_skip, exp_amts_are_neg = list_files(read_files, 'data/')
            read_files.append(filename)
            df = pd.read_csv(filename, skiprows=rows_to_skip, parse_dates=['Date'])
            name, name_backup, amount, date = prompt_for_cols(
                filename,
                df.keys()
            )
            month_cat_amt_mapping, exp_to_cat_mapping = update_monthly_mappings(
                df,
                name,
                name_backup,
                amount,
                date,
                month_cat_amt_mapping,
                exp_to_cat_mapping,
                exp_amts_are_neg
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
        annual_expenses = 0
        annual_income = 0
        for month, categories in enriched_mapping.items():
            f.write(calendar.month_name[month] + ':\n')
            monthly_expenses = 0
            monthly_income = 0
            for category, amt in categories.items():
                if category == 'income':
                    monthly_income += amt
                    annual_income += amt
                elif not category == 'skip':     # 'income' and 'n' categories are to be ignored ('n' is ignore)
                    monthly_expenses += amt
                category_summary = '\t' + category + ': ' + str(round(amt, 2)) + '\n'
                f.write(category_summary)
            annual_expenses += monthly_expenses
            monthly_expenses_summary = 'Total monthly expenses: $' + str(round(monthly_expenses, 2)) + '\n'
            f.write(monthly_expenses_summary)

            if 'income' in enriched_mapping[month]:
                income_summary = 'Total monthly income: $' + str(round(monthly_income, 2)) + '\n'
                net_income = round(enriched_mapping[month]['income'] + monthly_expenses, 2)
                net_income_summary = 'Net monthly income: $' + str(net_income) + '\n'
                f.write(income_summary)
                f.write(net_income_summary)

        f.write('\nTotal annual expenses: $' + str(round(annual_expenses, 2)))
        f.write('\nTotal annual income: $' + str(round(annual_income, 2)))
        f.write('\nTotal net income: $' + str(round(annual_income + annual_expenses, 2)))
    print('[INFO] Finished writing enriched {month_name : {category : $} } mapping data.\n')
    return


def writer(enriched_mapping, exp_to_cat_mapping):
    expense_to_category_writer(exp_to_cat_mapping)
    enriched_mapping_writer(enriched_mapping)

    print('[INFO] Finished writing all data.\n')
    return


if __name__ == '__main__':
    basic_mappings, category_set, expense_to_category_mapping = builder()
    enriched_mappings, expense_to_category_mapping = reader(basic_mappings, expense_to_category_mapping)
    writer(enriched_mappings, expense_to_category_mapping)