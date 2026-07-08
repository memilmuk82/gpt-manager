# GPT Manager

## Project Overview

GPT Manager is a Flask-based school operations application for managing shared access to generative AI accounts in an educational setting.

The project was created in the context of the AI and Computer Science curriculum at Jongno Polytechnic High School in Korea. It addresses a concrete school workflow: when teachers or staff share limited generative AI resources, the school needs a clear way to reserve time slots, prevent conflicts, record usage, support responsible prompting, and provide basic administrative oversight.

This project is not presented as a widely adopted open-source project yet. Its current impact comes from solving real operational problems in schools and serving as a practical educational reference for students learning backend software development.

The repository is developed as open-source software so that educators, students, reviewers, and future contributors can study how a real Flask application is structured, deployed, tested, documented, and maintained over time.

## Why This Project Exists

Schools that introduce shared generative AI tools often face operational questions that are not solved by the AI service itself:

- Who is using a shared account, and when?
- How can reservation conflicts be avoided?
- How should usage logs be recorded for accountability?
- How can prompt writing be improved without turning the tool into an unrestricted chatbot?
- How can administrators manage users, resources, reports, backups, and basic audit history?

GPT Manager focuses on these practical needs. It does not store shared account passwords, does not control direct login to external AI services, and does not attempt to measure actual provider-side usage. Instead, it manages the school-side reservation, logging, prompt-review, and administration workflow around shared AI resources.

## Educational Philosophy

The project is also a long-term educational reference implementation for beginner backend students.

The guiding principle is that students should understand the architecture they learn from. The project is not meant to be copied blindly. It is meant to be read, discussed, modified carefully, and used as a working example of how backend concepts connect in a real application.

Students can study:

- request and response flow in Flask
- server-rendered pages with Jinja2
- CRUD workflows and form validation
- SQLite persistence and SQLAlchemy models
- authentication and role-based access
- service-layer organization
- testing with pytest and browser-level checks
- Docker-based local and server execution
- deployment with Gunicorn, Nginx, HTTPS, and an OCI Linux server
- documentation, maintenance notes, and architecture decisions

Generative AI tools such as ChatGPT, Codex, Claude, and Claude CLI are used as development assistants in this project, but they do not replace human judgment. Generated code is expected to be reviewed, understood, tested, and documented before it becomes part of the project.

## Project Status

This project is actively maintained as both a production-oriented school tool and a long-term educational reference project.

Rather than being a one-time classroom example, it evolves continuously through real-world development, testing, deployment, documentation, and maintenance.

Each academic year, it serves as a reference implementation for students learning Flask, SQLAlchemy, Docker, deployment, testing, backend software architecture, and software engineering practices. New features, documentation, and architectural improvements continue to evolve alongside classroom use and real operational requirements.

The long-term goal is to provide an open educational resource that helps students, educators, and future contributors understand how a real Flask application is designed, maintained, and continuously improved over time.

Current documented status includes:

- Flask application with SQLite, SQLAlchemy, Flask-Login, Jinja2, Tailwind CSS, and Vanilla JavaScript
- Docker Compose deployment with Gunicorn and Nginx reverse proxy
- school-oriented reservation, logging, prompt-review, reporting, backup, and administration workflows
- BYOK prompt-review support for OpenAI, Google Gemini, and Anthropic Claude
- pytest and Playwright-based verification documented in the Korean project status files
- active Korean documentation for operations, education, system design, deployment, UI decisions, and security decisions

## Key Features

- Local account registration, login, logout, and Google OAuth login
- User approval, suspension, role management, and assistant administrator access
- Reservation creation, cancellation, completion, calendar views, and conflict prevention
- Usage log creation, search, filtering, and reservation-linked reminders
- Administrator dashboard for users, AI resources, work types, reports, audit logs, CSV export, and SQLite backup
- BYOK AI provider settings with encrypted optional API key storage
- Prompt-review workflow for improving structured prompts without providing a general-purpose chatbot
- Terms, privacy policy, legal review checklist, and responsible-use guidance
- Docker Compose based execution for local and server environments

