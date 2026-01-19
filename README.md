# 🛡️ SAKSHAM

### Secure Authorization & Knowledge-based Shared Human Access Manager

**SAKSHAM** is a transparent, auditable consent management system designed to help individuals, organizations, and regulators operationalize consent requirements under **India’s DPDP Act** and **GDPR**.

The project treats consent not as a static checkbox, but as a **verifiable, purpose-bound, and revocable event**—with cryptographic receipts and audit-ready visibility.

---

## 🚀 Getting Started

### Frontend (User Interface)

This directory contains the React/Vite Frontend.

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Run Development Server**:
   ```bash
   npm run dev
   ```
   Access the UI at `http://localhost:5173`.


### Backend (API & Ledger)

For backend setup, API documentation, and database schema, please refer to the [Backend README](./backend/README.md).

---

## 🚩 Problem Statement

In today’s digital ecosystem:

* Users lack clear visibility and control over how their personal data is used.
* Consent is often broad, opaque, and difficult to revoke.
* Organizations struggle to demonstrate compliance during audits.
* Regulators depend heavily on self-reported policies rather than verifiable evidence.

While DPDP and GDPR define strong legal rights, **practical technical systems to enforce and prove consent remain limited**.

---

## 💡 Solution Overview

**SAKSHAM** provides a federated, API-first consent infrastructure that enables:

* Purpose-specific consent granting
* One-click, traceable consent revocation
* Cryptographically verifiable consent receipts
* Append-only audit logs for compliance verification
* Interoperability across multiple applications

The system does **not** centralize personal data. Instead, it manages **consent metadata and proofs**, making adoption realistic and scalable.

---

## ✨ Key Features

### For Users (Data Principals)

* Unified consent dashboard across applications
* Purpose-wise consent control
* Partial and full consent revocation
* Downloadable consent receipts (PDF / QR)
* Clear, plain-language explanations

### For Applications (Data Fiduciaries)

* Consent request & validation APIs
* Purpose registry enforcement
* Revocation webhooks with acknowledgement tracking
* Compliance overview and consent health indicators

### For Regulators & Auditors

* Read-only audit dashboard
* Independent receipt verification
* Time-bound audit logs
* Revocation SLA visibility

---

## 🧠 Unique Innovations

* **Consent Receipts**: Signed, verifiable proof of consent actions
* **Purpose Registry**: Standardized purpose codes aligned with law
* **Event-Driven Revocation**: Traceable, acknowledged consent withdrawal
* **Audit-by-Design**: Compliance visibility without trusting the application
* **Federated Architecture**: No central storage of personal data

---

## 🏗️ System Architecture (High Level)

SAKSHAM follows a layered architecture:

* **Interface Layer**: User, App Admin, and Regulator dashboards
* **Consent Orchestration Layer**: Consent manager, purpose registry, revocation logic
* **Trust & Audit Layer**: Receipt engine, immutable audit logs
* **Integration Layer**: APIs, SDKs, and webhook dispatcher
* **Storage Layer**: Metadata store and append-only log store

Consent actions flow as **auditable events**, not static records.

---

## 🛠️ Tech Stack

**Backend**

* Python (API-first design)
* RESTful services

**Authentication & Database**

* Supabase (Auth + PostgreSQL)

**Frontend**

* Web-based dashboards (role-based access)

**Security**

* Signed JSON receipts
* Hash-chained audit logs
* Role-based access control (RBAC)

---

## 🧪 Prototype Scope

The prototype demonstrates:

* End-to-end consent grant → receipt → revoke → audit flow
* Multi-application interoperability
* Regulator audit simulation

Out of scope (explicitly):

* Physical data deletion inside third-party systems
* Legal enforcement beyond proof and traceability

---

## 📊 Evaluation Metrics & KPIs

* Consent processing latency
* Revocation acknowledgement time
* Receipt verification success rate
* Audit completeness
* User clarity and usability indicators

---

## ⚠️ Limitations

* Enforcement relies on organizational compliance, not coercion
* Prototype uses simulated external applications
* Legal adjudication mechanisms are out of scope

---

## 🚀 Future Scope

* Integration with government consent frameworks
* Advanced compliance analytics
* Mobile-first consent wallets
* Cross-border consent portability
* Standardization with emerging privacy protocols

---

## 🌍 Impact

* **Citizens** gain real control and proof over consent decisions
* **Organizations** reduce compliance risk with audit-ready systems
* **Regulators** gain visibility into actual consent practices

---

## 🏁 Conclusion

SAKSHAM demonstrates how consent can be **granted with clarity, revoked with accountability, and audited with confidence**. By aligning legal intent with practical system design, it provides a realistic and scalable foundation for privacy governance in the digital age.

---

## 👥 Team

* **Prasanna Pal**
* **Tanmay Rajurkar**
* **Chinmay Bhat**
* **Anshul Hajare**
