import pandas as pd
import requests
import os

CONSOLIDADO_CSV = "consolidado_despesas.csv"
OPERADORAS_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
CADASTRO_CSV = "cadastro_operadoras.csv"
RESULTADO_FINAL = "despesas_agregadas.csv"

def validar_cnpj(valor):
    cnpj = str(valor).replace('.', '').replace('-', '').replace('/', '').replace(' ', '').replace('"', '').zfill(14)
    if len(cnpj) != 14 or cnpj in [s * 14 for s in "0123456789"]:
        return False
    def calcula_digito(fatia, pesos):
        soma = sum(int(a) * b for a, b in zip(fatia, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    try:
        if int(cnpj[12]) != calcula_digito(cnpj[:12], pesos1): return False
        if int(cnpj[13]) != calcula_digito(cnpj[:13], pesos2): return False
    except: return False
    return True

def baixar_cadastro():
    try:
        r = requests.get(OPERADORAS_URL, timeout=30)
        if r.status_code == 200:
            with open(CADASTRO_CSV, 'wb') as f:
                f.write(r.content)
            return True
        return False
    except: return False

def processar_transformacao():
    if not os.path.exists(CONSOLIDADO_CSV): return
    if not os.path.exists(CADASTRO_CSV): baixar_cadastro()

    df = pd.read_csv(CONSOLIDADO_CSV, sep=';', encoding='utf-8-sig')
    
    df['VALOR_LIMPO'] = df['CNPJ'].astype(str).str.replace(r'\D', '', regex=True)
    df['IS_CNPJ_VALIDO'] = df['VALOR_LIMPO'].apply(validar_cnpj)
    
    df = df[df['ValorDespesas'] > 0].copy()
    df = df[df['RazaoSocial'].notna()]

    try:
        df_cad = pd.read_csv(CADASTRO_CSV, sep=';', encoding='latin1', quotechar='"')
        df_cad.columns = [str(c).strip().upper() for c in df_cad.columns]
        
        df_cad['CNPJ_KEY'] = df_cad['CNPJ'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(14)
        df_cad['REG_KEY'] = df_cad['REGISTRO_OPERADORA'].astype(str).str.replace(r'\D', '', regex=True)

        m1 = pd.merge(df, df_cad[['CNPJ_KEY', 'REG_KEY', 'REGISTRO_OPERADORA', 'MODALIDADE', 'UF', 'RAZAO_SOCIAL']], 
                      left_on='VALOR_LIMPO', right_on='CNPJ_KEY', how='left')
        
        
        m2 = pd.merge(df, df_cad[['REG_KEY', 'REGISTRO_OPERADORA', 'MODALIDADE', 'UF', 'RAZAO_SOCIAL']], 
                      left_on='VALOR_LIMPO', right_on='REG_KEY', how='left')
        
        df_final = m1.copy()
        mask = df_final['REG_KEY'].isna()
        df_final.loc[mask, ['REG_KEY', 'REGISTRO_OPERADORA', 'MODALIDADE', 'UF', 'RAZAO_SOCIAL']] = m2.loc[mask, ['REG_KEY', 'REGISTRO_OPERADORA', 'MODALIDADE', 'UF', 'RAZAO_SOCIAL']].values

        df_final = df_final.rename(columns={'REGISTRO_OPERADORA': 'RegistroANS', 'MODALIDADE': 'Modalidade'})

        
        df_quarterly = df_final.groupby(['RegistroANS', 'RAZAO_SOCIAL', 'UF', 'Ano', 'Trimestre'], dropna=False).agg({
            'ValorDespesas': 'sum'
        }).reset_index()

        agrupado = df_quarterly.groupby(['RegistroANS', 'RAZAO_SOCIAL', 'UF'], dropna=False).agg({
            'ValorDespesas': ['sum', 'mean', 'std']
        }).reset_index()

        agrupado.columns = ['RegistroANS', 'RazaoSocial', 'UF', 'TotalDespesas', 'MediaTrimestral', 'DesvioPadrao']
        agrupado['DesvioPadrao'] = agrupado['DesvioPadrao'].fillna(0)
        
        agrupado = agrupado.sort_values(by='TotalDespesas', ascending=False)
        
        agrupado = agrupado.drop_duplicates(subset=['RazaoSocial', 'UF'])

        CORRECTED_FINAL = "despesas_agregadas.csv"
        agrupado.to_csv(CORRECTED_FINAL, index=False, sep=';', encoding='utf-8-sig')
        
        FIXED_CONSOLIDADO = "fix_consolidado.csv"
        df_final[['CNPJ_KEY', 'RegistroANS', 'Trimestre', 'Ano', 'ValorDespesas', 'RazaoSocial_x']].to_csv(FIXED_CONSOLIDADO, index=False, sep=';', encoding='utf-8-sig')
        
        print(f"Sucesso: {CORRECTED_FINAL} e {FIXED_CONSOLIDADO} gerados.")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    processar_transformacao()