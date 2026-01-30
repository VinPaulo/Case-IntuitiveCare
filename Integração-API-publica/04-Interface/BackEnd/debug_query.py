from database import get_db
import sqlalchemy

db = next(get_db())

query = sqlalchemy.text("""
    WITH despesas_inicio AS (
        SELECT cnpj::text as cnpj_txt, SUM(valordespesas) as total 
        FROM despesas_consolidadas 
        WHERE ano = 2023 
        GROUP BY cnpj
    ),
    despesas_fim AS (
        SELECT cnpj::text as cnpj_txt, SUM(valordespesas) as total 
        FROM despesas_consolidadas 
        WHERE ano = 2024 OR ano = 2025
        GROUP BY cnpj
    )
    SELECT 
        o.razao_social,
        ((u.total - p.total) / NULLIF(p.total, 0)) * 100 as crescimento
    FROM despesas_inicio p
    JOIN despesas_fim u ON p.cnpj_txt = u.cnpj_txt
    JOIN operadoras o ON o.cnpj = p.cnpj_txt
    WHERE p.total > 0
    ORDER BY crescimento DESC
    LIMIT 5
""")

try:
    results = db.execute(query).mappings().all()
    print(f"Results count: {len(results)}")
    for row in results:
        print(row)
except Exception as e:
    print(f"Error: {e}")
