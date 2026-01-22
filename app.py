import streamlit as st
import json
import re
import pandas as pd
import gc

# =========================================================
# APP CONFIG
# =========================================================
st.set_page_config(page_title="LifeSciences DER Automation Tool", layout="wide")
st.title("🧬 LifeSciences DER Automation Tool")

app_choice = st.selectbox(
    "Choose an operation",
    ["DER ZIP Data Compiler", "DER JSON Creator"]
)

st.divider()

# =========================================================
# ---------------- HEALTH SYSTEM MAPPING -------------------
# =========================================================
MAPPING = {
    'advantasure-prod': 'Advantasure (Env 1)', 'advantasureapollo-prod': 'Advantasure (Env 2)',
    'adventist-prod': 'Adventist Healthcare', 'alameda-prod': 'Alameda County',
    'alo-prod': 'Alo solutions', 'arkansashealth-prod': 'Chi St Vincent',
    'ascension-preprod': 'Ascension Health (Env 1)', 'ascension-prod': 'Ascension Health (Env 2)',
    'atlantichealth-prod': 'Atlantic Health', 'bannerapollo-prod': 'Banner Health',
    'bhsf-prod': 'Baptist Health South Florida', 'bsim-prod': 'BSIM Healthcare services',
    'careabout-prod': 'CareAbout Health', 'ccmcn-prod': 'Colorado Community Managed Care Network',
    'ccnc-prod': 'Community Care of North Carolina', 'chessapollo-prod': 'CHESS Health Solutions',
    'childrenshealthapollo-prod': 'Children Health Alliance', 'christianacare-prod': 'Christiana Care Health System',
    'cmhcapollo-prod': 'Central Maine Healthcare', 'cmicsapollo-prod': 'Childrens Mercy Hospital And Clinics',
    'coa-prod': 'Colorado Access', 'concare-prod': 'ConcertoCare',
    'connecticutchildrens-prod': "Connecticut Children's Health", 'cshnational-new-prod': 'CSH National (Env 1)',
    'cshnational-prod': 'CSH National (Env 2)', 'curana-prod': 'Curana Health',
    'dhmsapollo-prod': 'Dignity Health', 'dock-cmicsapollo-prod': 'Childrens Mercy Hospital And Clinics (Nexus)',
    'dock-embrightapollo-prod': 'Embright (Nexus)', 'dock-nemoursapollo-prod': 'Nemours Childrens Health System (Nexus)',
    'dock-risehealth-prod': 'Rise Health (Nexus)', 'dock-tccn-prod': 'Childrens Healthcare Of Atlanta (Nexus)',
    'embrightapollo-prod': 'Embright', 'evergreen-prod': 'Evergreen Nephrology',
    'falliance-prod': 'Franciscan Health', 'flmedicaid-prod': 'Florida Medicaid',
    'franciscan-staging': 'Franciscan Health (staging)', 'govcloud-prod': 'govcloud-prod',
    'gravitydemo-prod': 'Gravity', 'impacthealth-prod': 'Impact Primary Care Network/Impact Health',
    'innohumana-prod': 'Longevity Health Plan(LHP) - HUMANA', 'innolhp-prod': 'Longevity Health Plan(LHP) - Core)',
    'innovaetna-prod': 'Longevity Health Plan(LHP) - Aetna', 'integration-preprod': 'internal env',
    'integris-prod': 'integris-prod', 'intjuly-prod': 'internal account',
    'longitudegvt-prod': 'LongitudeRx (Env 1)', 'longituderx-prod': 'LongitudeRx (Env 2)',
    'mcs-prod': 'Medical Card System', 'mercyoneapollo-prod': 'MercyOne',
    'mercypit-prod': 'Trinity Health Pittsburgh', 'mgm-prod': 'Mgm Resorts',
    'mhcn-prod': 'Chi Memorial', 'nemoursapollo-prod': 'Nemours Childrens Health System',
    'novanthealth-prod':'Novant Health', 'nwm-prod': 'Northwestern Medicine',
    'orlandoapollo-prod': 'Orlando Health', 'pedassoc-prod': 'Pediatric Associates',
    'phlc-prod': 'Population Health Learning Center', 'php-prod': 'P3 Health Partners',
    'pophealthcare-prod': 'Emcara / POP Health / Guidewell Mutual Holding Company',
    'prismah-prod': 'Prisma Health', 'pswapollo-prod': 'Physicians Of Southwest Washington',
    'risehealth-prod': 'Rise Health', 'sacramento-prod': 'Sacramento SHIE (Env 1)',
    'sacramentoshie-prod': 'Sacramento SHIE (Env 2)', 'sentara-prod': 'Sentara Health',
    'smch-prod': 'San Mateo County Health ', 'stewardapollo-prod': 'Steward Health Care System',
    'strivehealth-prod': 'Strive Health', 'tccn-prod': 'Childrens Healthcare Of Atlanta',
    'thnapollo-prod': 'Cone Health', 'trinity-prod': 'Trinity Health National',
    'uninet-prod': 'CHI Health Partners', 'usrc-prod': 'US RenalCare',
    'walgreens-prod': 'Walgreens', 'champion-prod' : 'Champion Health Plan',
    'mdxhawaii-prod' : 'MDX Hawaii', 'recuro-prod' : 'Recuro Health',
    'mhpartner-prod' : 'Mission Health Partners', 'dock-olyortho-prod' : 'Oly Ortho (Nexus)'
}

