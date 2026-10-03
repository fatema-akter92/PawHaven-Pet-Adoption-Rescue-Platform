# PawHaven — Pet Adoption & Rescue Platform

- A production-ready, full-stack Pet Adoption & Rescue Platform featuring a serene aesthetic, full compliance with the assignment specification, and high-performance **Django REST Framework (DRF)** APIs.

---


---

## 📋 Features Implemented (From Specification)

### 1. User Features & Authentication
- **User Registration:** Custom registration with username, email, full name, and password confirmation.
- **Login / Logout:** Secure session authentication with customized login forms and redirects.
- **User Profile (`/profile/`):** View personal information, total application count, approved/rejected breakdown, and saved favorites.
- **REST API Token Manager:** View, copy, and regenerate personal DRF Auth Tokens directly in the profile UI.

### 2. Pet Browsing, Search & Filtering 
- **Metadata Display:** Pet name, species, breed, age, gender, location, description, health badges, and adoption status.
- **Multi-parameter Search & Filtering:**
  - Keyword search (name, breed, location, description)
  - Animal type (Dog, Cat, Bird, Rabbit, Other)
  - Gender (Male, Female)
  - Breed filter
  - Location filter (e.g. Dhaka, Chittagong, Sylhet)
  - Status filter (Available, Adopted)


### 3. Pet Details 
- High-resolution pet photo presentation with fallbacks.
- Complete characteristics, health badges (Vaccinated, Spayed/Neutered, Microchipped, Good with kids/pets).
- **Adoption Action Area:**
  - If **Available**: Prominent "Apply for Adoption" button.
  - If **Adopted**: Displays prominent notice: `❌ This pet has already been adopted.` and disables/hides the adoption button.
  - Similar companions recommendation carousel at the bottom.

### 4. Adoption Request Application 
- Logged-in adopters submit:
  - Residential Address
  - Phone Number
  - Reason for Adoption ("Why do you want this pet?")
  - Previous Pet Experience (Yes / No radio selection)
  - Additional Message (Optional)

### 5. User Dashboard — "My Adoption Requests" (`/my-adoptions/`)
- Dashboard overview showing summary metrics: Total Applications, Pending, Approved, Rejected.
- Applications table with Pet details, Application Date (e.g. `20 Sep 2026`), Status badges, and Review notes.
- **Visual Adoption Stepper:** Multi-stage progress tracking (Submitted → Under Review → Approved / Rejected).
- Pending request cancellation option.

### 6.  Django Admin Management (`/admin/`)
- **Pet Management:** Add, edit, delete pets, preview photo thumbnails, update status, and filter by species/gender/location.
- **Adoption Request Management:** Review applicant info, contact number, reason, and change statuses.
- **Custom Admin Actions:**
  - `✅ Approve selected requests (Mark Pet as Adopted)`
  - `❌ Reject selected requests`


### 7.  Unique Features (Beyond the Spec)
1. **PawMatch Compatibility Quiz (`/pawmatch-quiz/`):**
   Interactive lifestyle questionnaire matching prospective adopters with the best available pets based on home space, energy level, family members, and pet experience with match percentage scores.
2. **Interactive REST API Documentation Portal (`/api-docs/`):**
   In-app API documentation with curl commands, JSON request/response formats, and a 1-click personal token copy button.
3. **Medical & Care Badges:**
   Visual indicators on pet cards for vaccination, neutering, microchipping, and child-friendliness.
4. **Automated Demo Data Seeder (`python manage.py seed_data`):**
   Instantly populates 10 realistic pets with custom generated artwork, pre-configured users (`admin`, `rahim`, `fatima`), sample applications, and DRF tokens.

---

## 🌐 REST API Endpoints Overview

| Method | Endpoint | Permissions | Description |
|---|---|---|---|
| `GET` | `/api/pets/` | Public | Paginated list of pets (Supports `?search=...`, `?animal_type=...`, `?page=...`) |
| `GET` | `/api/pets/<id>/` | Public | Retrieve individual pet details |
| `POST` | `/api/pets/` | Staff/Admin | Create a new pet profile |
| `PUT` | `/api/pets/<id>/` | Staff/Admin | Update pet profile |
| `DELETE` | `/api/pets/<id>/` | Staff/Admin | Delete pet profile |
| `GET` | `/api/adoptions/` | Authenticated | Adopter views their own requests; Staff views all |
| `POST` | `/api/adoptions/` | Authenticated | Submit adoption request (Enforces Rules 1 & 2) |
| `GET` | `/api/adoptions/<id>/` | Authenticated | View adoption request detail |
| `PUT` | `/api/adoptions/<id>/` | Staff/Admin | Approve/Reject request (Triggers Rule 3) |
| `GET` | `/api/favorites/` | Authenticated | List user's favorite pets |
| `POST` | `/api/favorites/toggle/<id>/` | Authenticated | Toggle favorite status for pet |
| `POST` | `/api/auth/token/` | Public | Obtain DRF Auth Token via username/password |
| `POST` | `/api/auth/register/` | Public | Register new user via REST API |
| `POST` | `/api/auth/login/` | Public | Login and receive user profile & token |
| `GET` | `/api/auth/me/` | Authenticated | Get current authenticated user profile & stats |

---

Visit **http://127.0.0.1:8000/** in your browser!

---
