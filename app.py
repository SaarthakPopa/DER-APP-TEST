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

# Sidebar for global settings
st.sidebar.header("Global Settings")
map_unknown = st.sidebar.checkbox("Show 'Unknown' for missing mappings", value=True)

app_choice = st.selectbox(
    "Choose an operation",
    ["DER ZIP Data Compiler", "DER JSON Creator"]
)

st.divider()

# =========================================================
# ---------------- HEALTH SYSTEM MAPPING -------------------
# =========================================================
# (Mapping dictionary remains the same as provided)
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

# =========================================================
# ---------------- CONFIG FOR ORDERING --------------------
# =========================================================
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
# ---------------- HELPER FUNCTIONS -----------------------
# =========================================================

def get_vaccine_sort_key(col_name):
    col_lower = col_name.lower()
    for index, pattern in enumerate(VACCINE_ORDER_PATTERNS):
        if pattern in col_lower:
            is_den = 0 if (col_lower.startswith("den_") or "a_b_den" in col_lower) else 1
            return (index, is_den, col_name)
    return (999, 0, col_name)

def process_single_file_to_long(f):
    """Processes CSV into a standardized long format based on CATEGORY_ORDER."""
    try:
        df = pd.read_csv(f).fillna(0)
    except Exception as e:
        st.error(f"Error reading {f.name}: {e}")
        return pd.DataFrame()

    if "customer" not in df.columns:
        return pd.DataFrame()

    total_suffix = CATEGORY_CONFIG["Total"]
    # Identify the base metric names (e.g., den_hpv_9_17)
    base_metrics = [c.replace(total_suffix, "") for c in df.columns if c.endswith(total_suffix)]
    
    if not base_metrics:
        # Fallback for simple count files
        base_metrics = [c for c in df.select_dtypes(include="number").columns if c != "customer"]

    chunk_results = []
    for category in CATEGORY_ORDER:
        suffix = CATEGORY_CONFIG[category]
        temp = pd.DataFrame({"customer": df["customer"], "Category": category})
        for metric in base_metrics:
            src_col = metric + suffix
            if src_col in df.columns:
                temp[metric] = df[src_col]
            elif category == "Total" and metric in df.columns:
                temp[metric] = df[metric]
            else:
                temp[metric] = 0
        chunk_results.append(temp)
    
    del df
    return pd.concat(chunk_results, ignore_index=True)

def extract_metadata_from_sql(sql_content):
    """Simple parser for SQL file metadata tags."""
    meta = {}
    patterns = {
        "slug": r"--\s*slug:\s*([^\n]+)",
        "name": r"--\s*name:\s*([^\n]+)",
        "description": r"--\s*description:\s*([^\n]+)"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, sql_content, re.IGNORECASE)
        meta[key] = match.group(1).strip() if match else "N/A"
    return meta

# =========================================================
# ---------------- MAIN APP LOGIC -------------------------
# =========================================================

if app_choice == "DER ZIP Data Compiler":
    mode = st.selectbox("Select processing mode", [
        "Contact Validity Compilation", 
        "Aggregated (Customer level)", 
        "Outer Merge (Multi-column Join)"
    ])
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("Processing files..."):
            if mode == "Contact Validity Compilation":
                all_chunks = [process_single_file_to_long(f) for f in uploaded_files]
                all_chunks = [c for c in all_chunks if not c.empty]
                
                if all_chunks:
                    final_df = pd.concat(all_chunks, ignore_index=True).groupby(["customer", "Category"], as_index=False).sum()
                    final_df.insert(1, "Health System Name", final_df["customer"].map(MAPPING).fillna("Unknown" if map_unknown else ""))
                    final_df["Category"] = pd.Categorical(final_df["Category"], categories=CATEGORY_ORDER, ordered=True)
                    final_df = final_df.sort_values(["customer", "Category"])
                    
                    id_cols = ["customer", "Health System Name", "Category"]
                    metric_cols = [c for c in final_df.columns if c not in id_cols]
                    sorted_metrics = sorted(metric_cols, key=get_vaccine_sort_key)
                    final_df = final_df[id_cols + sorted_metrics]
                    
                    st.success("Data Compiled Successfully")
                    st.dataframe(final_df, use_container_width=True)
                    st.download_button("⬇️ Download Compiled CSV", final_df.to_csv(index=False), "compiled_data.csv")

            elif mode == "Aggregated (Customer level)":
                master_df = pd.concat([pd.read_csv(f) for f in uploaded_files]).fillna(0)
                numeric_cols = master_df.select_dtypes(include="number").columns
                master_df = master_df.groupby("customer", as_index=False)[numeric_cols].sum()
                master_df.insert(1, "Health System Name", master_df["customer"].map(MAPPING).fillna(""))
                st.dataframe(master_df)

            elif mode == "Outer Merge (Multi-column Join)":
                dfs = [pd.read_csv(f) for f in uploaded_files]
                final_df = dfs[0]
                for next_df in dfs[1:]:
                    common = [c for c in final_df.columns if c in next_df.columns and c in ["customer", "prid", "plid"]]
                    final_df = pd.merge(final_df, next_df, on=common, how='outer').fillna(0)
                
                final_df.insert(1, "Health System Name", final_df["customer"].map(MAPPING).fillna(""))
                st.dataframe(final_df)
        
        gc.collect()

elif app_choice == "DER JSON Creator":
    uploaded_files = st.file_uploader("Upload SQL files", type=["sql"], accept_multiple_files=True)
    if uploaded_files:
        json_output = {"reports": []}
        for f in uploaded_files:
            content = f.read().decode("utf-8")
            meta = extract_metadata_from_sql(content)
            json_output["reports"].append({
                "slug": meta["slug"],
                "name": meta["name"],
                "description": meta["description"],
                "query": content
            })
        
        st.json(json_output)
        st.download_button("⬇️ Download JSON", json.dumps(json_output, indent=4), "DER_Configuration.json")
