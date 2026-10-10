# Student Academic Performance Analytics Dashboard — MVP Plan

## Top-Level Overview

Build a full-stack web application that lets **Admins** manage students, subjects, and grades, while **Students** view their own academic performance through an analytics dashboard.

- **Backend:** Python + FastAPI, SQLite (via SQLAlchemy), JWT authentication
- **Frontend:** React + TypeScript + Vite, Recharts for visualisations, Tailwind CSS
- **Runs locally:** Backend on `http://localhost:8000`, Frontend on `http://localhost:5173`
- **No AI/ML features**
- **Scope:** Students, Subjects, Grades modules only (no Attendance)

---

## Architecture Overview

```
Frontend (React + TS + Vite)          Backend (FastAPI + SQLAlchemy)
  :5173                                  :8000
  ┌─────────────────────────┐            ┌──────────────────────────────┐
  │  Login Page             │◄──JWT──────│  POST /auth/login             │
  │  Admin Dashboard        │◄──REST─────│  GET  /students               │
  │  Student Dashboard      │            │  POST /students               │
  │  Grades Table + Charts  │            │  GET  /subjects               │
  └─────────────────────────┘            │  POST /grades                 │
                                         │  GET  /grades/student/{id}    │
                                         │  GET  /dashboard/admin        │
                                         │  GET  /dashboard/student/{id} │
                                         └──────────────┬───────────────┘
                                                        │
                                                   SQLite DB
                                                   (app.db)
```

---

## Roles

| Role    | Capabilities |
|---------|-------------|
| Admin   | Create/view students, subjects, grades; view full analytics dashboard |
| Student | View own grades and personal performance dashboard only |

---

## Database Schema

**users** — id, username, hashed_password, role (admin/student)
**students** — id, user_id (FK→users), name, roll_number, department, year
**subjects** — id, name, code, department, max_marks
**grades** — id, student_id (FK→students), subject_id (FK→subjects), exam_type (internal/midterm/final), marks_obtained, semester

---

## Sub-Tasks

---

### Sub-Task 1 — Backend Project Scaffold

**Intent:** Set up the FastAPI project folder structure, virtual environment, and dependencies so every subsequent backend sub-task has a working base to build on.

**Expected Outcomes:**
- `backend/` folder exists with a working `main.py` that starts FastAPI
- `requirements.txt` lists all dependencies
- Running `uvicorn main:app --reload` at `localhost:8000` returns `{"status":"ok"}`
- CORS configured to allow requests from `localhost:5173`

