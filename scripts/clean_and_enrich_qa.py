#!/usr/bin/env python3
"""
Enrich and Clean Women's Health & Maternal Q&A Dataset for IVY App
Removes non-OB/GYN false positives and enriches with high-quality clinical queries.
"""

import os
import re
import pandas as pd

QA_PATH = "data/medical_qa/raw_womens_health_qa.csv"
CLEAN_QA_PATH = "data/medical_qa/clean_womens_health_qa.csv"

# Unwanted general disease keywords
EXCLUDE_TERMS = [
    "rocky mountain", "marine toxin", "lice", "marburg", "ebola", "chronic fatigue",
    "cerebral atrophy", "shingles", "anthrax", "rabies", "lyme", "salmonella",
    "cholera", "plague", "tuberculosis", "leprosy", "meningitis", "tularemia"
]

# Required relevant keywords
INCLUSION_TERMS = [
    "pregnan", "period", "menstru", "ovulat", "cramp", "bleeding", "spotting",
    "hcg", "ultrasound", "trimester", "ttc", "fertility", "cervical", "nausea",
    "morning sickness", "fetal", "baby", "miscarriage", "gestational", "pcos",
    "contracepti", "birth control", "luteal", "folic acid", "braxton hicks",
    "vagina", "uterus", "ovary", "endometriosis", "pap smear", "conception"
]

def clean_data():
    df = pd.read_csv(QA_PATH)
    cleaned_rows = []
    
    for _, row in df.iterrows():
        text = (str(row["question"]) + " " + str(row["answer"])).lower()
        
        # Check exclusion
        if any(term in text for term in EXCLUDE_TERMS):
            continue
            
        # Check inclusion
        if not any(term in text for term in INCLUSION_TERMS):
            continue
            
        cleaned_rows.append(row)
        
    df_clean = pd.DataFrame(cleaned_rows)
    
    # Add curated clinical benchmark cases
    curated_cases = [
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "PREGNANCY",
            "question": "Is extreme nausea and vomiting at 9 weeks hyperemesis gravidarum or normal morning sickness?",
            "answer": "Normal morning sickness involves mild to moderate nausea with occasional vomiting. Hyperemesis gravidarum (HG) is diagnosed when severe vomiting leads to dehydration, electrolyte imbalance, ketonuria, and weight loss exceeding 5% of pre-pregnancy weight. Seek immediate evaluation for IV rehydration and antiemetics if you cannot retain fluids for 12 hours."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "PREGNANCY",
            "question": "What is the acceptable range for fasting blood glucose during pregnancy to avoid gestational diabetes complications?",
            "answer": "According to ACOG guidelines, target blood glucose levels in gestational diabetes management are: Fasting <= 95 mg/dL, 1-hour postprandial <= 140 mg/dL, and 2-hour postprandial <= 120 mg/dL. Tightly controlled glycemic levels prevent macrosomia and neonatal hypoglycemia."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "TTC",
            "question": "How do basal body temperature (BBT) shifts confirm ovulation, and when does the temperature rise?",
            "answer": "After ovulation, the corpus luteum produces progesterone, a thermogenic hormone that raises basal body temperature by approximately 0.5 to 1.0 degree Fahrenheit (0.3 to 0.6 C). This biphasic shift confirms ovulation retrospectively; temperature remains elevated throughout the luteal phase (12-16 days)."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "PERIOD_TRACKING",
            "question": "Why is my menstrual flow suddenly very heavy with golf-ball-sized clots, and when does it become menorrhagia?",
            "answer": "Menorrhagia is clinically defined as blood loss exceeding 80 mL per cycle or soaking through one or more pads/tampons every hour for consecutive hours. Passing blood clots larger than a quarter requires clinical assessment for uterine fibroids, adenomyosis, polyps, or coagulopathies."
        }
    ]
    
    df_curated = pd.DataFrame(curated_cases)
    df_final = pd.concat([df_clean, df_curated]).drop_duplicates(subset=["question"]).reset_index(drop=True)
    
    df_final.to_csv(CLEAN_QA_PATH, index=False)
    print(f"Cleaned dataset: {len(df_final)} high-quality women's health Q&As saved to {CLEAN_QA_PATH}")

if __name__ == "__main__":
    clean_data()
