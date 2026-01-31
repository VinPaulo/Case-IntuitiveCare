DROP TABLE IF EXISTS despesas_agregadas;
DROP TABLE IF EXISTS despesas_consolidadas;
DROP TABLE IF EXISTS operadoras;

CREATE TABLE operadoras (
    registro_operadora VARCHAR(20) PRIMARY KEY,
    cnpj VARCHAR(20),
    razao_social VARCHAR(255),
    nome_fantasia VARCHAR(255),
    modalidade VARCHAR(100),
    logradouro VARCHAR(255),
    numero VARCHAR(50),
    complemento VARCHAR(255),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf CHAR(2),
    cep VARCHAR(20),
    ddd VARCHAR(10),
    telefone VARCHAR(20),
    fax VARCHAR(20),
    endereco_eletronico VARCHAR(255),
    representante VARCHAR(255),
    cargo_representante VARCHAR(255),
    regiao_de_comercializacao VARCHAR(10),
    data_registro_ans TIMESTAMP
);

CREATE TABLE despesas_consolidadas (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(20),
    registro_ans VARCHAR(20), 
    trimestre INT,
    ano INT,
    valordespesas DECIMAL(18,2), 
    descricao_conta VARCHAR(255),
    FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_operadora)
);

CREATE TABLE despesas_agregadas (
    razaosocial VARCHAR(255),     
    uf CHAR(2),
    totaldespesas DECIMAL(20,2),   
    mediatrimestral DECIMAL(20,2), 
    desviopadrao DECIMAL(20,2),    
    PRIMARY KEY (razaosocial, uf)
);

CREATE INDEX idx_despesas_reg_ans ON despesas_consolidadas(registro_ans);
CREATE INDEX idx_despesas_periodo ON despesas_consolidadas(ano, trimestre);
CREATE INDEX idx_despesas_cnpj ON despesas_consolidadas(cnpj);

-- Query 1: 5 operadoras com maior crescimento percentual
WITH despesas_por_periodo AS (
    SELECT 
        registro_ans,
        ano,
        trimestre,
        SUM(valordespesas) as total_tri
    FROM despesas_consolidadas
    GROUP BY registro_ans, ano, trimestre
),
periodos_extremos AS (
    SELECT 
         registro_ans,
         MIN(ano * 10 + trimestre) as primeiro_periodo,
         MAX(ano * 10 + trimestre) as ultimo_periodo
    FROM despesas_por_periodo
    GROUP BY registro_ans
)
SELECT 
    o.razao_social,
    dp_inicio.total_tri AS valor_inicial,
    dp_fim.total_tri AS valor_final,
    ((dp_fim.total_tri - dp_inicio.total_tri) / NULLIF(dp_inicio.total_tri, 0)) * 100 AS crescimento_percentual
FROM periodos_extremos pe
JOIN despesas_por_periodo dp_inicio ON pe.registro_ans = dp_inicio.registro_ans AND pe.primeiro_periodo = (dp_inicio.ano * 10 + dp_inicio.trimestre)
JOIN despesas_por_periodo dp_fim ON pe.registro_ans = dp_fim.registro_ans AND pe.ultimo_periodo = (dp_fim.ano * 10 + dp_fim.trimestre)
JOIN operadoras o ON o.registro_operadora = pe.registro_ans
WHERE dp_inicio.total_tri > 0
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- Query 2: Distribuição de despesas por UF
SELECT 
    o.uf,
    SUM(d.valordespesas) AS despesa_total,
    AVG(d.valordespesas) AS media_por_operadora
FROM despesas_consolidadas d
INNER JOIN operadoras o 
        ON o.registro_operadora = d.registro_ans
GROUP BY o.uf
ORDER BY despesa_total DESC
LIMIT 5;

-- Query 3: Operadoras acima da média em pelo menos 2 trimestres
WITH media_geral AS (
    SELECT AVG(total_tri) as valor_medio
    FROM (
        SELECT registro_ans, ano, trimestre, SUM(valordespesas) as total_tri
        FROM despesas_consolidadas
        GROUP BY registro_ans, ano, trimestre
    ) as sub
),
acima_da_media AS (
    SELECT 
        d.registro_ans,
        COUNT(*) as trimestres_acima
    FROM (
        SELECT registro_ans, ano, trimestre, SUM(valordespesas) as total_tri
        FROM despesas_consolidadas
        GROUP BY registro_ans, ano, trimestre
    ) d, media_geral m
    WHERE d.total_tri > m.valor_medio
    GROUP BY d.registro_ans
)
SELECT COUNT(*) as total_operadoras_acima_criterio
FROM acima_da_media
WHERE trimestres_acima >= 2;