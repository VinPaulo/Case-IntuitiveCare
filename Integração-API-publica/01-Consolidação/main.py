import os
import requests
import zipfile
import pandas as pd
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configurações
BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
TEMP_DIR = "temp-file"
OUTPUT_FILE = "consolidado_despesas.csv"

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def get_latest_zips(limit=3):
    try:
        response = requests.get(BASE_URL, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Filtra anos (diretórios numéricos)
        years = [urljoin(BASE_URL, a['href']) for a in soup.find_all('a') 
                 if a['href'].endswith('/') and a['href'].strip('/').isdigit()]
        
        target_zips = []
        for year_url in sorted(years, reverse=True):
            print(f"Verificando ano: {year_url}")
            resp = requests.get(year_url, timeout=30)
            s = BeautifulSoup(resp.text, 'html.parser')
            # Busca arquivos zip que seguem o padrão QT YYYY
            zips = [urljoin(year_url, a['href']) for a in s.find_all('a') 
                    if a['href'].lower().endswith('.zip') and re.search(r'[1-4]\s?T', a['href'].upper())]
            
            # Ordena zips do ano decrescente (ex: 4T, 3T...)
            target_zips.extend(sorted(zips, reverse=True))
            if len(target_zips) >= limit:
                break
        return target_zips[:limit]
    except Exception as e:
        print(f"Erro ao buscar arquivos: {e}")
        return []

def download_and_extract_zip(zip_url):
    extracted_files = []
    try:
        file_name = zip_url.split('/')[-1]
        file_path = os.path.join(TEMP_DIR, file_name)
        
        print(f"  Baixando: {file_name}")
        r = requests.get(zip_url, timeout=60)
        with open(file_path, 'wb') as f:
            f.write(r.content)
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(TEMP_DIR)
                for n in zip_ref.namelist():
                    extracted_files.append((os.path.join(TEMP_DIR, n), zip_url))
        except Exception as e:
            print(f"  Erro ao extrair {file_name}: {e}")
    except Exception as e:
        print(f"  Erro no download {zip_url}: {e}")
    return extracted_files

def process_file(file_path, source_url):
    if not file_path.lower().endswith(('.csv', '.txt', '.xlsx')):
        return None

    try:
        # Extração melhorada do Trimestre e Ano
        context_text = (source_url + "_" + os.path.basename(file_path)).upper()
        
        # Busca Trimestre (XT ou /X/) e Ano (4 dígitos)
        tri_match = re.search(r'([1-4])\s?T|/([1-4])/', context_text)
        ano_match = re.search(r'(20\d{2})', context_text)
        
        extracted_tri = (tri_match.group(1) or tri_match.group(2)) if tri_match else "1"
        extracted_ano = ano_match.group(1) if ano_match else "2024"

        try:
            if file_path.lower().endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path, sep=None, engine='python', encoding='latin1', on_bad_lines='skip')
        except Exception as e:
            print(f"    Falha na leitura de {os.path.basename(file_path)}: {e}")
            return None
        
        df.columns = [str(c).upper().strip() for c in df.columns]

        # Mapeamento dinâmico de colunas
        col_id = next((c for c in df.columns if any(x in c for x in ['CNPJ', 'REG_ANS', 'ID_OPERADORA'])), None)
        col_desc = next((c for c in df.columns if any(x in c for x in ['DESC', 'RAZAO', 'NOME', 'CONTA'])), None)
        col_valor = next((c for c in df.columns if any(x in c for x in ['VALOR', 'VL_SALDO', 'VL_EVENTO'])), None)

        if not col_id or not col_valor:
            return None

        temp_df = pd.DataFrame()
        temp_df['CNPJ'] = df[col_id].astype(str).str.replace(r'\D', '', regex=True)
        temp_df['RazaoSocial'] = df[col_desc].fillna('DESPESA') if col_desc else 'DESPESA'
        
        if df[col_valor].dtype == object:
            val_str = df[col_valor].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            temp_df['ValorDespesas'] = pd.to_numeric(val_str, errors='coerce').fillna(0)
        else:
            temp_df['ValorDespesas'] = pd.to_numeric(df[col_valor], errors='coerce').fillna(0)
            
        temp_df = temp_df[temp_df['ValorDespesas'] > 0]
        temp_df['Trimestre'] = extracted_tri
        temp_df['Ano'] = extracted_ano

        return temp_df
    except Exception as e:
        print(f"  Erro no processamento {os.path.basename(file_path)}: {e}")
        return None

def main():
    print("Iniciando Consolidação de Dados ANS...")
    zip_urls = get_latest_zips(limit=3)
    
    if not zip_urls:
        print("Nenhum arquivo encontrado.")
        return

    print(f"Arquivos para processar: {len(zip_urls)}")
    
    all_dfs = []
    for z_url in zip_urls:
        files = download_and_extract_zip(z_url)
        for f_path, url in files:
            df = process_file(f_path, url)
            if df is not None and not df.empty:
                print(f"    + {len(df)} registros de {os.path.basename(f_path)} ({df['Trimestre'].iloc[0]}T/{df['Ano'].iloc[0]})")
                all_dfs.append(df)

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8-sig')
        print(f"\nSucesso! {len(final_df)} registros salvos em {OUTPUT_FILE}")
    else:
        print("\nNenhum registro extraído.")

if __name__ == "__main__":
    main()