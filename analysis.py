import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.colors as mcolors
import matplotlib.cm as cm

def load_data():
    """
    Load datasets from CSV files.

    Returns
    -------
    tuple of pandas.DataFrame
        df_households : Household-level information dataset.
        df_expenses : Household expenditure dataset.
        df_products : Product classification dataset.
    """
    df_households = pd.read_csv('data_package/households.csv')
    df_expenses = pd.read_csv('data_package/expenses.csv')
    df_products = pd.read_csv('data_package/products.csv')
    return df_households, df_expenses, df_products

def sanity_check(df_households, df_expenses, df_products):
    """
    Perform a sanity check to verify if all households in the household dataset exist in the expenses dataset.
    Also, check for missing (NaN) values in all datasets and report the specific columns containing NaN values.

    Parameters
    ----------
    df_households : pandas.DataFrame
        Household-level dataset.
    df_expenses : pandas.DataFrame
        Household expenditure dataset.
    df_products : pandas.DataFrame
        Product classification dataset.

    Returns
    -------
    str
        Message confirming if all households have expenses recorded and if datasets contain NaN values.
    """
    household_ids = set(df_households['hh_id'])
    expense_ids = set(df_expenses['hh_id'])
    print("...................................sanity Check...........................\n")
    if household_ids.issubset(expense_ids):
        print(f"Yes, every household ({len(household_ids)}) has expenses recorded.")
    else:
        print("Warning: Some households do not have recorded expenses.")

    # Check for NaN values in all datasets and report the specific columns
    for df_name, df in zip(["households", "expenses", "products"], [df_households, df_expenses, df_products]):
        nan_columns = df.columns[df.isnull().any()].tolist()
        if nan_columns:
            print(f"Warning: Missing values detected in {df_name} dataset in columns: {nan_columns}")

def compute_national_share(df_households, df_expenses, df_products):
    """
    Calculate the national share of spending by COICOP Level 1 categories.

    Parameters
    ----------
    df_households : pandas.DataFrame
        Household-level dataset containing weights.
    df_expenses : pandas.DataFrame
        Household expenditure dataset.
    df_products : pandas.DataFrame
        Product classification dataset.

    Returns
    -------
    pandas.DataFrame
        National expenditure share for each COICOP Level 1 category.
    """
    # Mapping COICOP Level 1 codes to category names
    coicop_mapping = {
        '1': 'FOOD AND NON-ALCOHOLIC BEVERAGES',
        '2': 'ALCOHOLIC BEVERAGES, TOBACCO AND NARCOTICS',
        '3': 'CLOTHING AND FOOTWEAR',
        '4': 'HOUSING, WATER, ELECTRICITY, GAS AND OTHER FUELS',
        '5': 'FURNISHINGS, HOUSEHOLD EQUIPMENT AND ROUTINE HOUSEHOLD MAINTENANCE',
        '6': 'HEALTH',
        '7': 'TRANSPORT',
        '8': 'COMMUNICATION',
        '9': 'RECREATION AND CULTURE',
        '10': 'EDUCATION',
        '11': 'RESTAURANTS AND HOTELS',
        '12': 'MISCELLANEOUS GOODS AND SERVICES'
    }
    # Merge expenses with product and household datasets
    df_expenses = df_expenses.merge(df_products, on='product_id')
    df_expenses = df_expenses.merge(df_households[['hh_id', 'weight']], on='hh_id')

    # Map COICOP Level 1 codes to category names
    df_expenses['coicop_category'] = df_expenses['coicop_survey_1'].astype(str).map(coicop_mapping)

    # Calculate weighted expenditure
    df_expenses['weighted_expenditure'] = df_expenses['annual_expenditure'] * df_expenses['weight']

    # Aggregate expenditure at COICOP Level 1 and comput the share
    df_national_expenditure = df_expenses.groupby('coicop_category')['weighted_expenditure'].sum()
    total_expenditure = df_national_expenditure.sum()
    df_national_share = (df_national_expenditure / total_expenditure) * 100

    # Convert to DataFrame
    df_national_share = df_national_share.reset_index()
    df_national_share.columns = ['Category', 'Share (%)']
    df_national_share['Share (%)'] = df_national_share['Share (%)'].round(2)

    # Save output to file
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    df_national_share.to_csv(f"{output_dir}/national_share.csv", index=False)

    print("National Share of Spending by COICOP Level 1:")
    print(df_national_share)

def compute_lorenz_curve_and_gini(df_households, df_expenses):
    """
    Compute and plot the Lorenz curve and calculate the Gini coefficient.

    Parameters
    ----------
    df_households : pandas.DataFrame
        Household-level dataset containing weights and household sizes.
    df_expenses : pandas.DataFrame
        Household expenditure dataset.

    Returns
    -------
    float
        The Gini coefficient representing income inequality.
    """
    # Calculate total household expenditure
    total_expenditure = df_expenses.groupby("hh_id")["annual_expenditure"].sum().reset_index()
    total_expenditure = total_expenditure.merge(df_households, on="hh_id")

    # Calculate per capita expenditure
    total_expenditure["per_capita_expenditure"] =  total_expenditure["annual_expenditure"] / total_expenditure["hh_size"]

    # Sort households by per capita expenditure
    total_expenditure = total_expenditure.sort_values("per_capita_expenditure")

    # Compute cumulative population share and expenditure share
    total_expenditure["cum_pop"] = np.cumsum(total_expenditure["hh_size"] * total_expenditure["weight"] / np.sum(total_expenditure["hh_size"] * total_expenditure["weight"]))
    total_expenditure["cum_exp"] = np.cumsum(total_expenditure["annual_expenditure"]*total_expenditure["weight"]/ np.sum(total_expenditure["annual_expenditure"]*total_expenditure["weight"]))
    
    #compute 50% percentile
    nearest_fifty = np.argmin(np.abs(total_expenditure["cum_pop"] - 0.5))
    fifty_percentile_share =(100* total_expenditure["cum_exp"].values[nearest_fifty]).round(2)
    print(f"The bottom 50% of the population contributes a {fifty_percentile_share}% of the total expenditure")

    # Plot Lorenz Curve
    plt.figure(figsize=(6, 6))
    plt.plot(total_expenditure["cum_pop"], total_expenditure["cum_exp"], label="Lorenz Curve")
    plt.plot([0, 1], [0, 1], linestyle="--", color="black")
    plt.tick_params(axis='y', which='both', labelleft=False, labelright=True, reset=True, left=False)
    plt.xlabel("Cumulative Population Share")
    plt.ylabel("Cumulative Expenditure Share",labelpad=-400)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)

    
    plt.savefig("output/lorenz_curve.png", bbox_inches="tight", dpi=300)
    plt.show()
    plt.close()
    
    # Compute Gini Coefficient
    lorenz_x = total_expenditure["cum_pop"].values
    lorenz_y = total_expenditure["cum_exp"].values
    gini = 1 - 2 * np.trapezoid(lorenz_y, lorenz_x) # (0.5 - np.trapezoid(lorenz_y, lorenz_x))/0.5
    print(f"\nGini Coefficient: {gini:.4f}")

if __name__ == "__main__":
    # Load datasets
    df_households, df_expenses, df_products = load_data()
    
    #sanity check
    sanity_check(df_households, df_expenses, df_products)

    #comput national share of expenditure by product
    compute_national_share(df_households, df_expenses, df_products)

    #draw lorenz curve, calculate the gini coef
    compute_lorenz_curve_and_gini(df_households, df_expenses)
