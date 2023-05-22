import datetime
import logging
import os
import pathlib
from logging.handlers import TimedRotatingFileHandler
from urllib.parse import urlparse, parse_qs

import requests
from botocore.client import Config
from sqlalchemy.orm import Session

from database.crud import CMMPAResultsCrud
from database.db import get_db

from healthie import healthie, healthie_api
from db_client import DBClient
from drchrono import drchrono
from mdintegrations import mdi_instance_dict
from utils import send_text_email, send_text_message
from config import *
from helpers.messages import weight_loss_message
from datetime import date
import uuid
from utils import create_presigned_url, check_file_in_s3
import asyncio

HOURS_DELTA = 6

# logging
logger = logging.getLogger('drchrono_sync')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')

log_dir = os.path.join(os.getcwd(), 'log')
logging_file = os.path.join(
    log_dir,
    os.path.splitext(os.path.basename(__file__))[0] + datetime.datetime.now().strftime('%y%m%d') + '.log'
)
fh = TimedRotatingFileHandler(logging_file, when='d', interval=1, backupCount=5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

OBSERVATION_TO_TEST_NAME = {
    # Quest
    'Color Ur': 'Color',
    'Appearance Ur': 'Appearance',
    'Sp Gr Ur Strip': 'Specific Gravity',
    'pH Ur Strip': 'pH',
    'Glucose Ur Ql Strip': 'Glucose',
    'Bilirub Ur Ql Strip': 'Bilirubin',
    'Ketones Ur Ql Strip': 'Ketones',
    'Hgb Ur Ql Strip': 'Occult Blood',
    'Prot Ur Ql Strip': 'Protein',
    'Nitrite Ur Ql Strip': 'Nitrite',
    'Leukocyte esterase Ur Ql Strip': 'Leukocyte Esterase',
    'WBC #/area UrnS HPF': 'White Blood Cells',
    'RBC #/area UrnS HPF': 'Red Blood Cells',
    'Squamous #/area UrnS HPF': 'Squamous Epithelial Cells',
    'Bacteria #/area UrnS HPF': 'Bacteria',
    'Hyaline Casts #/area UrnS LPF': 'Hyaline Cast',
    'HSV1 IgG Ser IA-aCnc': 'Herpes 1',
    'HSV2 IgG Ser IA-aCnc': 'Herpes 2',
    'HIV 1+2 Ab+HIV1 p24 Ag SerPl Ql IA': 'HIV',
    'C trach rRNA Spec Ql NAA+probe': 'Chlamydia',
    'N gonorrhoea rRNA Spec Ql NAA+probe': 'Gonorrhea',
    'T vaginalis rRNA Spec Ql NAA+probe': 'Trichomoniasis',
    'RPR Ser Ql': 'Syphilis',
    'HBV surface Ag SerPl Ql IA': 'Hepatitis B',
    'HCV Ab SerPl Ql IA': 'Hepatitis C',
    'HCV Ab s/co SerPl IA': 'Hepatitis C',
    'M hominis Spec Ql Cult': 'Mycoplasma',
    'Ureaplasma Spec Cult': 'Ureaplasma',
    'HSV1 IgM Ser Ql IF': 'Herpes 1',
    'HSV2 IgM Ser Ql IF': 'Herpes 2',
    'HIV1 RNA # SerPl NAA+probe': 'HIV',
    'HIV1 RNA SerPl Ql NAA+probe': 'HIV',
    'Squid IgE Qn': 'Squid Allergy',
    'Squid IgE RAST Ql': 'Corn Allergy',
    'Corn IgE Qn': 'Corn Allergy',
    'Corn IgE RAST Ql': 'Corn Allergy',
    'Rice IgE Qn': 'Rice Allergy',
    'Rice IgE RAST Ql': 'Rice Allergy',
    'Tomato IgE Qn': 'Tomato Allergy',
    'Tomato IgE RAST Ql': 'Tomato Allergy',
    'Pork IgE Qn': 'Pork Allergy',
    'Pork IgE RAST Ql': 'Pork Allergy',
    'Beef IgE Qn': 'Beef Allergy',
    'Beef IgE RAST Ql': 'Beef Allergy',
    'Strawberry IgE Qn': 'Strawberry Allergy',
    'Strawberry IgE RAST Ql': 'Strawberry Allergy',
    'Garlic IgE Qn': 'Garlic Allergy',
    'Garlic IgE RAST Ql': 'Garlic Allergy',
    'Apple IgE Qn': 'Apple Allergy',
    'Apple IgE RAST Ql': 'Apple Allergy',
    'Chicken Meat IgE Qn': 'Chicken Allergy',
    'Chicken Meat IgE RAST Ql': 'Chicken Allergy',
    'Celery IgE Qn': 'Celery Allergy',
    'Celery Allergy': 'Celery Allergy',
    'Kiwifruit IgE Qn': 'Kiwi Allergy',
    'Kiwifruit IgE RAST Ql': 'Kiwi Allergy',
    'Mustard IgE Qn': 'Mustard Allergy',
    'Mustard IgE RAST Ql': 'Mustard Allergy',
    'Pineapple IgE Qn': 'Pineapple Allergy',
    'Pineapple IgE RAST Ql': 'Pineapple Allergy',
    'Peach IgE Qn': 'Peach Allergy',
    'Peach IgE RAST Ql': 'Peach Allergy',
    'Banana IgE Qn': 'Banana Allergy',
    'Banana IgE RAST Ql': 'Banana Allergy',
    'Avocado IgE Qn': 'Avocado Allergy',
    'Avocado IgE RAST Ql': 'Avocado Allergy',
    'Egg White IgE Qn': 'Egg Allergy',
    'Egg White IgE RAST Ql': 'Egg Allergy',
    'Peanut IgE Qn': 'Peanut Allergy',
    'Peanut IgE RAST Ql': 'Peanut Allergy',
    'Wheat IgE Qn': 'Wheat Allergy',
    'Wheat IgE RAST Ql': 'Wheat Allergy',
    'Walnut IgE Qn': 'Walnut Allergy',
    'Walnut IgE RAST Ql': 'Walnut Allergy',
    'Codfish IgE Qn': 'Codfish Allergy',
    'Codfish IgE RAST Ql': 'Codfish Allergy',
    'Milk IgE Qn': 'Milk Allergy',
    'Milk IgE RAST Ql': 'Milk Allergy',
    'Soybean IgE Qn': 'Soybean Allergy',
    'Soybean IgE RAST Ql': 'Soybean Allergy',
    'Shrimp IgE Qn': 'Shrimp Allergy',
    'Shrimp IgE RAST Ql': 'Shrimp Allergy',
    'Scallop IgE Qn': 'Scallop Allergy',
    'Scallop IgE RAST Ql': 'Scallop Allergy',
    'Sesame Seed IgE Qn': 'Sesame Seed Allergy',
    'Sesame Seed IgE RAST Ql': 'Sesame Seed Allergy',
    'Hazelnut IgE Qn': 'Hazelnut Allergy',
    'Hazelnut Allergy': 'Hazelnut Allergy',
    'Cashew Nut IgE Qn': 'Cashew Allergy',
    'Cashew Nut IgE RAST Ql': 'Cashew Allergy',
    'Almond IgE Qn': 'Almond Allergy',
    'Almond IgE RAST Ql': 'Almond Allergy',
    'Salmon IgE Qn': 'Salmon Allergy',
    'Salmon IgE RAST Ql': 'Salmon Allergy',
    'Tuna IgE Qn': 'Tuna Allergy',
    'Tuna IgE RAST Ql': 'Tuna Allergy',
    'Mango IgE Qn': 'Mango Allergy',
    'Mango IgE RAST Ql': 'Mango Allergy',
    'Watermelon IgE Qn': 'Watermelon Allergy',
    'Watermelon IgE RAST Ql': 'Watermelon Allergy',
    'Gelatin IgE Qn': 'Gelatin Allergy',
    'Gelatin IgE RAST Ql': 'Gelatin Allergy',
    'Cilantro IgE Qn': 'Cilantro Allergy',
    'Cilantro IgE RAST Ql': 'Cilantro Allergy',
    'tTG IgG Ser-aCnc': 'tTG IgG',
    'tTG IgA Ser-aCnc': 'tTG IgA',
    'Gliadin IgA Ser IA-aCnc': 'Giladin IgA',
    'Gliadin IgG Ser IA-aCnc': 'Giladin IgG',
    'IgA SerPl-mCnc': 'Total IgA',
    'TSH SerPl-aCnc': 'TSH',
    'T4 Free SerPl-mCnc': 'Free T4',
    'Free T3, FREE': 'Free T3',
    'Thyroperoxidase Ab SerPl-aCnc': 'TPO',
    'Testost Free SerPl-mCnc': 'Testosterone, Free',
    'Cortis SerPl-mCnc': 'Cortisol',
    'DHEA-S SerPl-mCnc': 'DHEAS',
    'FSH SerPl-aCnc': 'FSH',
    'LH SerPl-aCnc': 'LH',
    'Progest SerPl-mCnc': 'Progesterone',
    'Estradiol SerPl-mCnc': 'Estradiol',
    'u DHEA SerPl-mCnc': 'DHEA',
    'Prot SerPl-mCnc': 'Total Protein',
    'Albumin SerPl-mCnc': 'Albumin',
    'Globulin Ser Calc-mCnc': 'Globulin',
    'Albumin/Glob SerPl': 'A/G Ratio',
    'Sodium SerPl-sCnc': 'Sodium',
    'Potassium SerPl-sCnc': 'Potassium',
    'Chloride SerPl-sCnc': 'Chloride',
    'CO2 SerPl-sCnc': 'CO2',
    'BUN SerPl-mCnc': 'BUN',
    'Creat SerPl-mCnc': 'Creatinine',
    'GFR/BSA pred.nonblk SerPl CKD-EPI-ArVRat': 'e-GFR',
    'GFR/BSA pred.blk SerPlBld CKD-EPI-ArVRat': 'e-GFR, African American',
    'BUN/Creat SerPl': 'BUN/Creat Ratio',
    'Calcium SerPl-mCnc': 'Calcium',
    'Bilirub SerPl-mCnc': 'Bilirubin',
    'ALP SerPl-cCnc': 'Alk Phos',
    'AST SerPl-cCnc': 'AST',
    'Glucose SerPl-mCnc': 'Glucose',
    'ALT SerPl-cCnc': 'ALT',
    'HbA1c MFr Bld': 'Hemoglobin A1c',
    'Cholest SerPl-mCnc': 'Cholesterol',
    'HDLc SerPl-mCnc': 'HDL Cholesterol',
    'Trigl SerPl-mCnc': 'Triglycerides',
    'LDLc SerPl Calc-mCnc': 'LDL Cholesterol',
    'Cholest/HDLc SerPl': 'Cholesterol/HDL Ratio',
    'NonHDLc SerPl-mCnc': 'Non HDL Cholesterol',
    'B burgdor Ab Ser IA-aCnc': 'Lyme Disease',
    'Arsenic Bld-mCnc': 'Arsenic',
    'Lead BldV-mCnc': 'Lead',
    'Mercury Bld-mCnc': 'Mercury',
    'Iodine SerPl-mCnc': 'Iodine',
    'Selenium Bld-mCnc': 'Selenium',
    'Cadmium Bld-mCnc': 'Cadmium',
    'Vit A SerPl-mCnc': 'Vitamin A',
    'Vit B1 Bld-sCnc': 'Vitamin B1',
    'Vit B6 SerPl-mCnc': 'Vitamin B6',
    'Folate SerPl-mCnc': 'Vitamin B9',
    'Vit B12 SerPl-mCnc': 'Vitamin B12',
    'Vit C SerPl-mCnc': 'Vitamin C',
    '25(OH)D3 SerPl-mCnc': 'Vitamin D 25-Hydroxy',
    'A-Tocopherol Vit E SerPl-mCnc': 'Vitamin E',
    'Beta+Gamma Tocopherol SerPl-mCnc': 'Vitamin E',
    'Phytonadione SerPl-mCnc': 'Vitamin K',
    'Zinc SerPl-mCnc': 'Zinc',
    'Carotene SerPl-mCnc': 'Carotene',
    'Ferritin SerPl-mCnc': 'Ferritin',
    'CRP SerPl HS-mCnc': 'HS CRP',
    'Iron SerPl-mCnc': 'Iron',
    'Iron Satn MFr SerPl': 'Iron',
    'TIBC SerPl-mCnc': 'Total Iron Binding Capacity',
    'D pteronyss IgE Qn': 'Allergies',
    'D pteronyss IgE RAST Ql': 'Allergies',
    'D farinae IgE Qn': 'Allergies',
    'D farinae IgE RAST Ql': 'Allergies',
    'P notatum IgE Qn': 'Allergies',
    'P notatum IgE RAST Ql': 'Allergies',
    'C herbarum IgE Qn': 'Allergies',
    'C herbarum IgE RAST Ql': 'Allergies',
    'A fumigatus IgE Qn': 'Allergies',
    'A fumigatus IgE RAST Ql': 'Allergies',
    'A alternata IgE Qn': 'Allergies',
    'A alternata IgE RAST Ql': 'Allergies',
    'Cat Dander IgE Qn': 'Allergies',
    'Cat Dander IgE RAST Ql': 'Allergies',
    'Dog Dander IgE Qn': 'Allergies',
    'Dog Dander IgE RAST Ql': 'Allergies',
    'Roach IgE Qn': 'Allergies',
    'Roach IgE RAST Ql': 'Allergies',
    'Boxelder IgE Qn': 'Allergies',
    'Boxelder IgE RAST Ql': 'Allergies',
    'Silver Birch IgE Qn': 'Allergies',
    'Silver Birch IgE RAST Ql': 'Allergies',
    'Mt Juniper IgE Qn': 'Allergies',
    'Mt Juniper IgE RAST Ql': 'Allergies',
    'White Oak IgE Qn': 'Allergies',
    'White Oak IgE RAST Ql': 'Allergies',
    'White Elm IgE Qn': 'Allergies',
    'White Elm IgE RAST Ql': 'Allergies',
    'Pecan/Hick Tree IgE Qn': 'Allergies',
    'Pecan/Hick Tree IgE RAST Ql': 'Allergies',
    'Bermuda grass IgE Qn': 'Allergies',
    'Bermuda grass IgE RAST Ql': 'Allergies',
    'Timothy IgE Qn': 'Allergies',
    'Timothy IgE RAST Ql': 'Allergies',
    'Bahia grass IgE Qn': 'Allergies',
    'Bahia grass IgE RAST Ql': 'Allergies',
    'Common Ragweed IgE Qn': 'Allergies',
    'Common Ragweed IgE RAST Ql': 'Allergies',
    'Common Pigweed IgE Qn': 'Allergies',
    'Common Pigweed IgE RAST Ql': 'Allergies',
    'Sheep Sorrel IgE Qn': 'Allergies',
    'Sheep Sorrel IgE RAST Ql': 'Allergies',
    'Nettle IgE Qn': 'Allergies',
    'Nettle IgE RAST Ql': 'Allergies',
    'Mouse Urine Prot IgE Qn': 'Allergies',
    'Mouse Urine Prot IgE RAST Ql': 'Allergies',
    'IgE SerPl-aCnc': 'Allergies',
    'Calif Walnut Poln IgE Qn': 'Allergies',
    'Calif Walnut Poln IgE RAST Ql': 'Allergies',
    'London Plane IgE Qn': 'Allergies',
    'London Plane IgE RAST Ql': 'Allergies',
    'Cottonwood IgE Qn': 'Allergies',
    'Cottonwood IgE RAST Ql': 'Allergies',
    'White Ash IgE Qn': 'Allergies',
    'White Ash IgE RAST Ql': 'Allergies',
    'White mulberry IgE Qn': 'Allergies',
    'White mulberry IgE RAST Ql': 'Allergies',
    'Mugwort IgE Qn': 'Allergies',
    'Mugwort IgE RAST Ql': 'Allergies',
    'Saltwort IgE Qn': 'Allergies',
    'Saltwort IgE RAST Ql': 'Allergies',
    'Johnson grass IgE Qn': 'Allergies',
    'Johnson grass IgE RAST Ql': 'Allergies',
    'Grey Alder IgE Qn': 'Allergies',
    'Grey Alder IgE RAST Ql': 'Allergies',
    'Olive Poln IgE Qn': 'Allergies',
    'Olive Poln IgE RAST Ql': 'Allergies',
    'Marsh Elder IgE Qn': 'Allergies',
    'Marsh Elder IgE RAST Ql': 'Allergies',
    'Immunoglobulin E, Total': 'Allergies',

    # Labcorp
    'Interpretation:': 'HIV',
    'Urine-Color': 'Color',
    'Appearance': 'Appearance',
    'Specific Gravity': 'Specific Gravity',
    'pH': 'pH',
    'Glucose': 'Glucose',
    'Bilirubin': 'Bilirubin',
    'Ketones': 'Ketones',
    'Occult Blood': 'Occult Blood',
    'Protein': 'Protein',
    'Nitrite, Urine': 'Nitrite',
    'WBC Esterase': 'WBC Esterase',
    'Urobilinogen,Semi-Qn': 'Urobilinogen',
    'WBC': 'White Blood Cells',
    'RBC': 'Red Blood Cells',
    'Epithelial Cells (non renal)': 'Epithelial Cells',
    'Epithelial Cells (renal)': 'Epithelial Cells',
    'Bacteria': 'Bacteria',
    'Yeast': 'Yeast',
    'Casts': 'Casts',
    'Cast Type': 'Casts',
    'Mucus Threads': 'Mucus',
    'HSV 1 IgG, Type Spec': 'Herpes 1',
    'HSV 2 IgG, Type Spec': 'Herpes 2',
    'HIV Screen 4th Generation wRfx': 'HIV',
    'Chlamydia by NAA': 'Chlamydia',
    'Gonococcus by NAA': 'Gonorrhea',
    'Trich vag by NAA': 'Trichomoniasis',
    'Trichomonas': 'Trichomoniasis',
    'HBsAg Screen': 'Hepatitis B',
    'HCV Ab': 'Hepatitis C',
    'Mycoplasma hominis': 'Mycoplasma',
    'Mycoplasma hominis NAA': 'Mycoplasma',
    'Ureaplasma urealyticum': 'Ureaplasma',
    'Ureaplasma spp NAA': 'Ureaplasma',
    'HIV 1 Ab': 'HIV',
    'HIV1 Ab SerPl Ql IA': 'HIV',
    'F001-IgE Egg White': 'Egg Allergy',
    'F013-IgE Peanut': 'Peanut Allergy',
    'F014-IgE Soybean': 'Soybean Allergy',
    'F002-IgE Milk': 'Milk Allergy',
    'F207-IgE Clam': 'Clam Allergy',
    'F024-IgE Shrimp': 'Shrimp Allergy',
    'F256-IgE Walnut': 'Walnut Allergy',
    'F003-IgE Codfish': 'Codfish Allergy',
    'F338-IgE Scallop': 'Scallop Allergy',
    'F004-IgE Wheat': 'Wheat Allergy',
    'F008-IgE Corn': 'Corn Allergy',
    'F010-IgE Sesame Seed': 'Sesame Seed Allergy',
    'F026-IgE Pork': 'Pork Allergy',
    'F027-IgE Beef': 'Beef Allergy',
    'F083-IgE Chicken': 'Chicken Allergy',
    'F202-IgE Cashew Nut': 'Cashew Alergy',
    'F025-IgE Tomato': 'Tomato Allergy',
    'F020-IgE Almond': 'Almond Allergy',
    'F017-IgE Hazelnut (Filbert)': 'Hazelnut Allergy',
    'F041-IgE Salmon': 'Salmon Alleregy',
    'F040-IgE Tuna': 'Tuna Allergy',
    'F009-IgE Rice': 'Rice Allergy',
    'F044-IgE Strawberry': 'Strawberry Allergy',
    'F047-IgE Garlic': 'Garlic Allergy',
    'F329-IgE Watermelon': 'Watermelon Allergy',
    'F081-IgE Cheese, Cheddar Type': 'Cheese Allergy',
    'F084-IgE Kiwi Fruit': 'Kiwi Allergy',
    'F085-IgE Celery': 'Celergy Allergy',
    'F089-IgE Mustard': 'Mustard Allergy',
    'F091-IgE Mango': 'Mango Allergy',
    'F095-IgE Peach': 'Peach Allergy',
    'F096-IgE Avocado': 'Avocado Allergy',
    'F210-IgE Pineapple': 'Pineapple Allergy',
    'F058-IgE Squid': 'Squid Allergy',
    'C074-IgE Gelatin': 'Gelatin Allergy',
    'F317-IgE Coriander/Cilantro': 'Cilantro Allergy',
    'Immunoglobulin A, Qn, Serum': 'Total IgA',
    'Deamidated Gliadin Abs, IgA': 'Gliadin IgA',
    'Deamidated Gliadin Abs, IgG': 'Gliadin IgG',
    't-Transglutaminase (tTG) IgA': 'tTG IgA',
    't-Transglutaminase (tTG) IgG': 'tTG IgG',
    'TSH': 'TSH',
    'T4,Free(Direct)': 'Free T4',
    'Triiodothyronine (T3), Free': 'Free T3',
    'Thyroid Peroxidase (TPO) Ab': 'TPO',
    'Free Testosterone(Direct)': 'Testosterone, Free',
    'Cortisol': 'Cortisol',
    'DHEA-Sulfate': 'DHEAS',
    'FSH': 'FSH',
    'LH': 'LH',
    'Progesterone': 'Progesterone',
    'Estradiol': 'Estradiol',
    'Dehydroepiandrosterone (DHEA)': 'DHEA',
    'Protein, Total': 'Total Protein',
    'Albumin': 'Albumin',
    'Globulin, Total': 'Globulin',
    'A/G Ratio': 'A/G Ratio',
    'Sodium': 'Sodium',
    'Potassium': 'Potassium',
    'Chloride': 'Chloride',
    'Carbon Dioxide, Total': 'CO2',
    'BUN': 'BUN',
    'Creatinine': 'Creatinine',
    'eGFR If NonAfricn Am': 'e-GFR',
    'eGFR If Africn Am': 'e-GFR, African American',
    'BUN/Creatinine Ratio': 'BUN/Creat Ratio',
    'Calcium': 'Calcium',
    'Bilirubin, Total': 'Bilirubin',
    'Alkaline Phosphatase': 'Alk Phos',
    'AST (SGOT)': 'AST',
    'ALT (SGPT)': 'ALT',
    'Cholesterol, Total': 'Cholesterol',
    'HDL Cholesterol': 'HDL Cholesterol',
    'Triglycerides': 'Triglycerides',
    'LDL Chol Calc (NIH)': 'LDL Cholesterol',
    'VLDL Cholesterol Cal': 'VLDL Cholesterol',
    'Lyme IgG/IgM Ab': 'Lyme Disease',
    'Lyme Disease Ab, Quant, IgM': 'Lyme Disease',
    'Lead, Blood': 'Lead',
    'Arsenic, Blood': 'Arsenic',
    'Mercury, Blood': 'Mercury',
    'Iodine, Serum or Plasma': 'Iodine',
    'Selenium, Blood': 'Selenium',
    'Cadmium, Blood': 'Cadmium',
    'C-Reactive Protein, Cardiac': 'HS CRP',
    'Class Description': 'Allergies',
    'D001-IgE D pteronyssinus': 'Allergies',
    'D002-IgE D farinae': 'Allergies',
    'E001-IgE Cat Dander': 'Allergies',
    'E005-IgE Dog Dander': 'Allergies',
    'G002-IgE Bermuda Grass': 'Allergies',
    'G017-IgE Bahia Grass': 'Allergies',
    'G006-IgE Timothy Grass': 'Allergies',
    'I006-IgE Cockroach, German': 'Allergies',
    'M001-IgE Penicillium chrysogen': 'Allergies',
    'M002-IgE Cladosporium herbarum': 'Allergies',
    'M003-IgE Aspergillus fumigatus': 'Allergies',
    'M006-IgE Alternaria alternata': 'Allergies',
    'T001-IgE Maple/Box Elder': 'Allergies',
    'T003-IgE Common Silver Birch': 'Allergies',
    'T006-IgE Cedar, Mountain': 'Allergies',
    'T007-IgE Oak, White': 'Allergies',
    'T008-IgE Elm, American': 'Allergies',
    'T022-IgE Pecan, Hickory': 'Allergies',
    'W001-IgE Ragweed, Short': 'Allergies',
    'W014-IgE Pigweed, Common': 'Allergies',
    'W018-IgE Sheep Sorrel': 'Allergies',
    'W020-IgE Nettle': 'Allergies',
    'E072-IgE Mouse Urine': 'Allergies',
    'D201-IgE Blomia tropicalis': 'Allergies',
    'T016-IgE Pine, White': 'Allergies',
    'T010-IgE Walnut': 'Allergies',
    'T011-IgE Maple Leaf Sycamore': 'Allergies',
    'T014-IgE Cottonwood': 'Allergies',
    'T015-IgE Ash, White': 'Allergies',
    'T070-IgE White Mulberry': 'Allergies',
    'W011-IgE Thistle, Russian': 'Allergies',
    'G010-IgE Johnson Grass': 'Allergies',
    'W016-IgE Rough Marshelder': 'Allergies',
    'W006-IgE Mugwort': 'Allergies',

    # BioRef
    'CHLAMYDIA TRACHOMATIS BY MULTIPLEX PCR': 'Chlamydia',
    'MYCOPLASMA GENITALIUM BY MULTIPLEX PCR': 'Mycoplasma',
    'TRICHOMONAS BY MULTIPLEX PCR': 'Trichomoniasis',
    'TRICHOMONAS APTIMA': 'Trichomoniasis',
    'Ureaplasma By Multiplex PCR- Males Only': 'Ureaplasma',
    'Herpes I Ab.(IgG)': 'Herpes 1',
    'Herpes II Ab.(IgG)': 'Herpes 2',
    'HIV Ag/Ab': 'HIV',
    'Specific Gravity Ur': 'Specific Gravity',
    'pH Urine': 'pH',
    'Protein, Urine': 'Protein',
    'Glucose, Urine': 'Glucose',
    'Ketone, Urine': 'Ketones',
    'Urobilinogen Urine': 'Urobilinogen',
    'Bilirubin, Urine': 'Bilirubin',
    'Blood, Urine': 'Blood',
    'Nitrites Urine': 'Nitrite',
    'Crystals Urine': 'Crystals',
    'WBC, Urine': 'White Blood Cells',
    'RBC, Urine': 'Red Blood Cells',
    'Cast, RBC, Urine': 'Casts',
    'Cast, Hyaline, Urine': 'Casts',
    'Epithelial Cells, Ur': 'Epithelial Cells',
    'Cast, Granular, Ur': 'Casts',
    'Bacteria, Urine': 'Bacteria',
    'Sperm Cells, Urine': 'Sperm',
    'Crystal Amt. Urine': 'Crystals',
    'Chlamydia trachomatis, NAA': 'Chlamydia',
    'HSV-2 IgG Supplemental Test': 'Herpes 2',
    'HSV, IgM I/II Combination': 'Herpes 1',
    'HSV2 IgM Titr Ser IF': 'Herpes 2',
    'RPR': 'Syphilis',
    'RPR, Quant': 'Syphilis',
    'RPR Ser-Titr': 'Syphilis',
    'T pallidum Antibodies': 'Syphilis',
    'Bacteria Ur Cult': 'Bacteria',
    'CaOx Cry #/area UrnS HPF': 'CALCIUM OXALATE CRYSTALS',
    'Crystals': 'Crystals',
    'Crystal Type': 'Crystals',
    'HBsAg Confirmation': 'Hepatitis B',
    'Hepatitis B Surf Ab Quant': 'Hepatitis B',
    'HBV surface Ab Ser Ql IA': 'Hepatitis B',
    'Leukocyte Esterase': 'Leukocyte Esterase',
    'Color': 'Color',
    'Character': 'Character',
    'Anti-Endomysial Ab': 'Endomysial Antibodies',
    'GLIADIN(DP) IgG,Ab': 'Gliadin IgG',
    'GLIADIN(DP) IgA,Ab': 'Gliadin IgA',
    'Thyroxine(T4)': 'Free T4',
    'T3, FREE (FT3)': 'Free T3',
    'ANTI-TPO Ab': 'TPO',
    'TESTOSTERONE, TOT.,S.': 'Testosterone, Free',
    'CORTISOL, RANDOM': 'Cortisol',
    'DHEA SULFATE': 'DHEAS',
    'PROGESTERONE': 'Progesterone',
    'ESTRADIOL': 'Estradiol',
    'Total Protein': 'Total Protein',
    'Globulin': 'Globulin',
    'CO2': 'CO2',
    'e-GFR': 'e-GFR',
    'e-GFR, African American': 'e-GFR, African American',
    'BUN/Creat Ratio': 'BUN/Creat Ratio',
    'Alk Phos': 'Alk Phos',
    'AST': 'AST',
    'Hemoglobin A1c': 'Hemoglobin A1c',
    'Cholesterol': 'Cholesterol',
    'HDL CHOL., DIRECT': 'HDL Cholesterol',
    'LDL Cholesterol': 'LDL Cholesterol',
    'Chol/HDL Ratio': 'Cholesterol/HDL Ratio',
    'Non-HDL Cholesterol': 'Non HDL Cholesterol',
    'HDL as % of Cholesterol': 'HDL Cholesterol %',
    'LDL/HDL Ratio': 'LDL/HDL Ratio',
    'VLDL, CALCULATED': 'VLDL Cholesterol',
    'IODINE, SERUM/PLASMA': 'Iodine',
    'ARSENIC, BLOOD': 'Arsenic',
    'CADMIUM, BLOOD': 'Cadmium',
    'LEAD, BLOOD (ADULT)': 'Lead',
    'MERCURY, BLOOD (3)': 'Mercury',
    'SELENIUM,SER/PLASMA': 'Selenium',
    '25OH, VITAMIN D': 'Vitamin D 25-Hydroxy',
    'hsCRP': 'HS CRP',
    'Alternaria Tenuis Mold': 'Allergies',
    'A. Fumigatus Mold': 'Allergies',
    'Maple (Box Elder)': 'Allergies',
    'Cat Dander': 'Allergies',
    'C. Herbarum': 'Allergies',
    'Cockroach': 'Allergies',
    'Dog Dander': 'Allergies',
    'Elm Tree': 'Allergies',
    'Lambs Quarters (Weed)': 'Allergies',
    'D. Pteronyssinus': 'Allergies',
    'D. Farinae (Dust Mite)': 'Allergies',
    'Oak Tree': 'Allergies',
    'Orchard Grass': 'Allergies',
    'White Ash': 'Allergies',
    'Common Birch': 'Allergies',
    'Common Ragweed': 'Allergies',
    'Bermuda Grass': 'Allergies',
    'Timothy Grass': 'Allergies',
    'Penicillium Mold': 'Allergies',
    'Cotton-Wood': 'Allergies',
    'Mugwort': 'Allergies',
    'Sheep Sorrel': 'Allergies',
    'White Mulberry': 'Allergies',
    'Walnut Tree': 'Allergies',
    'Sycamore': 'Allergies',
    'Mountain Juniper': 'Allergies',
    'Rough Careless Pigweed': 'Allergies',
    'eGFRcr SerPlBld CKD-EPI 2021': 'eGFR',
    'eGFR': 'eGFR',
    'Vitamin D, 25-Hydroxy': 'Vitamin D'
}

# convert all keys to lower case
OBSERVATION_TO_TEST_NAME = {k.lower(): v for k, v in OBSERVATION_TO_TEST_NAME.items()}

URGENT_TEST_LIST = ['Chlamydia', 'Gonorrhea', 'Trichomoniasis', 'Hepatitis C', 'HIV', 'Syphilis', 'Ureaplasma', 'Mycoplasma', 'TSH']
# cases to be created from frontend for these
FRONTEND_TEST_LIST = []
MDI_SERVICE_DICT = {}

s3_bucket = 'drchronodoc'
s3_patient_bucket = "patient-upload"
s3_region = 'us-east-2'
s3_client = boto3.client(
    's3',
    region_name=s3_region,
    aws_access_key_id="AKIAJSZRUVGIPVVOPUGA",
    aws_secret_access_key="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",
    config=Config(
        signature_version='s3v4',
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )
)

db = DBClient()


def fetch_lab_documents():
    """Fetch lab documents generated within HOURS_DELTA hours"""
    lastHourDateTime = datetime.datetime.now() - datetime.timedelta(hours=HOURS_DELTA)
    cursor = None
    documents = []
    while True:
        param = {
            'cursor': cursor,
            'since': lastHourDateTime.strftime('%Y-%m-%dT%H:%M:00')
        }
        res = drchrono.lab_documents_list(param)
        documents += res.get('results', [])
        url = res.get('next')
        if url is None:
            return documents
        else:
            parsed_url = urlparse(url)
            cursor = parse_qs(parsed_url.query)['cursor'][0]
            logger.debug(f'cursor={cursor}')
    return []


def fetch_lab_documents_between(start_date: str, end_date: str):
    """
    Fetch lab documents generated between start_date & end_date
    :param start_date: in format 2021-11-31 00:00:00
    :param end_date: in format 2021-12-31 00:00:00
    :return: list of lab documents
    """
    start_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

    cursor = None
    documents = []
    while True:
        param = {
            'cursor': cursor,
            'since': start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        }
        res = drchrono.lab_documents_list(param)
        results = res.get('results', [])

        for i, result in reversed(list(enumerate(results))):
            ts = result.get('timestamp')
            if datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S') <= end_datetime:
                documents += results[:i + 1]
                break
        url = res.get('next')
        if url is None:
            return documents
        else:
            parsed_url = urlparse(url)
            cursor = parse_qs(parsed_url.query)['cursor'][0]
            logger.debug(f'cursor={cursor}')
    return []


class LabDocument:
    """class representation of Drchrono Lab document."""

    def __init__(self, id: str, lab_order: str, document: str, type: str, timestamp):
        self.visits = None
        self.mdi_account_type = None
        self.mdi_api = None
        self.id = id
        self.lab_order = lab_order
        self.document = document
        self.type = type
        self.timestamp = timestamp
        self.ts = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        self.patient_id = None
        self.pdf_path = None
        self.visit = None
        self.results = []
        self.abnormal_tests = []
        self._fetch_patient_id_()

    def _fetch_lab_results_(self):
        """Fetch lab results"""
        try:
            logger.info("drchrono_sync_new: getting lab result for email=" + str(self.visit.get('email')))
            cursor = None
            while True:
                param = {
                    'cursor': cursor,
                    'order': self.lab_order
                }

                res = drchrono.lab_results_list(param)
                self.results += res.get('results', [])
                logger.info("drchrono_sync_new: fetching lab results with results=" + str(self.results))
                url = res.get('next')
                if url is None:
                    return
                else:
                    parsed_url = urlparse(url)
                    cursor = parse_qs(parsed_url.query)['cursor'][0]
                    logger.debug(f'cursor={cursor}')
        except Exception as e:
            logger.exception(e)

    def are_results_final(self):
        """Returns False if any test result status is P or I else return True"""
        tests_dict = {}
        for result in self.results:
            test = result.get('observation_description')
            OBSERVATION_TO_TEST_NAME.get(test.lower(), "")
            result.get('status')
            tests_dict[test] = result.get('status')
        for status in tests_dict.values():
            if status == 'P' or status == 'I':
                return False
        return True

    def find_abnormal_results(self):
        """returns a list of Tests with abnormal results"""
        logger.info("drchrono_sync_new: finding abnormal results for email=" + str(self.visit.get('email')))
        for result in self.results:
            if result.get('is_abnormal') is True:
                logger.debug(f"Abnormal result found: {result}")
                # find lab test
                observation_description = result.get('observation_description')
                lab_test_name = OBSERVATION_TO_TEST_NAME.get(observation_description.lower(), "")
                if lab_test_name == "":
                    if observation_description.endswith('IgE Qn'):
                        lab_test_name = 'Allergies'
                    elif 'IgE ' in observation_description:
                        lab_test_name = 'Allergies'
                    else:
                        logger.warning(f"Lab Test name not found for observation_description:{observation_description}")
                        continue
                if lab_test_name not in self.abnormal_tests:
                    self.abnormal_tests.append(lab_test_name)

    def _fetch_patient_id_(self):
        lab_order = drchrono.lab_orders_read(self.lab_order)
        self.patient_id = lab_order.get('patient')

    def download_pdf(self):
        dr_chrono_documents_directory_path = 'pdfs/drchrono_documents/'
        pathlib.Path(dr_chrono_documents_directory_path).mkdir(parents=True, exist_ok=True)
        pdf_path = dr_chrono_documents_directory_path + str(self.id) + '.pdf'
        try:
            logger.debug(f"downloading pdf {self.id}")
            response = requests.get(self.document)
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            f.close()
            self.pdf_path = pdf_path
        except Exception as e:
            logger.exception(e)

    def delete_pdf(self):
        if self.pdf_path is None:
            return
        try:
            logger.debug(f"Deleting downloaded pdf {self.pdf_path}")
            os.remove(self.pdf_path)
        except Exception as e:
            logger.exception(e)

    def upload_file(self, object_name=None):
        """Upload a file to an S3 bucket

        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(self.pdf_path)

        # Upload the file
        try:
            s3_client.upload_file(self.pdf_path, s3_bucket, object_name)
        except Exception as e:
            logger.error(f"upload_file (handle_type_req, handle_type_res) ==> {str(e)}")
            return False
        return True

    def get_s3_url(self, object_name=None):
        object_key = object_name if object_name else self.id
        # fix NXTMD-494: .pdf.pdf is returned
        if object_key.endswith(".pdf"):
            return f"https://s3.{s3_region}.amazonaws.com/{s3_bucket}/{object_key}"
        else:
            return f"https://s3.{s3_region}.amazonaws.com/{s3_bucket}/{object_key}.pdf"

    async def send_requisition_to_healthie(self):
        """upload requisition to healthie"""
        try:
            healthie_id = self.visit.get("healthie_id")
            email = self.visit.get('email')
            r = await healthie_api.create_document(
                patient_id=healthie_id,
                filepath=self.pdf_path,
                desc=f"Requisition for {email}",
                include_in_charting=False,
                display_name="Lab_Requisition"
            )
            logger.info(f"uploaded lab requisition:{self.pdf_path} to healthie_id: {healthie_id} & {email}: {r}")
        except Exception as e:
            logger.exception(f"send_requisition_to_healthie: error for user with email={email} healthie_id={healthie_id} with error: {e}")

    async def handle_type_req(self):
        drchrono_req_ts = self.visit.get("drchrono_req_ts")
        mrn = self.visit.get("mrn")
        if drchrono_req_ts is not None:
            drchrono_req_timestamp = datetime.datetime.strptime(drchrono_req_ts, '%Y-%m-%dT%H:%M:%S')
            if drchrono_req_timestamp >= self.ts:
                logger.debug(f"Not a newer REQ: {self.id}. Skipping...")
                return
        self.download_pdf()
        # upload to S3
        object_name = f"{str(uuid.uuid4())}.pdf"
        if self.upload_file(object_name=object_name):
            bucket_check = check_file_in_s3(object_name)
            file_url = create_presigned_url(bucket_check, object_name)
        else:
            logger.warning(f"Upload to S3 failed for REQ: {self.id}")
            return
        logger.info(f"Updating visits table with req for mrn={mrn}, req={file_url}, ts={self.timestamp}")
        db.update_visits_drchrono_req(req=file_url, ts=self.timestamp, mrn=mrn)

        if self.visit.get("is_healthie") == "1" and self.visit.get("healthie_id"):
            await self.send_requisition_to_healthie()

        address = self.visit.get("address").lower()
        if any(["quest diagnostics" in address, "labcorp" in address]) and "home visit" not in address:
            # if file_url:
            first_name = self.visit.get("patient_name")
            message = f"""
            Hi {first_name}, your lab order is ready! Click here to download your order form.
            Show this to the lab when you arrive!
            
            {file_url}
            """
            phone = self.visit.get("phone")
            try:
                self.send_notification(phone, message)
            except Exception as e:
                logger.exception("AWS SNS sending SMS => SMS NOT SENT (FAILURE) => "+str(e))

    def send_notification(self, to_phone: str, message: str):
        """Send text notification"""
        try:
            logging.info(f"Sending notification to {to_phone}...")
            send_text_message(to_phone, message)
        except Exception as e:
            logging.exception(e)

    def is_frontend_case(self):
        """Return True if case should be created from frontend"""
        for test in self.abnormal_tests:
            for frontend_test in FRONTEND_TEST_LIST:
                if frontend_test in test:
                    return True
        return False

    def is_weight_loss_test(self):
        a1c = False
        tsh = False
        creatinine = False
        for result in self.results:
            observation_description = result.get('observation_description')
            lab_test_name = OBSERVATION_TO_TEST_NAME.get(observation_description.lower(), "")
            if 'Hemoglobin A1c' in lab_test_name:
                a1c = True
            if 'TSH' == lab_test_name:
                tsh = True
            if 'Creatinine' in lab_test_name:
                creatinine = True

        if a1c and tsh and creatinine:
            phone = self.visit.get("phone")
            first_name = self.visit.get("patient_name", "") or ""
            if phone:
                try:
                    self.send_notification(phone, weight_loss_message.format(first_name))
                    logger.debug("is_weight_loss_test ==> sending weight lost test SMS => SMS SENT (Successful)")
                except Exception:
                    logger.exception("is_weight_loss_test ==> Twilio sending SMS => SMS NOT SENT (FAILURE)")
        return a1c and tsh and creatinine

    def is_accutane_test(self):
        ALT = False
        for result in self.results:
            observation_description = result.get('observation_description')
            lab_test_name = OBSERVATION_TO_TEST_NAME.get(observation_description.lower(), "")
            if 'ALT' in lab_test_name:
                ALT = True
        return ALT

    async def send_result_to_healthie(self):
        """upload results to healthie"""
        try:
            healthie_id = self.visit.get("healthie_id")
            email = self.visit.get('email')
            r = await healthie_api.create_document(
                patient_id=healthie_id,
                filepath=self.pdf_path,
                desc=f"Final results for {email}",
                include_in_charting=False,
                display_name="Final_Lab_Results"
            )
            logger.info(f"uploaded final result:{self.pdf_path} to healthie_id: {healthie_id} & {email}: {r}")
        except Exception as e:
            logger.exception(f"send_result_to_healthie: error for user with email={email} healthie_id={healthie_id} with error: {e}")

    async def handle_type_res(self):
        from airtable_api import create_new_record
        drchrono_res_ts = self.visit.get("drchrono_res_ts")
        mrn = self.visit.get("mrn")
        # check if a new RES
        logger.info("drchrono_sync_new: handle_type_res for mrn=" + str(mrn))
        if drchrono_res_ts is not None:
            drchrono_res_timestamp = datetime.datetime.strptime(drchrono_res_ts, '%Y-%m-%dT%H:%M:%S')
            if drchrono_res_timestamp >= self.ts:
                logger.debug(f"drchrono_sync_new: Not a newer RES: {self.id}. Skipping...")
                return

        # download file
        self.download_pdf()

        # upload to S3
        object_name = f"{str(uuid.uuid4())}.pdf"
        if self.upload_file(object_name=object_name):
            file_url = self.get_s3_url(object_name=object_name)
        else:
            logger.warning(f"drchrono_sync_new: Upload to S3 failed for RES: {self.id}")
            return

        # update db
        logger.info(f"drchrono_sync_new: Updating visits table with res for mrn={mrn}, res={file_url}, ts={self.timestamp}")
        db.update_visits_drchrono_res(res=file_url, ts=self.timestamp, mrn=mrn)

        # notify patient for new results
        self.notify_patient()

        # fetch results
        self._fetch_lab_results_()

        # find abnormal results
        self.find_abnormal_results()

        sent = False
        if self.are_results_final():
            logger.info("drchrono_sync_new: Lab results are final for mrn=" + str(mrn))
            try:
                db_session: Session = next(get_db())
                if not CMMPAResultsCrud.find_by_mrn(db_session=db_session, mrn=self.visit.get("mrn")):
                    ts = datetime.datetime.now()
                    CMMPAResultsCrud.create_with_values(
                        db_session,
                        mrn=self.visit.get("mrn"),
                        email=self.visit.get("email"),
                        name=self.visit.get("patient_name"),
                        date_added=ts.strftime("%Y/%m/%d %H:%M:%S"),
                        mounjaro=None,
                        ozempic=None,
                        rybelsus=None,
                        saxenda=None,
                        wegovy=None,
                        preferred_drug_approved=False,
                        rejected_all=False,
                        date_started=None
                    )
                    logger.info("drchrono_sync_new: New row created in pa_results for mrn=" + str(mrn))
                airtable_payload = {
                    "Patient Name": self.visit.get("patient_name"),
                    "Email": self.visit.get("email"),
                    "Stripe Payment ID": "",
                    "Phone Number": self.visit.get("phone"),
                    "Date Purchased": str(date.today()),
                    "Patient Address": self.visit.get("address"),
                    "Status": "Open"
                }
                insurance_data_list = self.visit.get("insurance", "").strip().replace(" ", "").split(',')
                if len(insurance_data_list) == 3:
                    airtable_payload["Patient Insurance Name"] = insurance_data_list[0]
                    airtable_payload["Insurance ID #"] = insurance_data_list[1]
                    airtable_payload["Insurance Group #"] = insurance_data_list[2]

                pharmacy_data_list = self.visit.get("pharmacy_ins_patient", "").strip().replace(" ", "").split(',')
                if len(pharmacy_data_list) == 3:
                    airtable_payload["Rx Bin"] = pharmacy_data_list[0]
                    airtable_payload["Rx PCN"] = pharmacy_data_list[1]
                    airtable_payload["Rx Group"] = pharmacy_data_list[2]

                if self.visit.get("consumer_notes") in [
                    "GLP-1 Weight Loss Complete Program",
                    "GLP-1 Weight Loss Program"
                ]:
                    if self.visit.get("consumer_notes") == "GLP-1 Weight Loss Complete Program":
                        airtable_payload["Subscription Type"] = "GLP Weight Loss Complete"
                    if self.visit.get("consumer_notes") == "GLP-1 Weight Loss Program":
                        airtable_payload["Subscription Type"] = "GLP Weight Loss"
                    create_new_record(airtable_payload)
                    logger.info("drchrono_sync_new: New row created in airtable for mrn=" + str(mrn))
            except Exception as e:
                logger.exception("drchrono_sync_new: create_new_record => record not created: " + str(e))
            logger.debug(f"drchrono_sync_new: All results in Final status for lab_order: {self.lab_order}.")
            if len(self.abnormal_tests) > 0:
                abnormal_tests_str = ';'.join(self.abnormal_tests)
                logger.info(
                    f"drchrono_sync_new: Updating visits table with drchrono_abnormal_tests={abnormal_tests_str} for mrn={mrn}")
                db.update_visits_drchrono_abnormal_tests(tests=abnormal_tests_str, mrn=mrn)
            # Send to mdi case if necessary
            if self.visit.get("is_healthie") == "0":
                self.update_mdi_case()
            # results are final and not sent to mdintegrations then send
            # if self.visit.get("drchrono_result_to_mdint") != "sent":
            #     if (not self.is_weight_loss_test()) and (not self.is_frontend_case()) and (not self.is_accutane_test()):
            #         sent = self.send_results_to_mdintegrations(final=True)
            logger.info("drchrono_sync_new: checking healthie values for email=" + str(self.visit.get('email')) + " is_healthie=" + str(self.visit.get('is_healthie')) + " healthie_id=" + str(self.visit.get('healthie_id')))
            if self.visit.get("is_healthie") == "1" and self.visit.get("healthie_id"):
                logger.info("drchrono_sync_new: sending result to healthie for mrn=" + str(mrn))
                await self.send_result_to_healthie()

                healthie_id = self.visit.get('healthie_id')

                glucose_value = ''
                glucose_status = None
                a1c_value = ''
                a1c_status = None

                try:
                    if healthie_id:
                        if self.visit.get('weight') and self.visit.get('height'):
                            bmi = (self.visit.get('weight') / (self.visit.get('height') * self.visit.get('height'))) * 703.0
                            if bmi < 27:
                                bmi_status = "bmi_status_1"
                            elif bmi >= 27 and bmi < 30:
                                bmi_status = "bmi_status_2"
                            elif bmi >= 30 and bmi < 35:
                                bmi_status = "bmi_status_3"
                            elif bmi >= 35:
                                bmi_status = "bmi_status_4"
                        else:
                            bmi = ''
                            bmi_status = None

                        for result in self.results:
                            if result.get('observation_description') == "Glucose" or result.get(
                                    'observation_description') == "Glucose SerPl-mCnc":  # one for labcorp and one for quest, respectively
                                try:
                                    glucose_value = result.get('value')
                                    glucose_int = int(glucose_value)
                                    if glucose_int < 100:
                                        glucose_status = "fasting_glucose_status_1"
                                    elif glucose_int >= 100 and glucose_int < 120:
                                        glucose_status = "fasting_glucose_status_2"
                                    elif glucose_int >= 120:
                                        glucose_status = "fasting_glucose_status_3"
                                except Exception as e:
                                    logger.error('Cannot parse int from string')
                            elif result.get('observation_description') == "Hemoglobin A1c" or result.get(
                                    'observation_description') == "HbA1c MFr Bld":  # one for labcorp and one for quest, respectively
                                try:
                                    a1c_value = result.get('value')
                                    a1c_float = float(a1c_value)
                                    if a1c_float < 5.7:
                                        a1c_status = "a1c_status_1"
                                    elif a1c_float >= 5.7 and a1c_float < 6.4:
                                        a1c_status = "a1c_status_2"
                                    elif a1c_float >= 6.4:
                                        a1c_status = "a1c_status_3"
                                except Exception as e:
                                    logger.error('Cannot parse float from string')

                        form_dict = {
                            "user_id": healthie_id,
                            "finished": True,
                            "custom_module_form_id": "1188048",
                            "form_answers": [{
                                "custom_module_id": "15003592",
                                "answer": a1c_value,
                                "user_id": healthie_id
                            },
                                {
                                    "custom_module_id": "15003593",
                                    "answer": a1c_status,
                                    "user_id": healthie_id
                                },
                                {
                                    "custom_module_id": "15003594",
                                    "answer": glucose_value,
                                    "user_id": healthie_id
                                },
                                {
                                    "custom_module_id": "15003595",
                                    "answer": glucose_status,
                                    "user_id": healthie_id
                                },
                                {
                                    "custom_module_id": "15032427",
                                    "answer": str(bmi),
                                    "user_id": healthie_id
                                },
                                {
                                    "custom_module_id": "15005094",
                                    "answer": bmi_status,
                                    "user_id": healthie_id
                                }]
                        }
                        if a1c_status or glucose_status:
                            healthie.creating_filled_out_forms(form_dict)
                            logger.info(
                            f'created form with id=1188048 and healthie_id={healthie_id} glucose_status={str(glucose_status)} glucose_value={str(glucose_value)} a1c_status={str(a1c_status)} a1c_value={a1c_value}')
                        else:
                            logger.info("Healthie form not sending as glucose_status and a1c_status are None")
                    else:
                        logger.error('healthie pa form => no healthie id associated with this customer')
                except Exception as e:
                    logger.exception(e)

                # if it is the first lab order, send an eb_check
                if self.visit.get("is_second_lab_order") == "0" or self.visit.get("is_second_lab_order") is None or self.visit.get("is_second_lab_order") == '':
                    try:
                        data_dict = {
                            "user_id": "1627246",
                            "content": "EB_CHECK",
                            "client_id": self.visit.get("healthie_id"),
                            "due_date": date.today().strftime('%Y-%m-%d'),
                            "reminder": {
                                "is_enabled": True,
                                "interval_type": "daily",
                                "interval_value": "friday",
                                "remove_reminder": True
                            }
                        }
                        logger.info(f"drchrono_sync_new: creating task on healthie: {data_dict}")
                        r = healthie.create_task(data_dict)
                        logger.debug(r)
                    except Exception as e:
                        logger.exception(
                            "healthie create task => task not created: " + str(e)
                        )
                # otherwise, send new lab task but not eb check
                else:
                    try:
                        data_dict = {
                            "user_id": "1627246",
                            "content": "NEW LAB RESULTS",
                            "client_id": self.visit.get("healthie_id"),
                            "due_date": date.today().strftime('%Y-%m-%d'),
                            "reminder": {
                                "is_enabled": True,
                                "interval_type": "daily",
                                "interval_value": "friday",
                                "remove_reminder": True
                            }
                        }
                        logger.info(f"drchrono_sync_new: creating task on healthie: {data_dict}")
                        r = healthie.create_task(data_dict)
                        logger.debug(r)
                    except Exception as e:
                        logger.exception(
                            "drchrono_sync_new: healthie create task => task not created: " + str(e)
                        )
        else:
            # results are not final
            if self.visit.get("is_healthie") != "1" and \
                    self.visit.get("drchrono_result_to_mdint") != "sent" and len(self.abnormal_tests) > 0:
                if self.is_abnormal_test_urgent():
                    sent = self.send_results_to_mdintegrations(final=False)
            else:
                logger.debug(f"drchrono_sync_new: Some results in P/I status for lab_order: {self.lab_order}. skipping...")

        if sent:
            logger.info(f"drchrono_sync_new: Updating visits table with drchrono_result_to_mdint to 'sent' for mrn={mrn}")
            db.update_visits_drchrono_result_to_mdint(mrn=mrn, sent=True)

    def is_abnormal_test_urgent(self):
        """Return True if any abnormal test is urgent"""
        for test in self.abnormal_tests:
            if test in URGENT_TEST_LIST:
                return True
        return False

    def notify_patient(self):
        try:
            logger.info("drchrono_sync_new: Notifying patient with email=" + str(self.visit.get('email')))
            patient_name = self.visit.get("patient_name")
            recipient = self.visit.get("email")
            subject = 'Test Results Available'
            content = f"""
                        Hi {patient_name},

                        Results from your Next Medical visit have been uploaded. 
                        Please visit www.joinnextmed.com/login to view them.'

                        Thanks & Regards,
                        """
            send_text_email(sender='team@joinnextmed.com', recipient=recipient, subject=subject, content=content)
        except Exception as e:
            logger.exception(e)
        try:
            phone = self.visit.get("phone")
            patient_name = self.visit.get("patient_name")
            logger.debug(f"Sending msg to {patient_name} on {phone}...")
            db.send_patient_message(patient_name, "Dr. Marc Serota", phone, "result")
            if self.visit.get("drchrono_result_notify") != "sent":
                db.update_visits_drchrono_result_notify(mrn=self.visit.get("mrn"), sent=True)
        except Exception as e:
            logger.exception(e)

    def _get_medication_(self, disease):
        medication_dict = {
            'Chlamydia': [{
                'medicine': 'Azithromycin (oral - tablet)',
                'id': '4b546b54-b892-4581-8dc2-38040c5deaf8',
                'type': 'Medication'
            }],
            'Gonnorhea': [{
                'medicine': 'Cefixime (oral - capsule)',
                'id': '2681002b-49ba-4874-ab05-e4f6f7488f85',
                'type': 'Medication'
            }],
            'Trichomoniasis': [{
                'medicine': 'metroNIDAZOLE (oral - tablet)',
                'id': '52edad60-5426-4fbe-a261-a73947494073',
                'type': 'Medication'
            }],
            'Mycoplasma': [{
                'medicine': 'Doxycycline hyclate 100 mg',
                'id': 'dfcf9870-5beb-474c-8347-aa831653b9dd',
                'type': 'Compound'
            },
                {
                    'medicine': 'Azithromycin 5 Day Dose Pack (oral - tablet)',
                    'id': '61b997d8-762f-44b6-bbb6-3f9e724ddb3f',
                    'type': 'Medication'
                }],
            'Ureaplasma': [{
                'medicine': 'Azithromycin (oral - tablet)',
                'id': '4b546b54-b892-4581-8dc2-38040c5deaf8',
                'type': 'Medication'
            }],
            # female
            'UTI 1': {
                'medicine': 'Nitrofurantoin Macrocrystals (oral - capsule)',
                'id': 'cf500d27-7bd4-41a1-ac56-3cab125edb05',
                'type': 'Medication'
            },
            # male
            'UTI 0': {
                'medicine': 'Doxycycline hyclate 100 mg',
                'id': 'dfcf9870-5beb-474c-8347-aa831653b9dd',
                'type': 'Compound'
            }
        }

        return medication_dict.get(disease)

    def _attach_prescription_(self):
        case_prescriptions = []
        for test in self.abnormal_tests:
            medication = self._get_medication_(test)
            if medication is None:
                continue

            for medicine in medication:
                if medicine['type'] == 'Medication':
                    prescription = {
                        'partner_medication_id': medicine['id'],
                    }
                else:
                    prescription = {
                        'partner_compound_id': medicine['id'],
                    }
                case_prescriptions.append(prescription)

        # check for UTI
        if len(case_prescriptions) == 0:
            # attach prescription in MDI case #1329 => all conditions should be 'OR'
            if 'Leukocyte Esterase' in self.abnormal_tests or 'WBC Esterase' in self.abnormal_tests or \
                    'White Blood Cells' in self.abnormal_tests or 'Bacteria' in self.abnormal_tests or \
                    'Nitrite' in self.abnormal_tests:
                test = f"UTI {self.visit.get('sex', 0)}"
                medication = self._get_medication_(test)
                if medication['type'] == 'Medication':
                    prescription = {
                        'partner_medication_id': medication['id'],
                    }
                else:
                    prescription = {
                        'partner_compound_id': medication['id'],
                    }
                case_prescriptions.append(prescription)
            self._remove_urinalysis_components_()

        return case_prescriptions

    def _remove_urinalysis_components_(self):
        urinalysis_components = ['Color', 'Appearance', 'Specific Gravity', 'pH', 'Glucose', 'Bilirubin', 'Ketones',
                                 'Occult Blood', 'Protein', 'Nitrite', 'WBC Esterase', 'Leukocyte Esterase',
                                 'Urobilinogen', 'White Blood Cells', 'Red Blood Cells', 'Epithelial Cells',
                                 'Squamous Epithelial Cells', 'Casts', 'Hyaline Cast', 'Bacteria',
                                 'CALCIUM OXALATE CRYSTALS'
                                 ]
        for c in urinalysis_components:
            if c in self.abnormal_tests:
                self.abnormal_tests.remove(c)

    def _fetch_mdi_service_list_(self):
        try:
            if MDI_SERVICE_DICT.get(self.mdi_account_type):
                return
            services_list = self.mdi_api.list_services()
            service_dict = {i["title"]: i["partner_service_id"] for i in services_list}
            MDI_SERVICE_DICT[self.mdi_account_type] = service_dict
        except Exception as e:
            logger.exception(e)

    def _get_mdi_case_services_(self, abnormal=False):
        case_services = []
        self._fetch_mdi_service_list_()
        service_dict = MDI_SERVICE_DICT.get(self.mdi_account_type, {})

        for test in self.visit.get('consumer_notes').split(','):
            try:
                test = test.strip()
                if ' x ' in test:
                    test = test[4:]
                if abnormal:
                    test = f'{test} (abnormal results)'
                else:
                    test = f'{test} (normal results)'
                service_id = service_dict.get(test)
                if service_id:
                    logger.debug(f"adding {service_id} for {test}")
                    case_service = {"partner_service_id": service_id}
                    case_services.append(case_service)
            except Exception as e:
                logger.exception(e)
        return case_services

    def _get_md_data_(self, file_id):
        case_prescriptions = self._attach_prescription_()
        # MDI herpes question #1277
        herpes_question = None
        if 'Herpes 1' in self.abnormal_tests and 'Herpes 2' in self.abnormal_tests:
            herpes_question = {
                'question': "HERPES POSITIVE",
                'answer': "HERPES 1 & HERPES 2",
                'type': "string",
                'important': True,
            }
        elif 'Herpes 2' in self.abnormal_tests:
            herpes_question = {
                'question': "HERPES POSITIVE",
                'answer': "HERPES 2",
                'type': "string",
                'important': True,
            }
        elif 'Herpes 1' in self.abnormal_tests:
            herpes_question = {
                'question': "HERPES POSITIVE",
                'answer': "HERPES 1",
                'type': "string",
                'important': True,
            }

        # herpes 1 as abnormal #1260: do not consider Herpes 1 as abnormal
        if 'Herpes 1' in self.abnormal_tests:
            logger.debug("Not considering Herpes 1 as abnormal.")
            self.abnormal_tests.remove('Herpes 1')

        case_services = []
        # mark abnormal if prescription is attached
        if len(case_prescriptions) > 0:
            abnormal_result = 'YES'
            case_services = self._get_mdi_case_services_(abnormal=True)
        elif len(self.abnormal_tests) > 0:
            abnormal_result = 'YES'
            case_services = self._get_mdi_case_services_(abnormal=True)
        else:
            abnormal_result = 'NO'
            case_services = self._get_mdi_case_services_(abnormal=False)
        patient_symptoms = self.visit.get("patient_symptoms")
        if patient_symptoms is None:
            patient_symptoms = 'NA'
        elif len(patient_symptoms) == 0:
            patient_symptoms = 'NA'
        case_files = [file_id]
        questions = [
            {
                'question': "RESULT REVIEW",
                'answer': "REVIEW RESULTS",
                'type': "string",
                'important': True,
            },
            {
                'question': "ABNORMAL RESULT",
                'answer': abnormal_result,
                'type': "string",
                'important': True,
            },
            {
                'question': "SYMPTOMS",
                'answer': patient_symptoms,
                'type': "string",
                'important': True,
            }
        ]
        if herpes_question is not None:
            questions.append(herpes_question)

        data = {
            'patient_id': self.visit.get("patient_id_md"),
            'case_files': case_files,
            'case_questions': questions,
        }
        clinician_id = self._get_md_clinician_id()
        if clinician_id is not None:
            data['clinician_id'] = clinician_id
        if len(case_prescriptions) > 0:
            data['case_prescriptions'] = case_prescriptions

        if case_services:
            data['case_services'] = case_services

        return data

    def _get_md_clinician_id(self):
        patient_id_md = self.visit.get("patient_id_md")
        if patient_id_md is None or patient_id_md == 'None':
            logger.warning("patient_id_md is None.")
            return None
        try:
            response = self.mdi_api.get_patient_cases(patient_id_md)
            if 'data' not in response:
                logger.debug(response)
                return None

            for case in response['data']:
                clinician_id = case['case_assignment']['clinician']['clinician_id']
                return clinician_id

        except Exception as e:
            logger.exception(e)
        return None

    def _herpes_abnormal_tests_(self):
        """Return True if Herpes 1 or 2 or both in abnormal_tests"""
        if 'Herpes 1' in self.abnormal_tests or 'Herpes 2' in self.abnormal_tests and len(self.abnormal_tests) <= 2:
            return True
        return False

    def detect_mdi_account_type(self):
        """Detect mdi account type & set mdi instance"""
        patient_id_md = self.visit.get("patient_id_md")
        if patient_id_md and patient_id_md != 'None':
            logger.debug(f"Detecting account type for patient_id_md: {patient_id_md}")
            for mdi_account_type, mdi_api in mdi_instance_dict.items():
                try:
                    res = mdi_api.get_patient(patient_id_md)
                    if 'patient_id' in res:
                        self.mdi_api = mdi_api
                        self.mdi_account_type = mdi_account_type
                        logger.info(f"Detected account type: {mdi_account_type} for patient_id_md: {patient_id_md}")
                        return True
                except Exception as e:
                    logger.exception(e)
        md_case_id = self.visit.get("md_case_id")
        if md_case_id and md_case_id != 'None':
            logger.debug(f"Detecting account type for md_case_id: {md_case_id}")
            for mdi_account_type, mdi_api in mdi_instance_dict.items():
                try:
                    res = mdi_api.get_case(case_id=md_case_id)
                    if 'case_id' in res:
                        self.mdi_api = mdi_api
                        self.mdi_account_type = mdi_account_type
                        logger.info(f"Detected account type: {mdi_account_type} for md_case_id: {md_case_id}")
                        return True
                except Exception as e:
                    logger.exception(e)
        return False

    def send_results_to_mdintegrations(self, final=True):
        # herpes results -> prescription workflow #1297
        if final is True:
            if self._herpes_abnormal_tests_() is True:
                logger.info(f"Not sending case to MDI: {self.abnormal_tests}")
                return False
        try:
            if self.mdi_api is None:
                self.detect_mdi_account_type()
            file_id = self.create_mdi_file()
            if file_id is None:
                return False
            data = self._get_md_data_(file_id)
            logger.debug(f"creating case on mdintegrations: {data}")
            response = self.mdi_api.create_case(data)
            logger.debug(response)
            if 'error' in response:
                return False
            md_case_id = response.get('case_id')
            mrn = self.visit.get('mrn')
            logger.info(f"saving case_id: {md_case_id} to mrn: {mrn}")
            db.update_visits_md_case_id(mrn=mrn, md_case_id=md_case_id)
            return True
        except Exception as e:
            logger.exception(e)
        return False

    def create_mdi_file(self):
        if not os.path.exists(self.pdf_path):
            logger.warning(f"{self.pdf_path} doesn't exist.")
            return None
        logger.debug(f"Creating file on mdintegrations: {self.pdf_path}")
        with open(self.pdf_path, 'rb') as f:
            response = self.mdi_api.create_file(f)
            logger.debug(response)
            file_id = response.get('file_id')
            return file_id

    def update_mdi_case(self):
        try:
            if self.mdi_api is None:
                self.detect_mdi_account_type()
            md_case_id = self.visit.get("md_case_id")
            if md_case_id is None or md_case_id == 'None' or md_case_id == '':
                mrn = self.visit.get('mrn')
                logger.warning(f"md_case_id not found for {mrn}")
                return False
            file_id = self.create_mdi_file()
            if file_id is None:
                return False
            logger.debug(f"adding file: {file_id} to case: {md_case_id}...")
            res = self.mdi_api.add_file_to_case(md_case_id, file_id)
            logger.debug(res)
        except Exception as e:
            logger.exception(e)
        return False

    async def workflow(self):
        if self.patient_id is None or self.patient_id == 'None':
            logger.warning("patient_id is None. skipping...")
            return
        # get all rows from visits table for this patient
        self.visits = db.get_visits_all_rows_by_patient_id(self.patient_id)
        if len(self.visits) == 0:
            logger.error("visit not found. skipping...")
            return
        self.visit = self.visits[0]
        for visit in self.visits[1:]:
            try:
                server_date_time = datetime.datetime.strptime(visit.get('server_date_time'), '%d/%m/%Y %H:%M:%S')
                if server_date_time >= datetime.datetime.strptime(self.visit.get('server_date_time'), '%d/%m/%Y %H:%M:%S'):
                    self.visit = visit
            except Exception as e:
                logger.exception(e)
        if self.type == 'REQ':
            await self.handle_type_req()
        elif self.type == 'RES':
            await self.handle_type_res()
        else:
            logger.error(f"unknown type={self.type}")

        self.delete_pdf()


async def main():
    logger.info("Started")

    lab_docs = fetch_lab_documents()
    lab_docs.reverse()

    for lab_doc in lab_docs:
        try:
            logger.debug(lab_doc)
            lab_doc_obj = LabDocument(**lab_doc)
            await lab_doc_obj.workflow()
        except Exception as e:
            logger.exception(e)
    logger.info("Finished")
    logging.shutdown()


async def run_workflow_between(start_datetime: str, end_datetime: str):
    """Run workflow between start_datetime & end_datetime"""
    logger.info("Started")

    lab_docs = fetch_lab_documents_between(start_datetime, end_datetime)
    lab_docs.reverse()

    for lab_doc in lab_docs:
        try:
            logger.debug(lab_doc)
            lab_doc_obj = LabDocument(**lab_doc)
            await lab_doc_obj.workflow()
        except Exception as e:
            logger.exception(e)

    logger.info("Finished")
    logging.shutdown()


async def run_doc(lab_doc):
    lab_doc_obj = LabDocument(**lab_doc)
    await lab_doc_obj.workflow()


if __name__ == '__main__':
    asyncio.run(main())
    # run_workflow_between('2022-08-04 00:00:00', '2022-08-07 00:00:00')