**Todo List:**
1. Create `backend/` directory
2. Create `backend/requirements.txt` with: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`, `pydantic`
3. Create `backend/main.py` — instantiate `FastAPI()`, add CORS middleware, mount routers, add a `GET /health` route
4. Create `backend/database.py` — SQLAlchemy engine pointing to `./app.db`, `SessionLocal`, `Base`, `get_db` dependency
5. Create folder structure: `backend/models/`, `backend/routers/`, `backend/schemas/`, `backend/core/`

**Relevant Context:** None — greenfield project.

**Status:** [x] done

---

### Sub-Task 2 — Database Models

**Intent:** Define all SQLAlchemy ORM models and create the SQLite tables so the rest of the app has a concrete data layer to read/write.

**Expected Outcomes:**
- `User`, `Student`, `Subject`, `Grade` models defined in `backend/models/`
- `Base.metadata.create_all(engine)` called at startup creates all tables in `app.db`
- Relationships defined: `Student.user` (one-to-one), `Grade.student`, `Grade.subject`

**Todo List:**
1. Create `backend/models/user.py` — `User` model: id, username, hashed_password, role
2. Create `backend/models/student.py` — `Student` model: id, user_id, name, roll_number, department, year
3. Create `backend/models/subject.py` — `Subject` model: id, name, code, department, max_marks
4. Create `backend/models/grade.py` — `Grade` model: id, student_id, subject_id, exam_type, marks_obtained, semester
5. Create `backend/models/__init__.py` exporting all models
6. Call `Base.metadata.create_all(bind=engine)` in `main.py` startup

**Relevant Context:** Sub-Task 1 must be complete. `Base` comes from `database.py`.

**Status:** [x] done

---

### Sub-Task 3 — Authentication (JWT)

**Intent:** Implement login endpoint and JWT token generation/validation so routes can be protected by role.

**Expected Outcomes:**
- `POST /auth/login` accepts `username` + `password`, returns `access_token` + `token_type`
- `GET /auth/me` returns the current user's profile
- A reusable `get_current_user` dependency extracts and validates JWT from the `Authorization: Bearer` header
- A `require_admin` dependency raises 403 if the current user is not an admin
- A seed script creates one default admin user (`admin` / `admin123`) on first run

**Todo List:**
1. Create `backend/core/security.py` — `create_access_token()`, `verify_password()`, `get_password_hash()`, `decode_token()`
2. Create `backend/core/deps.py` — `get_current_user(token, db)` dependency; `require_admin` dependency
3. Create `backend/routers/auth.py` — `POST /auth/login`, `GET /auth/me`
4. Create `backend/schemas/auth.py` — `LoginRequest`, `TokenResponse`, `UserOut` Pydantic models
5. Add a `seed_admin()` function called at startup in `main.py` that creates the admin user if none exists
6. Mount `auth` router in `main.py`

**Relevant Context:** Uses `User` model from Sub-Task 2. Secret key stored as a constant in `core/security.py` for local dev.

**Status:** [x] done

---

### Sub-Task 4 — Students & Subjects API

**Intent:** Provide CRUD endpoints for Students and Subjects so the Admin can populate data, and students can be linked to user accounts.

**Expected Outcomes:**
- `GET /students` — admin gets all students
- `POST /students` — admin creates a student (also creates a linked user account)
- `GET /students/{id}` — admin or owner student can fetch one student
- `GET /subjects` — any authenticated user can list subjects
- `POST /subjects` — admin can create a subject
- All routes are JWT-protected

**Todo List:**
1. Create `backend/schemas/student.py` — `StudentCreate`, `StudentOut` Pydantic models
2. Create `backend/schemas/subject.py` — `SubjectCreate`, `SubjectOut` Pydantic models
3. Create `backend/routers/students.py` — implement the 3 student routes with auth dependencies
4. Create `backend/routers/subjects.py` — implement the 2 subject routes with auth dependencies
5. Mount both routers in `main.py`

**Relevant Context:** `StudentCreate` should include the plain-text password so the router can hash it and create the linked `User` record in the same transaction.

**Status:** [x] done

---

### Sub-Task 5 — Grades API

**Intent:** Allow admins to record grades per student/subject/exam and expose grade data to the dashboard endpoints.

**Expected Outcomes:**
- `POST /grades` — admin records a grade entry
- `GET /grades/student/{student_id}` — returns all grades for a student (admin or the student themselves)
- `GET /dashboard/admin` — returns aggregated stats: total students, subject averages, pass/fail counts per subject
- `GET /dashboard/student/{student_id}` — returns that student's grades grouped by subject and semester

**Todo List:**
1. Create `backend/schemas/grade.py` — `GradeCreate`, `GradeOut` Pydantic models
2. Create `backend/routers/grades.py` — `POST /grades` (admin only), `GET /grades/student/{student_id}`
3. Create `backend/routers/dashboard.py` — `GET /dashboard/admin`, `GET /dashboard/student/{student_id}`
4. Admin dashboard query: use SQLAlchemy to compute average marks, count of pass (marks ≥ 40% of max_marks) and fail per subject
5. Mount both routers in `main.py`

**Relevant Context:** Pass threshold is marks_obtained ≥ 40% of subject.max_marks — purely a query-time calculation, no stored field needed.

**Status:** [x] done

---

### Sub-Task 6 — Frontend Scaffold

**Intent:** Set up the React + TypeScript + Vite project with routing, Tailwind CSS, and an Axios API client so all subsequent frontend sub-tasks have a base to build on.

**Expected Outcomes:**
- `frontend/` folder bootstrapped with Vite (React + TypeScript template)
- Tailwind CSS configured
- `axios` installed; `frontend/src/api/client.ts` exports an Axios instance pointed at `http://localhost:8000`
- `react-router-dom` installed; `App.tsx` has routes for `/login`, `/admin`, `/student`
- A protected route wrapper redirects unauthenticated users to `/login`
- JWT token stored in `localStorage`; attached automatically to every request via Axios request interceptor

**Todo List:**
1. Scaffold `frontend/` using `npm create vite@latest frontend -- --template react-ts`
2. Install dependencies: `tailwindcss`, `postcss`, `autoprefixer`, `axios`, `react-router-dom`, `recharts`
3. Initialise Tailwind: `npx tailwindcss init -p`; configure `content` paths in `tailwind.config.js`
4. Create `frontend/src/api/client.ts` — Axios instance with `baseURL`, request interceptor injecting Bearer token from localStorage
5. Create `frontend/src/context/AuthContext.tsx` — provides `user`, `token`, `login()`, `logout()` via React Context
6. Create `frontend/src/components/ProtectedRoute.tsx` — redirects to `/login` if no token
7. Wire up routes in `frontend/src/App.tsx`

**Relevant Context:** Sub-Task 3 (auth endpoints) must be complete before the login form can be tested end-to-end.

**Status:** [x] done

---

### Sub-Task 7 — Login Page

