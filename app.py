import streamlit as st
import json
import re
import pandas as pd
import gc
from pandas.errors import EmptyDataError

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
# ---------------- HEALTH SYSTEM MAPPING -------------------
# =========================================================
mapping = {
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
    'mhpartner-prod' : 'Mission Health Partners'
}

# =========================================================
# -------- CONTACT VALIDITY CONFIG & LOGIC ----------------
# =========================================================
# Updated categories and order per user request
CATEGORY_ORDER = [
    "Total", 
    "With Telephone", 
    "With Email", 
    "With only Telephone", 
    "With only Email", 
    "With Both Telephone and Email", 
    "None"
]

CATEGORY_CONFIG = {
    "Total": "", 
    "With Telephone": "_patients_with_contact_number",
    "With Email": "_patients_with_email", 
    "With only Telephone": "_patients_with_only_contact",
    "With only Email": "_patients_with_only_email", 
    "Both Telephone and Email": "_patients_with_both_contact_and_email",
    "None": "_patients_with_neither_contact_nor_email"
}

def process_single_file_to_long(f):
    """Processes file into long format and returns (df, dict_of_metrics_found)."""
    try:
        df = pd.read_csv(f).fillna(0)
    except Exception:
        return pd.DataFrame(), []

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    suffixes = [v for v in CATEGORY_CONFIG.values() if v != ""]
    base_metrics = [c for c in numeric_cols if not any(c.endswith(s) for s in suffixes)]
    
    # Extract DER number from filename for sorting
    der_match = re.search(r"DER_(\d+)", f.name)
    der_num = int(der_match.group(1)) if der_match else 9999
    metric_num_map = {m: der_num for m in base_metrics}

    chunk_results = []
    for category in CATEGORY_ORDER:
        suffix = CATEGORY_CONFIG[category]
        temp = pd.DataFrame({"customer": df["customer"], "Category": category})
        for metric in base_metrics:
            if category == "Total":
                temp[metric] = df[metric]
            else:
                src_col = metric + suffix
                temp[metric] = df[src_col] if src_col in df.columns else 0
        chunk_results.append(temp)
    
    return pd.concat(chunk_results, ignore_index=True), metric_num_map

# =========================================================
# ---------------- APP LOGIC ------------------------------
# =========================================================
if app_choice == "DER ZIP Data Compiler":
    mode = st.selectbox("Select processing mode", 
                        ["Contact Validity Compilation", "Aggregated (Customer level)", "Use this for more than 2 columns"])
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        if mode == "Contact Validity Compilation":
            all_chunks = []
            master_metric_map = {}
            progress_bar = st.progress(0)
            
            for i, f in enumerate(uploaded_files):
                processed_chunk, file_metrics = process_single_file_to_long(f)
                if not processed_chunk.empty:
                    all_chunks.append(processed_chunk)
                    master_metric_map.update(file_metrics)
                
                if len(all_chunks) >= 10:
                    combined = pd.concat(all_chunks, ignore_index=True)
                    all_chunks = [combined.groupby(["customer", "Category"], as_index=False).sum()]
                    gc.collect() 
                
                progress_bar.progress((i + 1) / len(uploaded_files))

            if all_chunks:
                final_df = pd.concat(all_chunks, ignore_index=True)
                final_df = final_df.groupby(["customer", "Category"], as_index=False).sum()
                
                # Apply Health System Name
                final_df.insert(1, "Health System Name", final_df["customer"].map(mapping).fillna(""))
                
                # Apply Category Sort Order
                final_df["Category"] = pd.Categorical(final_df["Category"], categories=CATEGORY_ORDER, ordered=True)
                final_df = final_df.sort_values(["customer", "Category"])

                # Handle Column Sorting by DER Number
                id_cols = ["customer", "Health System Name", "Category"]
                metrics_in_df = [c for c in final_df.columns if c not in id_cols]
                
                # Sort metrics: Primary by DER number, Secondary alphabetically
                sorted_metrics = sorted(metrics_in_df, key=lambda x: (master_metric_map.get(x, 9999), x))
                
                final_df = final_df[id_cols + sorted_metrics]
                
                st.success(f"Successfully processed {len(uploaded_files)} files!")
                st.dataframe(final_df, use_container_width=True)

                st.download_button(
                    "⬇️ Download Compiled CSV",
                    final_df.to_csv(index=False),
                    "compiled_contact_validity.csv",
                    "text/csv"
                )

       

        elif mode == "Aggregated (Customer level)":
            master_df = None
            for f in uploaded_files:
                df_temp = pd.read_csv(f)
                numeric_cols = df_temp.select_dtypes(include="number").columns
                chunk = df_temp.groupby("customer", as_index=False)[numeric_cols].sum()
                master_df = chunk if master_df is None else pd.concat([master_df, chunk]).groupby("customer", as_index=False).sum()
                gc.collect()
            
            master_df.insert(1, "Health System Name", master_df["customer"].map(mapping).fillna(""))
            st.dataframe(master_df, use_container_width=True)

        elif mode == "Use this for more than 2 columns":
            df = pd.concat((pd.read_csv(f) for f in uploaded_files), ignore_index=True)
            df.insert(1, "Health System Name", df["customer"].map(mapping).fillna(""))
            st.dataframe(df, use_container_width=True)


# =========================================================
# ---------------- APP 1 UI -------------------------------
# =========================================================
if app_choice == "DER JSON Creator":
    uploaded_files = st.file_uploader("Upload SQL files", type=["sql"], accept_multiple_files=True)
    if uploaded_files:
        final_json = create_final_json(uploaded_files)
        st.json(final_json)
        st.download_button("⬇️ Download JSON", json.dumps(final_json, indent=4), "DER_JSON_FINAL.json", "application/json")