## Technology Stack

The stack is intentionally conservative because the project must be explainable to beginner backend students and maintainable in a school context.

| Area | Technology | Reason |
| --- | --- | --- |
| Language | Python | Clear learning path from syntax to backend development |
| Backend | Flask | Exposes HTTP routing, templates, CRUD, authentication, and deployment concepts directly |
| Data | SQLite + SQLAlchemy | Starts with a simple file database while introducing ORM modeling and relational persistence |
| Frontend | Jinja2 + Tailwind CSS + Vanilla JavaScript | Keeps the focus on web fundamentals before introducing SPA frameworks |
| Auth | Flask-Login + Google OAuth | Supports both local school workflows and external identity integration |
| AI integration | BYOK provider settings | Lets users configure their own provider keys for prompt review while limiting scope |
| Testing | pytest + Playwright | Covers backend behavior and selected browser-level workflows |
| Runtime | Docker Compose + Gunicorn + Nginx | Matches local and server execution while teaching production-oriented deployment basics |
| Deployment | OCI Ubuntu server | Gives students practical exposure to Linux server operations, HTTPS, domains, and reverse proxy setup |

## Documentation

Most detailed documentation is currently written in Korean because the project is actively developed and used in a Korean high school context. English documentation will expand gradually as the project matures.

Important Korean documents include:

- [`README.md`](README.md): primary Korean project entry point, setup notes, feature overview, and documentation map
- [`docs/EDUCATION.md`](docs/EDUCATION.md): educational goals, curriculum context, AI usage principles, and technology selection rationale
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md): current implementation status, verification notes, remaining work, and deployment status
- [`SYSTEM_DESIGN.md`](SYSTEM_DESIGN.md): architecture, data model, configuration, routes, and service structure
- [`docs/decisions/TECH_STACK_DECISIONS.md`](docs/decisions/TECH_STACK_DECISIONS.md): rationale for Flask, SQLite, Tailwind, Docker Compose, OCI, and BYOK design choices
- [`docs/decisions/SECURITY_DECISIONS.md`](docs/decisions/SECURITY_DECISIONS.md): security boundaries, data handling decisions, and excluded high-risk features
- [`docs/deployment/OCI_DEV_SERVER_SETUP.md`](docs/deployment/OCI_DEV_SERVER_SETUP.md): server deployment notes
- [`docs/development/DEVELOPMENT_LOG.md`](docs/development/DEVELOPMENT_LOG.md): development history and implementation notes

This English README is intended to orient international reviewers, educators, and contributors. It is not a complete replacement for the Korean documentation yet.

## Roadmap

The near-term roadmap is focused on making the project easier to review, operate, and reuse:

- continue keeping implementation status, test results, and deployment notes current
- expand English documentation for architecture, education, and contribution workflows
- refine setup instructions for educators who want to evaluate or adapt the project
- improve maintainability through focused tests, clearer module boundaries, and documented decisions
- preserve the beginner-friendly Flask architecture while allowing future schools to adapt resources, policies, and deployment settings
- keep security boundaries explicit, especially around shared account credentials, personal data, and BYOK API key handling

The project does not currently claim large-scale adoption or a broad contributor community. Its current value is grounded in real school use, project-based backend education, and continuous maintenance.

## Contributing

Contributions are welcome when they preserve the educational purpose and operational safety of the project.

Useful contribution areas include:

- documentation improvements, especially English companion documentation
- setup and deployment clarification
- tests for existing behavior
- small maintainability improvements that keep the Flask architecture understandable
- accessibility and UI consistency improvements
- educator-focused guides for adapting the project to another school context

Before proposing major architectural changes, contributors should review the Korean documentation and architecture decision records. The project intentionally avoids unnecessary complexity so that students can understand the system from request handling through deployment.

Contributions should not introduce features that store shared AI account credentials, weaken API key handling, collect unnecessary student personal data, or turn the prompt-review feature into an unrestricted chatbot.