CATEGORY_ORDER = ["Total", "With Telephone", "With Email", "With only Telephone", "With only Email", "With Both Telephone and Email", "None"]

CATEGORY_CONFIG = {
    "Total": "_patients_total", 
    "With Telephone": "_patients_with_contact_number", 
    "With Email": "_patients_with_email", 
    "With only Telephone": "_patients_with_only_contact", 
    "With only Email": "_patients_with_only_email", 
    "With Both Telephone and Email": "_patients_with_both_contact_and_email", 
    "None": "_patients_with_neither_contact_nor_email"
}

VACCINE_ORDER_PATTERNS = [
    "total_attributed_lives", "age_16", "age_50", "age_analysis", 
    "hpv_9_17", "shingles_50_59", "shingles_60_64", "shingles_65_plus",
    "rsv_covid_60_64", "rsv_covid_65_74", "rsv_covid_75_plus",
    "pneumococcal_50_plus", "pneumococcal_50_64", "pneumococcal_65_plus",
    "influenza_50_plus", "covid_65_plus", "rsv_60_plus",
    "men_b_acwy_abcwy_16_18", "men_b_acwy_abcwy_19_23",
    "men_acwy_abcwy_16_18", "men_acwy_abcwy_19_23",
    "men_b_16_18", "men_b_19_23", "men_acwy_16_18", "men_acwy_19_23",
    "men_abcwy_16_18", "men_abcwy_19_23", "paxlovid",
    "shingles_actual", "shingles_ls", "men_acwy_actual", "men_b_actual", "men_b_ls"
]

# =========================================================
# ---------------- HELPERS & LOGIC ------------------------
# =========================================================

def get_vaccine_sort_key(col_name):
    col_lower = col_name.lower()
    for index, pattern in enumerate(VACCINE_ORDER_PATTERNS):
        if pattern in col_lower:
            is_den = 0 if (col_lower.startswith("den_") or "den" in col_lower or "a_b_den" in col_lower) else 1
            return (index, is_den, col_name)
    return (999, 0, col_name)

def process_to_long(f, group_by_provider=False):
    """Processes CSV into a standardized long format."""
    try:
        df = pd.read_csv(f).fillna(0)
    except:
        return pd.DataFrame()

    total_suffix = CATEGORY_CONFIG["Total"]
    base_metrics = [c.replace(total_suffix, "") for c in df.columns if c.endswith(total_suffix)]
    
    if not base_metrics:
        exclude = ["customer", "Health System Name", "prid", "prnm", "plid", "plnm"]
        base_metrics = [c for c in df.select_dtypes(include="number").columns if c not in exclude]

    chunk_results = []
    # Identify group columns
    group_cols = ["customer"]
    if group_by_provider and "plnm" in df.columns:
        group_cols.append("plnm")

    for category in CATEGORY_ORDER:
        suffix = CATEGORY_CONFIG[category]
        temp = df[group_cols].copy()
        temp["Category"] = category
        
        for metric in base_metrics:
            src_col = metric + suffix
            if src_col in df.columns:
                temp[metric] = df[src_col]
            elif category == "Total" and metric in df.columns:
                temp[metric] = df[metric]
            else:
                temp[metric] = 0
        chunk_results.append(temp)
    
    return pd.concat(chunk_results, ignore_index=True)

