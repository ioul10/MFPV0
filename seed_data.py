"""Pré-charge la base avec les fichiers fournis."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from app import init_db, upsert_masi20, upsert_bulletin, DB_PATH

init_db()

# MASI 20
df_m = pd.read_excel("/mnt/user-data/uploads/MASI_20.xlsx", sheet_name=0)
df_m.columns = [str(c).strip() for c in df_m.columns]
n = upsert_masi20(df_m)
print(f"MASI 20 : {n} lignes insérées")

# Bulletin
xl = pd.ExcelFile("/mnt/user-data/uploads/Suivi_de_marché.xlsx")
print("Sheets:", xl.sheet_names)
df_market = pd.read_excel(xl, sheet_name="Marché des MSI20", header=2)
df_market.columns = [str(c).strip() for c in df_market.columns]
df_market = df_market.rename(columns={"Date ": "Date", "Clôture (1)": "Clôture"})
df_market = df_market.dropna(subset=["Date", "Ticker"])

df_tx = pd.read_excel(xl, sheet_name="Transactions", header=1)
df_tx.columns = [str(c).strip() for c in df_tx.columns]
df_tx = df_tx.dropna(subset=["Date"])

nq, nt = upsert_bulletin(df_market, df_tx)
print(f"Cotations : {nq}, Transactions : {nt}")
print(f"DB: {DB_PATH}")
