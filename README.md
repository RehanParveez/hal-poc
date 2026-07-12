# HAL — MVP

Status: not built yet. This document describes exactly what this MVP repo is meant to contain, based on the architecture design behind it. Nothing below is working code right now.

This repo used to hold a smaller proof of concept. That proof of concept already showed the core money logic works: escrow, spending rules, atomic payment splits, no double payments. This repo is the next step: turning that proof of concept into a real MVP that a bank could actually trust and pilot.

Some of the old POC's logic carries over here, since it's already correct and already relevant. The two genuinely new pieces are described below.

# What HAL is?

HAL removes the middleman (the Arthi) from Pakistan's farm lending. Right now, most small farmers borrow from a local middleman. He lends cash, but he also controls what the farmer buys and what the farmer gets paid at harvest. This keeps the farmer stuck in debt.

HAL replaces this with one digital system. It connects the farmer, the bank, the input shop, the factory buyer, and the landowner. Money moves between them automatically, in the open. No one can quietly take more than their share.

# What "MVP done" actually means?

The MVP is done when the platform can do this, for one real pilot: one district, a small group of farmers, one shopkeeper, one factory buyer, one partner bank.


Sign up a farmer, and check them with a real Numberdar before they can borrow.
Run a real credit bureau check, with a real, recorded consent step, before any money is paid out.
Lock the bank's money in escrow, and release it in stages.
Let the farmer buy inputs from an approved shopkeeper, checked against their crop stage and spending cap.
Take out an insurance fee automatically, and allow a human to review a claim if one comes in.
Let a factory post a contract, assign farmers to it, and confirm the delivery and its quality grade.
Split the harvest payment automatically: the bank gets its loan back first, then its cut, then the platform's small fee, then the farmer gets the rest. The farmer never sees a fee line, it's built into the price quietly instead.
Tell every person involved what just happened, at every step, in both Urdu and English.


That loop, steps 1 through 8, is the whole business case. Everything else is about scaling this loop to more farmers and more districts later, not proving it works in the first place.

# What's included in this MVP, and what's saved for later

Fourteen backend apps are in scope for this MVP. Twelve of them either already exist from the old POC or are simple extensions of it. Two are genuinely new.

Carried over from the POC, mostly unchanged:
land, afo, escrow, insurance, inputs, contracts, delivery, factoring, wallets. These already work. They just need a few small hooks removed, since those hooks point at apps that don't exist yet (see below).

Extended from the POC:
accounts — corporate sign-up (shopkeepers, factories) waits for a person to manually check their documents, instead of an automatic outside check. loans — the pre-checks before a payout now also require a passed credit check and a passed Numberdar check. notifications — trimmed down to only the messages that actually matter for a small pilot.

Brand new, not built yet:


community — the Numberdar app. A Numberdar is a trusted local figure who already vouches for people in their village. A farmer needs a real Numberdar's approval before they can apply for a loan.
credit — the credit bureau app. Before any money goes out, the system runs a real credit check (through eCIB or Tasdeeq), with a clear consent step first (a one-time code sent by SMS, so there's proof the farmer agreed to the check).


Deliberately left out of this MVP, saved for later:


analytics — dashboards and reporting. Not needed to prove the loop works. Basic admin tools cover the pilot for now.
ewr (Electronic Warehouse Receipts) — turning stored crops into a bank-usable asset. This needs real warehouse partnerships a small pilot won't have yet.
groups (joint-liability lending) — a small, individually-checked pilot group doesn't need shared group risk yet. This matters more once there are many more farmers.
billing — automatic invoicing between the platform, shops, and factories. With one or two pilot partners, this can just be settled by hand for now.
warehouse_operator role — this only makes sense once the ewr app exists.


None of these five are missing by accident. Each one is left out on purpose, because the core loan-to-harvest loop works without them, and each one can be added back later without changing anything already built.

Backend structure (target)

backend/
├── apps/
│   ├── accounts/     user roles, login, manual shop/factory verification
│   ├── land/         land parcels, tenant agreements (Theka/Batai)
│   ├── community/    NEW — Numberdar sign-up and approval
│   ├── credit/       NEW — credit bureau check + consent
│   ├── afo/          crop types, spending caps, growth-stage rules
│   ├── loans/        loan applications, payout, gated on credit + Numberdar
│   ├── escrow/       escrow wallets, phase unlocking
│   ├── insurance/     policies, premium deduction, manual claim review
│   ├── inputs/       AFO-checked shopkeeper payments
│   ├── contracts/    factory crop contracts
│   ├── delivery/     batch deliveries, grade confirmation
│   ├── factoring/    the payment-split engine, fee hidden from farmer
│   ├── wallets/      account balances, transaction history
│   └── notifications/  SMS/push, trimmed to the events that matter for a pilot
└── shared/            permissions, error classes, shared helpers

Frontend structure (target)

frontend/
├── src/
│   ├── api/           one file per backend app, including new credit.js and community.js
│   ├── stores/        one Pinia store per app, same new additions
│   ├── views/
│   │   ├── farmer/    dashboard, escrow balance, input payments, a new credit consent screen
│   │   ├── bank/      loan queue with a credit-tier column, a new credit check panel
│   │   ├── numberdar/ NEW — a dashboard and approval queue for Numberdar users
│   │   └── ...         landowner, factory, shopkeeper, insurance, afo, mostly carried over
│   └── components/    shared pieces, plus new ones for OTP entry, document upload, and credit status


## Tech stack

Backend: Python, Django, Django REST Framework, PostgreSQL, SimpleJWT
Frontend: Vue 3, Pinia, Vue Router, Axios, Tailwind CSS, Vite
Infrastructure: Docker, Docker Compose


- One promise that's non-negotiable

The farmer never sees a platform fee, anywhere in the product. The platform's share is quietly built into the price the factory pays, not shown as a deduction to the farmer. This isn't a nice-to-have, it's a rule the frontend has to follow from the very first settlement screen.

# Dependency order

This MVP is structured so each piece depends on the one before it:


The Numberdar app (community) comes first, since a loan can't be gated on Numberdar approval until the app that tracks it exists.
The credit bureau app (credit) comes next, since disbursement depends on a passed credit check.
Manual shop/factory verification and the land app sit right after, since loans reference both.
The AFO app and the new loan pre-checks (credit + Numberdar) come next.
Escrow and insurance follow, carried over from the POC.
Inputs, contracts, and delivery follow, carried over, minus the billing hooks they don't need yet.
The payment-split engine and wallets come after that, carried over, minus the group and billing hooks.
Notifications come last on the backend side, trimmed to what a pilot actually needs.
A hardening pass closes it out: race conditions, edge cases, and the test suite.


The frontend follows this same order, one screen at a time, so no screen depends on a backend piece that isn't there yet.

# What moves to a later version, without a rebuild?

When the pilot works and it's time to grow past it, the ewr, groups, billing, and analytics apps slot back in exactly where they were removed from. Nothing built for this MVP needs to be torn up to make room for them. That's the point of leaving them out now instead of building a half-finished version of each.