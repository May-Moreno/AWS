# Zero Trust: React + FastAPI

- `backend/`: FastAPI con arquitectura hexagonal (domain / application / infrastructure / api).
- `frontend/`: React + Vite, login y Dashboard protegido.
- `deploy/` y `setup.sh`: despliegue en EC2 (Nginx + systemd).

## Desarrollo local
```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ajusta los valores
set -a; source .env; set +a
uvicorn app.main:app --reload

cd frontend && npm install && npm run dev
```

## Despliegue en EC2
```bash
git clone https://github.com/USUARIO/REPO.git && cd REPO && ./setup.sh
```
