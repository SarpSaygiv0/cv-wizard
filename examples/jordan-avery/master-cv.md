# Master CV — Jordan Avery

> Tailoring note: fictional example workspace. Every person, employer, school, and number here is made up.

## Contact
- **Name:** Jordan Avery
- **Headline:** Software Engineer | Python | Go | PostgreSQL
- **Location:** Denver, CO, USA
- **Phone:** +1 555 0142
- **Email:** jordan.avery@example.com
- **LinkedIn:** linkedin.com/in/javery-example
- **GitHub:** github.com/javery-example

## Summary
Software engineer with six years' experience building backend services for logistics and billing. Designs event-driven systems on Kafka and PostgreSQL, owns services from design through on-call, and prefers fast, boring, well-tested releases.

## Skills
- **Languages:** Python, Go, SQL, TypeScript
- **Backend:** Django, FastAPI, gRPC, REST APIs, event-driven architecture
- **Data:** PostgreSQL, Redis, Apache Kafka, dbt
- **Infrastructure:** AWS (ECS, Lambda, SQS), Terraform, Docker, GitHub Actions, Datadog
- **Practices:** Code review, testing (pytest, Go testing), incident response, technical writing, mentoring

## Experience

### Software Engineer — Globex Logistics
- **Dates:** Jun 2022 – Present
- **Location:** Denver, CO (remote)
- Built the shipment-tracking event pipeline in Go on Kafka, consolidating carrier updates from 40+ integrations into one stream consumed by 9 internal services.
- Cut p95 latency of the public tracking API from 900 ms to 180 ms by adding a Redis read-through cache and removing N+1 queries in the PostgreSQL access layer.
- Designed an idempotent webhook delivery service with retries and a dead-letter queue, raising successful partner deliveries from 97.1% to 99.8%.
- Led the migration of 14 services from hand-managed EC2 hosts to ECS with Terraform, removing a weekly manual deployment step.
- On the team's on-call rotation; wrote the runbooks and post-incident reviews that brought median time to recovery down from 70 to 25 minutes.
- Mentored two new engineers through their first six months with pairing and structured code review.

### Associate Software Engineer — Initech
- **Dates:** Jul 2020 – May 2022
- **Location:** Austin, TX
- Maintained the Django billing platform that invoiced about 12,000 business customers a month.
- Rebuilt proration logic for mid-cycle plan changes, eliminating a class of billing errors that had generated around 150 support tickets a month.
- Raised test coverage of the invoicing module from 41% to 85% and added contract tests against the payment provider's sandbox.
- Automated monthly revenue reports with dbt and SQL, replacing a two-day spreadsheet process.

### Software Engineering Intern — Acme Health
- **Dates:** Jun 2019 – Aug 2019
- **Location:** Boulder, CO
- Built an internal FastAPI service that flagged duplicate patient appointment requests.

## Projects

### Trailhead — Go, PostgreSQL/PostGIS, TypeScript
Open-source route planner for hikers that computes elevation-aware routes from public trail data; about 1,200 GitHub stars.
> Include when: the posting values open source, geospatial work, or frontend skills.

### pg-queue-bench — Python, PostgreSQL
Benchmark suite comparing PostgreSQL-backed job queues under contention; referenced in two library READMEs.
> Include when: the posting emphasizes databases or performance.

## Education

### Westfield University — B.S. Computer Science
- **Dates:** Aug 2016 – May 2020
- GPA 3.6

## Certifications
- AWS Certified Developer – Associate (2023)

## Languages
- English: Native
- Spanish: Conversational (B1)

## Profile & Working Style
> Tailoring note: optional traits to weave into a summary or cover letter when a posting calls for them.
- Prefers small, reversible changes, and writes things down: runbooks, design docs, incident reviews.
- Enjoys the unglamorous reliability work that keeps on-call quiet.
