import streamlit as st
import pandas as pd
import numpy as np
import io

# =========================================================
# APP CONFIG & MAPPINGS
# =========================================================
st.set_page_config(page_title="LifeSciences DER Automation Tool", layout="wide")
st.title("🧬 LifeSciences DER Automation Tool")

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
    "men_b_acwy_abcwy_16_18", "men_acwy_abcwy_16_18", "men_b_16_18", "men_acwy_16_18",
    "men_abcwy_16_18", "paxlovid", "shingles_actual", "shingles_ls", 
    "men_acwy_actual", "men_b_actual", "men_b_ls"
]

# =========================================================
# CORE LOGIC
# =========================================================

def get_vaccine_sort_key(col_name):
    col_lower = col_name.lower()
    for index, pattern in enumerate(VACCINE_ORDER_PATTERNS):
        if pattern in col_lower:
            # Denominators (starts with den_ or count_) sorted before Numerators (starts with num_)
            is_den = 0 if (col_lower.startswith("den_") or col_lower.startswith("count_")) else 1
            return (index, is_den, col_name)
    return (999, 0, col_name)

def process_file_universal(f, mode):
    """Handles both Long (SQL export) and Wide (Standard) CSV formats."""
    try:
        df = pd.read_csv(f).fillna(0)
    except:
        return pd.DataFrame()
    
    is_provider_mode = (mode == "provider type + contact")

    # --- CASE A: LONG FORMAT (provider_type, metric, value, customer) ---
    if {'provider_type', 'metric', 'value', 'customer'}.issubset(df.columns):
        rows = []
        for _, row in df.iterrows():
            m_str, pt_raw, val, cust = str(row['metric']), str(row['provider_type']), row['value'], row['customer']
            
            # Find category and base metric name
            found_cat, base_m = None, None
            for cat_name, suffix in CATEGORY_CONFIG.items():
                if m_str.lower().endswith(suffix):
                    found_cat = cat_name
                    base_m = m_str[:-len(suffix)]
                    break
            if not found_cat: continue
            
            # Extract Provider Type (e.g., den_HPV_9_17_employed -> employed)
            p_type = pt_raw
            if pt_raw.lower().startswith(base_m.lower()):
                p_type = pt_raw[len(base_m):].strip("_")
            
            entry = {'customer': cust, 'Category': found_cat, base_m: val}
            if is_provider_mode:
                entry['Provider Type'] = p_type.title()
            rows.append(entry)
        
        long_df = pd.DataFrame(rows)
        if long_df.empty: return long_df
        
        group_keys = ['customer', 'Category']
        if is_provider_mode: group_keys.append('Provider Type')
        
        metric_cols = [c for c in long_df.columns if c not in group_keys]
        return long_df.groupby(group_keys, as_index=False)[metric_cols].sum()

    # --- CASE B: WIDE FORMAT ---
    total_suffix = CATEGORY_CONFIG["Total"]
    base_metrics = [c.replace(total_suffix, "") for c in df.columns if c.endswith(total_suffix)]
    
    if not base_metrics:
        exclude = ["customer", "Health System Name", "prid", "prnm", "plid", "plnm", "Provider Type"]
        base_metrics = [c for c in df.select_dtypes(include="number").columns if c not in exclude]
    
    if not base_metrics: return pd.DataFrame()

    all_cat_chunks = []
    for category in CATEGORY_ORDER:
        suffix = CATEGORY_CONFIG[category]
        temp = df.copy()
        temp["Category"] = category
        for m in base_metrics:
            src = m + suffix
            if src in df.columns: temp[m] = df[src]
            elif category == "Total" and m in df.columns: temp[m] = df[m]
            else: temp[m] = 0
        all_cat_chunks.append(temp)
    
    df_expanded = pd.concat(all_cat_chunks, ignore_index=True)
    
    group_keys = ["customer", "Category"]
    if is_provider_mode:
        if "plnm" in df_expanded.columns:
            df_expanded = df_expanded.rename(columns={"plnm": "Provider Type"})
        if "Provider Type" not in df_expanded.columns:
            df_expanded["Provider Type"] = "All"
        group_keys.append("Provider Type")
        
    return df_expanded.groupby(group_keys, as_index=False)[base_metrics].sum()

