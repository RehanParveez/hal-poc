# Hal — POC

This is the proof of concept for Hal, a platform designed to remove the predatory Arhti/middleman from Pakistan's agricultural supply chain. Also this solution name is just not finalized, today named it what seemed better

The core idea is to replace him with a digital system solution that connects smallholder farmers, microfinance banks, input shopkeepers, factory buyers, and landowners into one secure loop where money moves transparently and instantly.

This POC exists to prove one specific thing: the core transactional logic works. A bank official or technical partner can watch a live demo where the backend blocks an illegal payment, executes a multi-party financial settlement atomically, and prevents double-spending.

---

## What's in here
The project is split into two main folders:

* **`backend/`** — Django + DRF. This is the financial engine. All the escrow logic, the AFO (Agriculture Field Officer) validation gate, the proportional settlement waterfall, and the Batai/Theka (rent) crop-sharing splits live here.
* **`frontend/`** — Vue 3 + Tailwind. A working UI that lets you switch between the different user roles (bank manager, farmer, factory, shopkeeper, landowner, tenant farmer, insurance agent) to walk through the demo visually.

**Note:** There is no Celery, Redis broker, or complex microservice routing here. Those belong in the production architecture. This POC runs on a single Postgres instance and executes everything synchronously so you can clearly see the data flowing step by step.

---

## What this demo proves
Three things specifically:

**1. The AFO gate is real.** 
A farmer cannot spend money handled by the escrow logic on the wrong input category for their current crop lifecycle phase. They also cannot exceed the spending cap per acre defined by the AFO. Both of these violations are blocked at the database level, not just the API level.

**2. The Payment split settlement is atomic.** 
When a factory confirms a crop delivery grade, the bank recovers its proportional loan principal, deducts its commission, the platform takes its fee, and the farmer receives the net profit. This happens inside a single database transaction (`transaction.atomic`). If any single calculation fails, the entire thing rolls back. Partial payouts are impossible.

**3. Double-spend is prevented.** 
If someone tries to settle the exact same batch twice, the second request is rejected instantly. The invoice already exists, the database row lock fires, and the system returns a clean error. No funds are ever debited twice.

---

## Running it locally
You only need Docker and Docker Compose installed.

```bash
git clone [https://github.com/yourusername/hal.git](https://github.com/yourusername/hal.git)
cd hal
cp backend/.env.example backend/.env
docker compose up --build

Once the containers are running, setup the database:
Bashdocker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo_data

Backend runs at http://localhost:8000
Frontend runs at http://localhost:3000

## Demo accounts:
The seed command creates these default accounts. The password for all of them is demo1234.
Role                             Phone
Bank Manager (NRSP)              03001111004
Smallholder Farmer               03001111001
Tenant Farmer                    03001111002
Landowner                        03001111003
Factory Buyer                    03001111005
Shopkeeper                       03001111006
AFO Officer                      03001111007
Insurance Agent                  03001111008
RolePhoneBank Manager (NRSP)     03001111004
Smallholder Farmer               03001111001
Tenant Farmer                    03001111002
Landowner                        03001111003
Factory Buyer                    03001111005
Shopkeeper                       03001111006
AFO Officer                      03001111007
Insurance Agent                  03001111008


##The demo flow:
This is the standard walkthrough to show the platform to a bank or partner. It takes roughly 8-10 minutes end to end.

Step 1:-
Bank approves and disburses a loan:
Login as the bank manager. Go to the Loan Queue. You will see a submitted loan from dexter for PKR 50,000 against 10 acres of wheat in Bahawalpur. The acreage panel shows the landowner registered 12 acres and only 10 were requested, so the ceiling check passes. Approve it, set the interest, and disburse.Terminal shows: Insurance premium auto-deducted, escrow created with the remaining balance, Phase 1 (Seed Purchase) activated.

Step 2:-
Farmer tries to break the system (and fails):
Login as the farmer. Go to Buy Inputs. Select Fertilizer as the category.The system blocks it: "Phase 1 only allows seed. Fertilizer not available yet."Select Seed and enter PKR 25,000. Blocked again: "AFO cap for seed on 10 acres is PKR 12,000."Enter PKR 10,000. The transaction goes through, and the shopkeeper's wallet is credited instantly.

Step 3:-
Advance to the next phase:
For demo purposes, the bank manager has a button to manually unlock the next escrow phase (in production, this is a scheduled background task). Advance to Phase 2. The farmer can now buy fertilizer, but still cannot buy pesticide.

Step 4:-
Factory posts a contract & farmer delivers:
Login as the factory and post a wheat contract (e.g., 1000 kg required, PKR 150/kg). Switch to the farmer and log a batch delivery of 200 kg. Switch back to the factory to confirm the grade. (Example: Grade B, 8.33% deduction applied).

Step 5:-
The Payment Split Execution:
The settlement runs the exact moment the grade is confirmed. The terminal prints:

============================================================
HAL WATERFALL SETTLEMENT
Farmer:              Dexter
Batch:               200 kg Wheat
Grade:               Grade B (8.33% deduction)
────────────────────────────────────────
Gross Payout:        PKR       27,500
Loan Principal:      PKR       10,000
Interest:            PKR          164
Bank Commission:     PKR          165
Platform Fee:        PKR          137
────────────────────────────────────────
FARMER NET PROFIT:   PKR       17,034
============================================================

Step 6:-
Double-spend proof:
Try to confirm the grade on that exact same batch again.Response: "This batch has already been settled. Double-spend prevented."You can show the database directly: SELECT * FROM factoring_factoringinvoice; — there is only one row.

Step 7:-
Batai demo (optional):
To show the crop-sharing split, run the same flow but login as the Tenant Farmer. At settlement, the landowner's wallet receives their exact percentage at the exact same second the farmer receives theirs.

## What's NOT in this POC?
No SMS notifications (prints to console instead)
No external API calls (Arazi Center, NADRA, and Insurance APIs are mocked)
No scheduled tasks (phase unlocks are manual)
No Redis caching or Celery workers
No Nginx proxy

All of that will be part of the production architecture. This POC is just the core engine on a stand.

## Tech stack:
Backend: Python, Django, Django REST Framework, PostgreSQL, SimpleJWT
Frontend: Vue 3, Pinia, Vue Router, Axios, Tailwind CSS, Vite
Infrastructure: Docker, Docker Compose

Project structure
hal/
├── backend/
│   ├── apps/
│   │   ├── accounts/     user roles, JWT auth
│   │   ├── land/         parcels, tenant agreements (Theka/Batai)
│   │   ├── afo/          crop types, input caps, lifecycle milestones
│   │   ├── loans/        loan applications, disbursement
│   │   ├── escrow/       escrow wallets, phase unlocking
│   │   ├── insurance/    policies, premium deduction
│   │   ├── inputs/       AFO-gated shopkeeper payments
│   │   ├── contracts/    factory crop contracts
│   │   ├── delivery/     batch delivery, grade confirmation
│   │   ├── factoring/    waterfall settlement engine
│   │   └── wallets/      ledger, transaction history
│   └── shared.py         RBAC permissions, exception classes
└── frontend/
    ├── src/
    │   ├── api/          one file per backend domain
    │   ├── stores/       Pinia state per domain
    │   ├── views/        one folder per user role
    │   └── components/   shared + role-specific components
    └── ...