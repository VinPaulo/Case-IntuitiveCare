from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import sqlalchemy
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API ANS - Estágio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/operadoras")
def list_operadoras(page: int = 1, limit: int = 10, search: str = None, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    
    where_clause = ""
    params = {"limit": limit, "offset": offset}
    
    if search:
        where_clause = "WHERE razao_social ILIKE :search OR cnpj LIKE :search OR registro_operadora::text LIKE :search"
        params["search"] = f"%{search}%"
        
    query_str = f"SELECT *, registro_operadora as registro_ans FROM operadoras {where_clause} LIMIT :limit OFFSET :offset"
    total_str = f"SELECT COUNT(*) FROM operadoras {where_clause}"
    
    query = db.execute(sqlalchemy.text(query_str), params).mappings().all()
    total = db.execute(sqlalchemy.text(total_str), params).scalar()
    
    return {
        "data": query,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/operadoras/{identificador}")
def get_operadora(identificador: str, db: Session = Depends(get_db)):
    query = sqlalchemy.text("SELECT *, registro_operadora as registro_ans FROM operadoras WHERE cnpj = :id OR registro_operadora::text = :id")
    result = db.execute(query, {"id": identificador}).mappings().first()
    if not result:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    return result

@app.post("/api/operadoras")
def create_operadora(data: dict, db: Session = Depends(get_db)):
    query = sqlalchemy.text("""
        INSERT INTO operadoras (registro_operadora, razao_social, cnpj, uf) 
        VALUES (:reg, :rs, :cnpj, :uf)
    """)
    db.execute(query, {"reg": data.get('registro_operadora') or data.get('registro_ans'), "rs": data['razao_social'], "cnpj": data['cnpj'], "uf": data['uf']})
    db.commit()
    return {"message": "Operadora criada com sucesso!"}

@app.put("/api/operadoras/{cnpj}")
def update_operadora(cnpj: str, data: dict, db: Session = Depends(get_db)):
    query = sqlalchemy.text("UPDATE operadoras SET razao_social = :rs, uf = :uf WHERE cnpj = :cnpj")
    db.execute(query, {"rs": data['razao_social'], "uf": data['uf'], "cnpj": cnpj})
    db.commit()
    return {"message": "Operadora atualizada!"}

@app.delete("/api/operadoras/{cnpj}")
def delete_operadora(cnpj: str, db: Session = Depends(get_db)):
    query = sqlalchemy.text("DELETE FROM operadoras WHERE cnpj = :cnpj")
    db.execute(query, {"cnpj": cnpj})
    db.commit()
    return {"message": "Operadora excluída!"}

@app.get("/api/operadoras/{identificador}/despesas")
def get_despesas_historico(identificador: str, db: Session = Depends(get_db)):
    # Agrupamos por ano e trimestre para mostrar um resumo no histórico, como pede o PDF
    query = sqlalchemy.text("""
        SELECT ano, trimestre, SUM(valordespesas) as valordespesas
        FROM despesas_consolidadas 
        WHERE cnpj = :id OR registro_ans = :id 
        GROUP BY ano, trimestre 
        ORDER BY ano DESC, trimestre DESC
    """)
    result = db.execute(query, {"id": identificador}).mappings().all()
    return result

@app.get("/api/estatisticas")
def get_estatisticas(db: Session = Depends(get_db)):
    agg_query = sqlalchemy.text("SELECT SUM(valordespesas) as total, AVG(valordespesas) as media FROM despesas_consolidadas")
    agg_res = db.execute(agg_query).mappings().first()
    
    top_query = sqlalchemy.text("""
        SELECT o.razao_social, SUM(d.valordespesas) as total_despesa
        FROM despesas_consolidadas d
        JOIN operadoras o ON o.registro_operadora = d.registro_ans
        GROUP BY o.razao_social
        ORDER BY total_despesa DESC LIMIT 5
    """)
    top_5 = db.execute(top_query).mappings().all()
    
    return {
        "total_geral": agg_res["total"],
        "media_geral": agg_res["media"],
        "top_5": top_5
    }

@app.get("/api/analise/despesas-por-uf")
def get_despesas_por_uf(db: Session = Depends(get_db)):
    query = sqlalchemy.text("""
        SELECT 
            o.uf,
            SUM(d.valordespesas) AS total_despesa
        FROM despesas_consolidadas d
        JOIN operadoras o ON o.registro_operadora = d.registro_ans
        GROUP BY o.uf
        ORDER BY total_despesa DESC
        LIMIT 10
    """)
    result = db.execute(query).mappings().all()
    return result

@app.get("/api/analise/crescimento")
def get_crescimento_despesas(db: Session = Depends(get_db)):
    query = sqlalchemy.text("""
        WITH despesas_inicio AS (
            SELECT registro_ans as reg_ans, SUM(valordespesas) as total 
            FROM despesas_consolidadas 
            WHERE ano = 2023 
            GROUP BY registro_ans
        ),
        despesas_fim AS (
            SELECT registro_ans as reg_ans, SUM(valordespesas) as total 
            FROM despesas_consolidadas 
            WHERE ano = 2024 OR ano = 2025
            GROUP BY registro_ans
        )
        SELECT 
            o.razao_social,
            ((u.total - p.total) / NULLIF(p.total, 0)) * 100 as crescimento
        FROM despesas_inicio p
        JOIN despesas_fim u ON p.reg_ans = u.reg_ans
        JOIN operadoras o ON o.registro_operadora = p.reg_ans
        WHERE p.total > 0
        ORDER BY crescimento DESC
        LIMIT 5
    """)
    result = db.execute(query).mappings().all()
    return result