from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_read_operadoras_pagination():
    response = client.get("/api/operadoras?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert len(data["data"]) <= 5

def test_get_invalid_operadora():
    response = client.get("/api/operadoras/00000000000000")
    assert response.status_code == 404

def test_create_operadora_validation():
    invalid_data = {
        "registro_operadora": 12345,
        "cnpj": "12345678000199",
        "uf": "SP"
    }
    response = client.post("/api/operadoras", json=invalid_data)
    assert response.status_code == 422 

def test_estatisticas_resilience():
    response = client.get("/api/estatisticas")
    assert response.status_code == 200
    data = response.json()
    assert "total_geral" in data
    assert "top_5" in data
    assert isinstance(data["top_5"], list)

def test_cache_performance():
    import time
    
    start_1 = time.time()
    client.get("/api/estatisticas")
    duration_1 = time.time() - start_1
    
    start_2 = time.time()
    client.get("/api/estatisticas")
    duration_2 = time.time() - start_2
    
    assert duration_2 <= duration_1 or duration_2 < 0.01
