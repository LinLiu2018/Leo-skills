# System Design Framework

> **Usage**: Load this framework for Architect Agent tasks (Database, API, System design).

## 1. Database Design (ER Modeling)
### 1.1 Core Entities
- Identify nouns in requirements.
- Define attributes (columns).
- Identify Primary Keys (PK).

### 1.2 Relationships
- **1:1**: One user has one profile.
- **1:N**: One user has many orders.
- **M:N**: Students take many courses (link table required).

### 1.3 Normalization
- **1NF**: Atomic values.
- **2NF**: No partial dependencies.
- **3NF**: No transitive dependencies.

## 2. API Design (RESTful)
### 2.1 Resource Naming
- Use plural nouns (e.g., `/users`, `/orders`).
- Stick to standard HTTP methods (GET, POST, PUT, DELETE).

### 2.2 Response Format (Standard JSON)
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

## 3. Technology Selection
### 3.1 Evaluation Criteria
- **Scalability**: Can it handle 10x growth?
- **Maintainability**: Is the ecosystem mature?
- **Performance**: Latency requirements?
- **Cost**: Licensing and hosting.

### 3.2 Common Stacks
- **Backend**: Python (FastAPI/Django), Node.js (NestJS), Go.
- **Frontend**: React, Vue.
- **Database**: PostgreSQL (Relational), MongoDB (Document), Redis (Cache).