**Intent:** Build the Login page so users can authenticate and receive a JWT, enabling access to the rest of the app.

**Expected Outcomes:**
- `/login` page renders a username + password form with a submit button
- On success, stores token in localStorage and redirects Admin → `/admin`, Student → `/student`
- Displays an error message on invalid credentials
- Styled with Tailwind CSS

**Todo List:**
1. Create `frontend/src/pages/Login.tsx` — controlled form component
2. On submit, call `POST /auth/login` via the Axios client
3. On success, call `AuthContext.login()` with the token and user info; redirect by role
4. On failure (401), display "Invalid credentials" inline error

**Relevant Context:** Role is returned in `GET /auth/me` or can be embedded in the JWT payload and decoded client-side.

**Status:** [x] done

---

### Sub-Task 8 — Admin Dashboard Page

**Intent:** Give the Admin a data-rich page showing overall academic performance KPIs and per-subject analytics.

**Expected Outcomes:**
- `/admin` page (protected, admin-only) displays:
  - KPI cards: Total Students, Total Subjects, Overall Pass Rate
  - Bar chart: Average marks per subject
  - Pie/Donut chart: Pass vs Fail distribution across all subjects
  - Table: All students with their name, roll number, department, year
- Data fetched from `GET /dashboard/admin` and `GET /students`

**Todo List:**
1. Create `frontend/src/pages/AdminDashboard.tsx`
2. Fetch `GET /dashboard/admin` on mount; store in local state
3. Render 3 KPI stat cards (Total Students, Total Subjects, Overall Pass %)
4. Render a `BarChart` (Recharts) for average marks per subject
5. Render a `PieChart` (Recharts) for pass vs fail counts
6. Render a students table with columns: Name, Roll No., Department, Year
7. Add a Navbar with a Logout button (clears auth context + redirects to `/login`)

**Relevant Context:** Uses `GET /dashboard/admin` (Sub-Task 5) and `GET /students` (Sub-Task 4).

**Status:** [x] done

---

### Sub-Task 9 — Student Dashboard Page

**Intent:** Give each Student their own personal performance view so they can track grades across subjects and semesters.

**Expected Outcomes:**
- `/student` page (protected, student-only) displays:
  - KPI cards: Subjects Enrolled, Overall Average %, Highest Scoring Subject
  - Bar chart: Marks obtained vs max marks per subject
  - Grades table: Subject, Exam Type, Marks, Semester, Pass/Fail status
- Data fetched from `GET /dashboard/student/{student_id}`

**Todo List:**
1. Create `frontend/src/pages/StudentDashboard.tsx`
2. Derive `student_id` from the authenticated user context (embed in JWT or fetch from `/auth/me`)
3. Fetch `GET /dashboard/student/{student_id}` on mount
4. Render KPI cards
5. Render a `BarChart` (Recharts) comparing marks_obtained vs max_marks per subject
6. Render a grades breakdown table with a Pass/Fail badge column
7. Add Navbar with Logout

**Relevant Context:** Uses `GET /dashboard/student/{id}` (Sub-Task 5). Student's `student_id` must be returned in the login/me response.

**Status:** [x] done

---

### Sub-Task 10 — Local Run & Wiring Verification

**Intent:** Confirm the full stack runs end-to-end on localhost with no errors and all features work together.

**Expected Outcomes:**
- Backend starts: `cd backend && uvicorn main:app --reload` → `localhost:8000`
- Frontend starts: `cd frontend && npm run dev` → `localhost:5173`
- Admin can log in, see the dashboard with charts, and the grades table
- Student can log in, see their own dashboard with charts and grades
- FastAPI auto-docs (`localhost:8000/docs`) list all routes correctly
- A `README.md` at the project root documents the setup and run instructions

**Todo List:**
1. Verify backend health: `GET /health` returns `{"status":"ok"}`
2. Verify CORS: frontend requests reach backend without CORS errors
3. Seed at least 3 students, 3 subjects, and sample grades via the API (or a seed script)
4. Smoke-test Admin login → dashboard renders charts
5. Smoke-test Student login → personal dashboard renders correctly
6. Write `README.md` with: prerequisites, install steps, seed instructions, run commands

**Relevant Context:** This sub-task validates all previous sub-tasks. No new code — integration + docs only.

**Status:** [x] done

---

## Implementation Order

```
Sub-Task 1 → Sub-Task 2 → Sub-Task 3 → Sub-Task 4 → Sub-Task 5
                                                            ↓
Sub-Task 6 → Sub-Task 7 → Sub-Task 8 → Sub-Task 9 → Sub-Task 10
```

Backend sub-tasks (1–5) should be completed before frontend sub-tasks (6–9) so API contracts are stable.