# =========================================================
# ---------------- APP INTERFACE --------------------------
# =========================================================

if app_choice == "DER ZIP Data Compiler":
    mode = st.selectbox("Select processing mode", [
        "Contact Validity Compilation", 
        "provider type + contact",
        "Aggregated (Customer level)", 
        "Use this for more than 2 columns"
    ])
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("Processing..."):
            if mode in ["Contact Validity Compilation", "provider type + contact"]:
                is_provider_mode = (mode == "provider type + contact")
                all_chunks = [process_to_long(f, group_by_provider=is_provider_mode) for f in uploaded_files]
                all_chunks = [c for c in all_chunks if not c.empty]
                
                if all_chunks:
                    group_keys = ["customer", "plnm", "Category"] if is_provider_mode else ["customer", "Category"]
                    final_df = pd.concat(all_chunks, ignore_index=True).groupby(group_keys, as_index=False).sum()
                    
                    # Mapping and Sorting
                    final_df.insert(1, "Health System Name", final_df["customer"].map(MAPPING).fillna(""))
                    final_df["Category"] = pd.Categorical(final_df["Category"], categories=CATEGORY_ORDER, ordered=True)
                    
                    # Sort logic
                    sort_cols = ["customer", "plnm", "Category"] if is_provider_mode else ["customer", "Category"]
                    final_df = final_df.sort_values(sort_cols)

                    # Column ordering
                    id_cols = ["customer", "Health System Name"]
                    if is_provider_mode: id_cols.append("plnm")
                    id_cols.append("Category")
                    
                    metric_cols = [c for c in final_df.columns if c not in id_cols]
                    sorted_metrics = sorted(metric_cols, key=get_vaccine_sort_key)
                    
                    final_df = final_df[id_cols + sorted_metrics]
                    if is_provider_mode:
                        final_df = final_df.rename(columns={"plnm": "Provider Type"})

                    st.success("Compilation Complete.")
                    st.dataframe(final_df, use_container_width=True)
                    st.download_button("⬇️ Download CSV", final_df.to_csv(index=False), "compiled_data.csv")

            elif mode == "Aggregated (Customer level)":
                master_df = pd.concat([pd.read_csv(f) for f in uploaded_files]).fillna(0)
                nums = master_df.select_dtypes(include="number").columns
                master_df = master_df.groupby("customer", as_index=False)[nums].sum()
                master_df.insert(1, "Health System Name", master_df["customer"].map(MAPPING).fillna(""))
                st.dataframe(master_df)

            elif mode == "Use this for more than 2 columns":
                dfs = [pd.read_csv(f) for f in uploaded_files]
                final_df = dfs[0]
                for i in range(1, len(dfs)):
                    common = [c for c in final_df.columns if c in dfs[i].columns and not any(p in c for p in ["den_", "num_", "count_"])]
                    final_df = pd.merge(final_df, dfs[i], on=common, how='outer').fillna(0)
                
                final_df.insert(1, "Health System Name", final_df["customer"].map(MAPPING).fillna(""))
                st.dataframe(final_df)

elif app_choice == "DER JSON Creator":
    # (JSON Creator logic remains same as previous version)
    st.info("Upload SQL files to generate DER JSON configuration.")
    uploaded_sql = st.file_uploader("Upload SQL files", type=["sql"], accept_multiple_files=True)
    if uploaded_sql:
        reports = []
        for f in uploaded_sql:
            content = f.read().decode("utf-8")
            slug = f.name.replace(".sql", "")
            reports.append({"slug": slug, "name": slug.replace("_", " ").title(), "query": content})
        st.json({"reports": reports})
