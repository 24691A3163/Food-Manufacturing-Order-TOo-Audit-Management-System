# PRODUCTION DEPLOYMENT GUIDE
## Order-to-Audit ERP for Food Manufacturing

This guide documents how to deploy the ERP in production using PostgreSQL (or Supabase), FastAPI, and modern frontend static hosting (Nginx / Vercel / Netlify).

---

### 1. Database Setup (PostgreSQL / Supabase)

#### Option A: Supabase Managed PostgreSQL
1. Create a project at [supabase.com](https://supabase.com).
2. Go to **Project Settings** → **Database** and copy the **Connection string (URI)**.
3. In `backend/.env`, set:
   ```env
   DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
   ```

#### Option B: Self-Hosted PostgreSQL / Docker
```bash
docker run -d \
  --name food_erp_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=securepassword \
  -e POSTGRES_DB=food_erp \
  -p 5432:5432 \
  postgres:16-alpine
```
Then configure `DATABASE_URL`:
```env
DATABASE_URL="postgresql://postgres:securepassword@localhost:5432/food_erp"
```

---

### 2. Backend Deployment (FastAPI + Gunicorn / Uvicorn)

1. **Install Python 3.11+ dependencies**:
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Set strong `SECRET_KEY`, corporate GSTIN details, and production `DATABASE_URL`.

3. **Run Production Server**:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

### 3. Frontend Deployment (React + Vite + Tailwind)

1. **Install Dependencies & Build**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
   The production-ready assets will be generated in `frontend/dist/`.

2. **Hosting with Nginx**:
   Example Nginx configuration block:
   ```nginx
   server {
       listen 80;
       server_name erp.aachifoods.com;

       root /var/www/food_erp/frontend/dist;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://127.0.0.1:8000/api/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

---

### 4. Health Check & Production Verification

Once running, verify:
- Backend Health: `GET http://your-domain.com/health` → `{"status": "ok"}`
- Interactive Swagger API: `GET http://your-domain.com/api/v1/docs`
- 1-Click Benchmark Execution: `POST http://your-domain.com/api/v1/benchmark/run`

