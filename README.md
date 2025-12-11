# Mini-projet — Analyse exploratoire du Bitcoin (BTC-USD)

Ce dossier contient le livrable du mini-projet 8PRO408 : un notebook EDA complet, une application Streamlit interactive et la documentation associée.

## 1. Préparer l'environnement

```bash
cd rendu
python -m venv .venv
.venv\Scripts\Activate.ps1  # PowerShell
pip install -r requirements.txt
```

## 2. Où trouver le jeu de données 

> Le jeu de données esy déjà présent dans le dossier data mais vous pouvez le retélécharger vous même

1. Télécharger depuis Kaggle : [Bitcoin Historical Data (1-min)](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data) (nécesssite un compte)
2. Copier le fichier `btcusd_1-min_data.csv` dans `rendu/data/`.

Le notebook et l'application Streamlit attendent exactement ce nom de fichier et utilisent les colonnes `Timestamp`, `Open`, `High`, `Low`, `Close`, `Volume`.

## 3. Livrables

### Notebook Jupyter

Ouvrir dans vscode, sinon:

```bash
jupyter lab bitcoin.ipynb
# ou
jupyter notebook bitcoin.ipynb
```

### Application Streamlit

```bash
streamlit run app_streamlit.py
```

### Rapport

`RAPPORT.pdf` existe aussi en markdown (je l'ai écrit en markdown puis converti avec ) `RAPPORT.md` 
