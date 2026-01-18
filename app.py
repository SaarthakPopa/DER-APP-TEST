import streamlit as st
import json
import re
import pandas as pd
from pandas.errors import EmptyDataError
import functools

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(page_title="LifeSciences DER Automation Tool", layout="wide")
st.title("🧬 LifeSciences DER Automation Tool")

app_choice = st.selectbox(
    "Choose an operation",
    ["DER JSON Creator", "DER ZIP Data Compiler"]
)

st.divider()

# =========================================================
# ---------------- HELPER: MEMORY OPTIMIZATION ------------
# =========================================================
def optimize_df(df):
    """Reduces memory usage by downcasting numeric types."""
    floats = df.select_dtypes(include=['float']).columns
    ints = df.select_dtypes(include=['int']).columns
    df[floats] = df[floats].apply(pd.to_numeric, downcast='float')
    df[ints] = df[ints].apply(pd.to_numeric, downcast='integer')
    return df

# =========================================================
# ---------------- APP 1 : DER JSON CREATOR ----------------
# =========================================================
def clean_sql_query(file):
    content = file.read().decode("utf-8")
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    content = re.sub(r"--.*?$", "", content, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", content).strip()

def create_final_json(uploaded_files):
    metrics = []
    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        cleaned_query = clean_sql_query(uploaded_file)
        metrics.append({
            "id": idx,
            "metric": f"DER_{uploaded_file.name}",
            "level": "l2",
            "supported_customers": {
                "included": [],
                "excluded": [
                    "kaiser-staging","kpphm-prod","kpphmi-prod",
                    "kpphmi-staging","kpwa-prod","kpwa-staging","jhah-prod"
                ]
            },
            "queries": {
                "snowflake": {"database": "DAP","schema": "L2","query": cleaned_query},
                "postgres": {"database": "postgres","schema": "l2","query": cleaned_query}
            }
        })
    return {"metrics": metrics}

# =========================================================
# ---------------- HEALTH SYSTEM MAPPING -------------------
# =========================================================
mapping = {
    'advantasure-prod': 'Advantasure (Env 1)',
    'advantasureapollo-prod': 'Advantasure (Env 2)',
    'adventist-prod': 'Adventist Healthcare',
    'alameda-prod': 'Alameda County',
    'alo-prod': 'Alo solutions',
    'arkansashealth-prod': 'Chi St Vincent',
    'ascension-preprod': 'Ascension Health (Env 1)',
    'ascension-prod': 'Ascension Health (Env 2)',
    'atlantichealth-prod': 'Atlantic Health',
    'bannerapollo-prod': 'Banner Health',
    'bhsf-prod': 'Baptist Health South Florida',
    'bsim-prod': 'BSIM Healthcare services',
    'careabout-prod': 'CareAbout Health',
    'ccmcn-prod': 'Colorado Community Managed Care Network',
    'ccnc-prod': 'Community Care of North Carolina',
    'chessapollo-prod': 'CHESS Health Solutions',
    'childrenshealthapollo-prod': 'Children Health Alliance',
    'christianacare-prod': 'Christiana Care Health System',
    'cmhcapollo-prod': 'Central Maine Healthcare',
    'cmicsapollo-prod': 'Childrens Mercy Hospital And Clinics',
    'coa-prod': 'Colorado Access',
    'concare-prod': 'ConcertoCare',
    'connecticutchildrens-prod': "Connecticut Children's Health",
    'cshnational-new-prod': 'CSH National (Env 1)',
    'cshnational-prod': 'CSH National (Env 2)',
    'curana-prod': 'Curana Health',
    'dhmsapollo-prod': 'Dignity Health',
    'dock-cmicsapollo-prod': 'Childrens Mercy Hospital And Clinics (Nexus)',
    'dock-embrightapollo-prod': 'Embright (Nexus)',
    'dock-nemoursapollo-prod': 'Nemours Childrens Health System (Nexus)',
    'dock-risehealth-prod': 'Rise Health (Nexus)',
    'dock-tccn-prod': 'Childrens Healthcare Of Atlanta (Nexus)',
    'embrightapollo-prod': 'Embright',
    'evergreen-prod': 'Evergreen Nephrology',
    'falliance-prod': 'Franciscan Health',
    'flmedicaid-prod': 'Florida Medicaid',
    'franciscan-staging': 'Franciscan Health (staging)',
    'govcloud-prod': 'govcloud-prod',
    'gravitydemo-prod': 'Gravity',
    'impacthealth-prod': 'Impact Primary Care Network/Impact Health',
    'innohumana-prod': 'Longevity Health Plan(LHP) - HUMANA',
    'innolhp-prod': 'Longevity Health Plan(LHP) - Core)',
    'innovaetna-prod': 'Longevity Health Plan(LHP) - Aetna',
    'integration-preprod': 'internal env',
    'integris-prod': 'integris-prod',
    'intjuly-prod': 'internal account',
    'longitudegvt-prod': 'LongitudeRx (Env 1)',
    'longituderx-prod': 'LongitudeRx (Env 2)',
    'mcs-prod': 'Medical Card System',
    'mercyoneapollo-prod': 'MercyOne',
    'mercypit-prod': 'Trinity Health Pittsburgh',
    'mgm-prod': 'Mgm Resorts',
    'mhcn-prod': 'Chi Memorial',
    'nemoursapollo-prod': 'Nemours Childrens Health System',
    'novanthealth-prod':'Novant Health',
    'nwm-prod': 'Northwestern Medicine',
    'orlandoapollo-prod': 'Orlando Health',
    'pedassoc-prod': 'Pediatric Associates',
    'phlc-prod': 'Population Health Learning Center',
    'php-prod': 'P3 Health Partners',
    'pophealthcare-prod': 'Emcara / POP Health / Guidewell Mutual Holding Company',
    'prismah-prod': 'Prisma Health',
    'pswapollo-prod': 'Physicians Of Southwest Washington',
    'risehealth-prod': 'Rise Health',
    'sacramento-prod': 'Sacramento SHIE (Env 1)',
    'sacramentoshie-prod': 'Sacramento SHIE (Env 2)',
    'sentara-prod': 'Sentara Health',
    'smch-prod': 'San Mateo County Health ',
    'stewardapollo-prod': 'Steward Health Care System',
    'strivehealth-prod': 'Strive Health',
    'tccn-prod': 'Childrens Healthcare Of Atlanta',
    'thnapollo-prod': 'Cone Health',
    'trinity-prod': 'Trinity Health National',
    'uninet-prod': 'CHI Health Partners',
    'usrc-prod': 'US RenalCare',
    'walgreens-prod': 'Walgreens',
    'champion-prod' : 'Champion Health Plan',
    'mdxhawaii-prod' : 'MDX Hawaii',
    'recuro-prod' : 'Recuro Health',
    'mhpartner-prod' : 'Mission Health Partners'
}

def add_health_system(df):
    df = df.copy()
    df.insert(1, "Health System Name", df["customer"].map(mapping).fillna(""))
    return df

# =========================================================
# -------- CONTACT VALIDITY (OPTIMIZED) --------------------
# =========================================================
CATEGORY_CONFIG = {
    "Total": "",
    "With Contact": "_patients_with_contact_number",
    "With Email": "_patients_with_email",
    "Only Contact": "_patients_with_only_contact",
    "Only Email": "_patients_with_only_email",
    "Both Contact and Email": "_patients_with_both_contact_and_email",
    "None Available": "_patients_with_neither_contact_nor_email"
}

CONTACT_SUFFIXES = (
    "_patients_with_contact_number",
    "_patients_with_email",
    "_patients_with_only_contact",
    "_patients_with_only_email",
    "_patients_with_both_contact_and_email",
    "_patients_with_neither_contact_nor_email"
)

def compile_contact_validity(df):
    """Vectorized compilation to avoid memory-heavy loops."""
    den_cols = [c for c in df.columns if c.startswith("den_")]
    num_cols = [c for c in df.columns if c.startswith("num_") and not c.endswith(CONTACT_SUFFIXES)]
    
    all_categories = []

    for category, suffix in CATEGORY_CONFIG.items():
        # Create a slice for this category
        cat_df = pd.DataFrame({"customer": df["customer"], "Category": category})
        
        # Denominators only appear in the 'Total' category
        for den in den_cols:
            cat_df[den] = df[den] if category == "Total" else 0
            
        # Numerators are pulled from suffixed columns
        for num in num_cols:
            col_source = num + suffix if suffix else num
            cat_df[num] = df[col_source] if col_source in df.columns else 0
            
        all_categories.append(cat_df)

    # Vertically stack all category dataframes
    result = pd.concat(all_categories, ignore_index=True)
    result = add_health_system(result)
    return result

def reorder_contact_validity_columns(df):
    fixed_cols = ["customer", "Health System Name", "Category"]
    den_cols = sorted([c for c in df.columns if c.startswith("den_")])
    num_cols = sorted([c for c in df.columns if c.startswith("num_")])

    ordered_metrics = []
    for den in den_cols:
        suffix = den.replace("den_", "")
        num = f"num_{suffix}"
        ordered_metrics.append(den)
        if num in num_cols:
            ordered_metrics.append(num)

    return df[fixed_cols + ordered_metrics]

# =========================================================
# ---------------- APP 2 : DER ZIP COMPILER ----------------
# =========================================================
if app_choice == "DER ZIP Data Compiler":

    mode = st.selectbox(
        "Select processing mode",
        ["Aggregated (Customer level)", "Use this for more than 2 columns", "Contact Validity Compilation"]
    )

    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        if mode == "Aggregated (Customer level)":
            # Optimized streaming concat
            df_list = []
            for f in uploaded_files:
                df_temp = optimize_df(pd.read_csv(f))
                df_list.append(df_temp)
            df = pd.concat(df_list, ignore_index=True)
            numeric_cols = df.select_dtypes(include="number").columns
            final_df = df.groupby("customer", as_index=False)[numeric_cols].sum()
            final_df = add_health_system(final_df)
            st.dataframe(final_df, use_container_width=True)

        elif mode == "Use this for more than 2 columns":
            df = pd.concat((optimize_df(pd.read_csv(f)) for f in uploaded_files), ignore_index=True)
            df = add_health_system(df)
            st.dataframe(df, use_container_width=True)

        elif mode == "Contact Validity Compilation":
            merged_df = None
            
            with st.spinner("Merging large file set..."):
                for f in uploaded_files:
                    try:
                        # Set index to 'customer' immediately for memory-efficient joining
                        df_temp = pd.read_csv(f)
                        if df_temp.empty: continue
                        
                        df_temp = optimize_df(df_temp).set_index("customer")
                        
                        if merged_df is None:
                            merged_df = df_temp
                        else:
                            # Left-join/Outer-join on index is faster than merge on columns
                            merged_df = merged_df.join(df_temp, how="outer", rsuffix='_dup')
                            # Clean up potential duplicate columns from overlapping files
                            merged_df = merged_df.loc[:, ~merged_df.columns.str.endswith('_dup')]
                    except Exception as e:
                        st.error(f"Error in {f.name}: {e}")
                        continue

            if merged_df is not None:
                merged_df = merged_df.reset_index().fillna(0)
                
                with st.spinner("Processing categories..."):
                    final_df = compile_contact_validity(merged_df)
                    final_df = reorder_contact_validity_columns(final_df)

                st.success(f"Successfully processed {len(uploaded_files)} files.")
                st.dataframe(final_df, use_container_width=True)

                st.download_button(
                    "⬇️ Download Final CSV",
                    final_df.to_csv(index=False),
                    "final_contact_validity.csv",
                    "text/csv"
                )

# =========================================================
# ---------------- APP 1 UI -------------------------------
# =========================================================
if app_choice == "DER JSON Creator":
    uploaded_files = st.file_uploader("Upload SQL files", type=["sql"], accept_multiple_files=True)

    if uploaded_files:
        final_json = create_final_json(uploaded_files)
        st.json(final_json)
        st.download_button(
            "⬇️ Download JSON",
            json.dumps(final_json, indent=4),
            "DER_JSON_FINAL.json",
            "application/json"
        )
