# Student Academic Performance Analytics Dashboard

A full-stack web application for analysing student academic performance.

- **Backend:** Python 3.14 · FastAPI · SQLAlchemy · SQLite · JWT Auth
- **Frontend:** React 19 · TypeScript · Vite · Tailwind CSS · Recharts
- **Roles:** Admin (full access) · Student (personal dashboard)

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

---

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python seed.py        # seed 3 students, 3 subjects, sample grades
uvicorn main:app --reload --port 8000
```

Backend runs at **http://localhost:8000**  
API docs: **http://localhost:8000/docs**

### 2. Frontend

Open a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Student | `alice` | `alice123` |
| Student | `bob` | `bob123` |
| Student | `carol` | `carol123` |

---

## Features

### Admin Dashboard (`/admin`)
- KPI cards: Total Students · Total Subjects · Overall Pass Rate
- Bar chart: Average marks per subject
- Pie chart: Pass vs Fail distribution
- Subject performance table
- All students table

### Student Dashboard (`/student`)
- Personal KPI cards: Subjects Enrolled · Overall Average · Best Subject
- Bar chart: Marks obtained vs max marks per subject
- Full grades table with Pass/Fail badge per entry

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | — | Login, returns JWT |
| GET | `/auth/me` | Any | Current user profile |
| GET | `/students` | Admin | List all students |
| POST | `/students` | Admin | Create student + user |
| GET | `/students/{id}` | Admin/Owner | Get one student |
| GET | `/subjects` | Any | List subjects |
| POST | `/subjects` | Admin | Create subject |
| POST | `/grades` | Admin | Record a grade |
| GET | `/grades/student/{id}` | Admin/Owner | Student grades |
| GET | `/dashboard/admin` | Admin | Aggregated analytics |
| GET | `/dashboard/student/{id}` | Admin/Owner | Personal analytics |
| GET | `/health` | — | Health check |

---

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy engine + session
│   ├── seed.py              # Sample data seeder
│   ├── requirements.txt
│   ├── models/              # ORM models (User, Student, Subject, Grade)
│   ├── routers/             # Route handlers (auth, students, subjects, grades, dashboard)
│   ├── schemas/             # Pydantic request/response models
│   └── core/                # JWT security + auth dependencies
│
└── frontend/
    ├── src/
    │   ├── api/client.ts    # Axios instance with JWT interceptor
    │   ├── context/         # AuthContext (user, token, login, logout)
    │   ├── components/      # Navbar, ProtectedRoute
    │   └── pages/           # Login, AdminDashboard, StudentDashboard
    └── tailwind.config.js
```

---

## Pass/Fail Threshold

A grade is considered **Pass** when `marks_obtained >= 40% of subject.max_marks`.  
This is computed at query time — no stored field required.
