import os
import requests
import zipfile
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
TEMP_DIR = "temp-file"
FINAL_CSV = "consolidado_despesas.csv"
FINAL_ZIP = "consolidado_despesas.zip"

def setup_folders():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def get_latest_quarters(limit=3):
    try:
        response = requests.get(BASE_URL, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [urljoin(BASE_URL, a['href']) for a in soup.find_all('a') if '/' in a['href'] and 'PDA' not in a['href']]
        return sorted(links, reverse=True)[:limit]
    except:
        return []

def download_and_extract(quarter_url):
    extracted_files = []
    try:
        resp = requests.get(quarter_url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        zip_links = [urljoin(quarter_url, a['href']) for a in soup.find_all('a') if a['href'].endswith('.zip')]

        for link in zip_links:
            file_name = link.split('/')[-1]
            file_path = os.path.join(TEMP_DIR, file_name)
            
            r = requests.get(link)
            with open(file_path, 'wb') as f:
                f.write(r.content)
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(TEMP_DIR)
                for n in zip_ref.namelist():
                    extracted_files.append((os.path.join(TEMP_DIR, n), quarter_url))
    except:
        pass
    return extracted_files

def process_file(file_path, source_url):
    if not file_path.lower().endswith(('.csv', '.txt')):
        return None

    try:
        df = pd.read_csv(file_path, sep=None, engine='python', encoding='latin1', on_bad_lines='skip')
        df.columns = [str(c).upper().strip() for c in df.columns]

        col_id = next((c for c in df.columns if any(x in c for x in ['CNPJ', 'REG_ANS', 'ID_OPERADORA'])), None)
        col_desc = next((c for c in df.columns if any(x in c for x in ['DESC', 'RAZAO', 'NOME', 'CONTA'])), None)
        col_valor = next((c for c in df.columns if any(x in c for x in ['VALOR', 'VL_SALDO', 'VL_EVENTO'])), None)

        if not col_id or not col_valor:
            return None

        temp_df = pd.DataFrame()
        temp_df['CNPJ'] = df[col_id].astype(str).str.replace(r'\D', '', regex=True)
        temp_df['RazaoSocial'] = df[col_desc].fillna('SEM DESCRICAO') if col_desc else 'DESPESA'
        temp_df['ValorDespesas'] = df[col_valor]

        if temp_df['ValorDespesas'].dtype == object:
            temp_df['ValorDespesas'] = temp_df['ValorDespesas'].astype(str).str.replace(',', '.')
        temp_df['ValorDespesas'] = pd.to_numeric(temp_df['ValorDespesas'], errors='coerce').fillna(0)

        temp_df = temp_df[temp_df['ValorDespesas'] > 0]

        ano = re.search(r'(\d{4})', source_url)
        tri = re.search(r'(\d)T|/(\d)/', source_url.upper())
        temp_df['Ano'] = ano.group(1) if ano else "2024"
        temp_df['Trimestre'] = (tri.group(1) or tri.group(2)) if tri else "1"

        return temp_df
    except:
        return None

def main():
    setup_folders()
    quarters = get_latest_quarters()
    print(f"Trimestres encontrados: {len(quarters)}")
    
    all_data = []
    for q in quarters:
        print(f"Processando: {q}")
        files = download_and_extract(q)
        for f, url in files:
            processed = process_file(f, url)
            if processed is not None and not processed.empty:
                all_data.append(processed)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        
        colunas = ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesas']
        final_df = final_df[colunas]

        final_df.to_csv(FINAL_CSV, index=False, sep=';', encoding='utf-8-sig')
        
        with zipfile.ZipFile(FINAL_ZIP, 'w') as z:
            z.write(FINAL_CSV)
        print(f"Sucesso! {FINAL_CSV} criado com {len(final_df)} linhas.")
    else:
        print("Nenhum dado foi processado. Verifique a conexão ou os arquivos da ANS.")

if __name__ == "__main__":
    main()