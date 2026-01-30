-- 1. CRIAÇÃO DAS TABELAS

CREATE TABLE operadoras (
    registro_ans VARCHAR(20) PRIMARY KEY,
    cnpj VARCHAR(14),
    razao_social VARCHAR(255),
    modalidade VARCHAR(100),
    uf CHAR(2)
);

CREATE TABLE despesas_consolidadas (
    id SERIAL PRIMARY KEY,
    registro_ans VARCHAR(20),
    trimestre INT,
    ano INT,
    valor_despesa DECIMAL(18,2), 
    descricao_conta VARCHAR(255),
    FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
);

CREATE TABLE despesas_agregadas (
    razao_social VARCHAR(255),
    uf CHAR(2),
    total_despesas DECIMAL(18,2),
    media_trimestral DECIMAL(18,2),
    desvio_padrao DECIMAL(18,2),
    PRIMARY KEY (razao_social, uf)
);

CREATE INDEX idx_despesas_reg_ans ON despesas_consolidadas(registro_ans);
CREATE INDEX idx_despesas_periodo ON despesas_consolidadas(ano, trimestre);

-- 2. IMPORTAÇÃO DE DADOS 

COPY operadoras(registro_ans, cnpj, razao_social, modalidade, uf) 
FROM 'Integração-API-publica/02-Validação/cadastro_operadoras.csv' 
DELIMITER ';' CSV HEADER ENCODING 'UTF8';

UPDATE despesas_consolidadas 
SET valor_despesa = CAST(REPLACE(valor_original_string, ',', '.') AS DECIMAL(18,2))
WHERE valor_original_string IS NOT NULL;



-- QUERIES

SELECT count(*) FROM operadoras;
SELECT count(*) FROM despesas_consolidadas;
SELECT count(*) FROM despesas_agregadas;

SELECT razaosocial, totaldespesas 
FROM despesas_agregadas 
ORDER BY totaldespesas DESC 
LIMIT 10;

SELECT cnpj::text FROM despesas_consolidadas LIMIT 5;
SELECT registro_operadora FROM operadoras LIMIT 5;

SELECT registro_ans, razao_social FROM operadoras LIMIT 10;

-- 1 

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
        ON CAST(o.registro_ans AS TEXT) = d23.cod_ans
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- 2

SELECT 
    o.uf,
    SUM(d.valordespesas) AS despesa_total,
    AVG(d.valordespesas) AS media_por_operadora
FROM despesas_consolidadas d
INNER JOIN operadoras o 
        ON CAST(o.registro_ans AS TEXT) = CAST(d.cnpj AS TEXT)
GROUP BY o.uf
ORDER BY despesa_total DESC
LIMIT 5;

-- 3

SELECT 
    o.razao_social, 
    SUM(d.valordespesas) AS total_despesas,
    o.uf
FROM despesas_consolidadas d
INNER JOIN operadoras o 
        ON CAST(o.registro_ans AS TEXT) = CAST(d.cnpj AS TEXT)
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