# =========================================================
# STREAMLIT UI
# =========================================================

app_choice = st.selectbox("Choose an operation", ["DER ZIP Data Compiler", "DER JSON Creator"])
st.divider()

if app_choice == "DER ZIP Data Compiler":
    mode = st.selectbox("Select processing mode", [
        "Contact Validity Compilation", 
        "provider type + contact",
        "Aggregated (Customer level)", 
        "Use this for more than 2 columns"
    ])
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("Compiling data..."):
            if mode in ["Contact Validity Compilation", "provider type + contact"]:
                processed_dfs = [process_file_universal(f, mode) for f in uploaded_files]
                processed_dfs = [d for d in processed_dfs if not d.empty]
                
                if processed_dfs:
                    # Merge all files
                    final_df = pd.concat(processed_dfs, ignore_index=True)
                    group_cols = ["customer", "Category"]
                    if mode == "provider type + contact": group_cols.append("Provider Type")
                    
                    final_df = final_df.groupby(group_cols, as_index=False).sum()
                    
                    # Mapping & Sorting
                    final_df.insert(1, "Health System Name", final_df["customer"].map(MAPPING).fillna(""))
                    final_df["Category"] = pd.Categorical(final_df["Category"], categories=CATEGORY_ORDER, ordered=True)
                    final_df = final_df.sort_values(group_cols)
                    
                    # Reorder columns (ID cols first, then sorted metrics)
                    id_cols = ["customer", "Health System Name"]
                    if mode == "provider type + contact": id_cols.append("Provider Type")
                    id_cols.append("Category")
                    
                    metrics = [c for c in final_df.columns if c not in id_cols]
                    sorted_metrics = sorted(metrics, key=get_vaccine_sort_key)
                    final_df = final_df[id_cols + sorted_metrics]
                    
                    st.success("Compilation Successful.")
                    st.dataframe(final_df, use_container_width=True)
                    st.download_button("⬇️ Download Compiled CSV", final_df.to_csv(index=False), "compiled_der_data.csv")

            elif mode == "Aggregated (Customer level)":
                # Simple sum by customer for wide files
                master_df = pd.concat([pd.read_csv(f) for f in uploaded_files]).fillna(0)
                nums = master_df.select_dtypes(include="number").columns
                master_df = master_df.groupby("customer", as_index=False)[nums].sum()
                master_df.insert(1, "Health System Name", master_df["customer"].map(MAPPING).fillna(""))
                st.dataframe(master_df)

            elif mode == "Use this for more than 2 columns":
                dfs = [pd.read_csv(f) for f in uploaded_files]
                final_df = dfs[0]
                for i in range(1, len(dfs)):
                    common = [c for c in final_df.columns if c in dfs[i].columns and not any(p in c.lower() for p in ["den_", "num_", "count_", "value"])]
                    final_df = pd.merge(final_df, dfs[i], on=common, how='outer').fillna(0)
                final_df.insert(1, "Health System Name", final_df["customer"].map(MAPPING).fillna(""))
                st.dataframe(final_df)

elif app_choice == "DER JSON Creator":
    st.info("Upload SQL files to generate the JSON report configuration.")
    uploaded_sql = st.file_uploader("Upload SQL files", type=["sql"], accept_multiple_files=True)
    if uploaded_sql:
        reports = []
        for f in uploaded_sql:
            content = f.read().decode("utf-8")
            slug = f.name.replace(".sql", "")
            reports.append({
                "slug": slug,
                "name": slug.replace("_", " ").title(),
                "query": content
            })
        st.json({"reports": reports})
