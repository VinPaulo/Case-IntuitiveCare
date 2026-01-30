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
def list_operadoras(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    query = db.execute(sqlalchemy.text("SELECT * FROM operadoras LIMIT :limit OFFSET :offset"), 
                       {"limit": limit, "offset": offset}).mappings().all()
    total = db.execute(sqlalchemy.text("SELECT COUNT(*) FROM operadoras")).scalar()
    
    return {
        "data": query,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/operadoras/{identificador}")
def get_operadora(identificador: str, db: Session = Depends(get_db)):
    query = sqlalchemy.text("SELECT * FROM operadoras WHERE cnpj = :id OR registro_ans::text = :id")
    result = db.execute(query, {"id": identificador}).mappings().first()
    if not result:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")
    return result

@app.post("/api/operadoras")
def create_operadora(data: dict, db: Session = Depends(get_db)):
    query = sqlalchemy.text("""
        INSERT INTO operadoras (registro_ans, razao_social, cnpj, uf) 
        VALUES (:reg, :rs, :cnpj, :uf)
    """)
    db.execute(query, {"reg": data['registro_ans'], "rs": data['razao_social'], "cnpj": data['cnpj'], "uf": data['uf']})
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

@app.get("/api/operadoras/{cnpj}/despesas")
def get_despesas_historico(cnpj: str, db: Session = Depends(get_db)):
    query = sqlalchemy.text("SELECT * FROM despesas_consolidadas WHERE cnpj::text = :cnpj ORDER BY ano DESC, trimestre DESC")
    result = db.execute(query, {"cnpj": cnpj}).mappings().all()
    return result

@app.get("/api/estatisticas")
def get_estatisticas(db: Session = Depends(get_db)):
    agg_query = sqlalchemy.text("SELECT SUM(valordespesas) as total, AVG(valordespesas) as media FROM despesas_consolidadas")
    agg_res = db.execute(agg_query).mappings().first()
    
    top_query = sqlalchemy.text("""
        SELECT o.razao_social, SUM(d.valordespesas) as total_despesa
        FROM despesas_consolidadas d
        JOIN operadoras o ON o.cnpj = d.cnpj::text
        GROUP BY o.razao_social
        ORDER BY total_despesa DESC LIMIT 5
    """)
    top_5 = db.execute(top_query).mappings().all()
    
    return {
        "total_geral": agg_res["total"],
        "media_geral": agg_res["media"],
        "top_5": top_5
    }

@app.get("/api/analise/crescimento")
def get_crescimento_despesas(db: Session = Depends(get_db)):
    query = sqlalchemy.text("""
        WITH despesas_inicio AS (
            SELECT cnpj as reg_ans, SUM(valordespesas) as total 
            FROM despesas_consolidadas 
            WHERE ano = 2023 
            GROUP BY cnpj
        ),
        despesas_fim AS (
            SELECT cnpj as reg_ans, SUM(valordespesas) as total 
            FROM despesas_consolidadas 
            WHERE ano = 2024 OR ano = 2025
            GROUP BY cnpj
        )
        SELECT 
            o.razao_social,
            ((u.total - p.total) / NULLIF(p.total, 0)) * 100 as crescimento
        FROM despesas_inicio p
        JOIN despesas_fim u ON p.reg_ans = u.reg_ans
        JOIN operadoras o ON o.registro_ans = p.reg_ans
        WHERE p.total > 0
        ORDER BY crescimento DESC
        LIMIT 5
    """)
    result = db.execute(query).mappings().all()
    return result