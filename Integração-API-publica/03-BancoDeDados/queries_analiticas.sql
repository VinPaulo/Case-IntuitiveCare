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


-- Query 1
WITH despesas_2023 AS (
    SELECT
        CAST(cnpj AS TEXT) AS cod_ans,
        SUM(valordespesas) AS total
    FROM despesas_consolidadas
    WHERE ano = 2023
      AND trimestre = 1
    GROUP BY cnpj
),
despesas_2025 AS (
    SELECT
        CAST(cnpj AS TEXT) AS cod_ans,
        SUM(valordespesas) AS total
    FROM despesas_consolidadas
    WHERE ano = 2025
      AND trimestre = 1
    GROUP BY cnpj
)
SELECT
    o.razao_social,
    d23.total AS valor_2023,
    d25.total AS valor_2025,
    ((d25.total - d23.total) / NULLIF(d23.total, 0)) * 100 AS crescimento_percentual
FROM despesas_2023 d23
INNER JOIN despesas_2025 d25
        ON d23.cod_ans = d25.cod_ans
INNER JOIN operadoras o
        ON CAST(o.registro_operadora AS TEXT) = d23.cod_ans
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- Query 2
SELECT 
    o.uf,
    SUM(d.valordespesas) AS despesa_total,
    AVG(d.valordespesas) AS media_por_operadora
FROM despesas_consolidadas d
INNER JOIN operadoras o 
        ON CAST(o.registro_operadora AS TEXT) = CAST(d.cnpj AS TEXT)
GROUP BY o.uf
ORDER BY despesa_total DESC
LIMIT 5;

-- Query 3

SELECT 
    o.razao_social, 
    SUM(d.valordespesas) AS total_despesas,
    o.uf
FROM despesas_consolidadas d
INNER JOIN operadoras o 
        ON CAST(o.registro_operadora AS TEXT) = CAST(d.cnpj AS TEXT)
GROUP BY o.razao_social, o.uf
HAVING SUM(d.valordespesas) > (
    SELECT AVG(total_acumulado) 
    FROM (
        SELECT SUM(valordespesas) AS total_acumulado 
        FROM despesas_consolidadas 
        GROUP BY cnpj
    ) AS subquery
)
ORDER BY total_despesas DESC;