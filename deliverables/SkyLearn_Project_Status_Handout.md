# SkyLearn Project Status Handout

**Document type:** Internal project handout and technical status baseline<br>
**Prepared for:** SkyLearn project team<br>
**Status date:** 14 July 2026<br>
**Repository:** `SkyLearn-main`<br>
**Reviewed branch:** `main`<br>
**Reviewed revision:** `62018d3` — “Improve project README”<br>
**Document status:** Working source of truth; update it as changes are reviewed and merged

> [!IMPORTANT]
> SkyLearn is a functional development build with a substantial amount of working LMS functionality. It is not yet a production-ready release. At the time of review, before this handout was added, the local working tree contained 72 changed paths—64 modified and 8 untracked—so several improvements described here are present locally but are not yet represented by a clean, reviewable commit history.

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Product purpose and scope](#2-product-purpose-and-scope)
3. [Current status at a glance](#3-current-status-at-a-glance)
4. [Users, roles, and permissions](#4-users-roles-and-permissions)
5. [System architecture and technology](#5-system-architecture-and-technology)
6. [Application modules and data model](#6-application-modules-and-data-model)
7. [Functional requirements](#7-functional-requirements)
8. [End-to-end workflows](#8-end-to-end-workflows)
9. [Non-functional requirements](#9-non-functional-requirements)
10. [User interface and experience](#10-user-interface-and-experience)
11. [Testing and verification](#11-testing-and-verification)
12. [Security, privacy, and release risks](#12-security-privacy-and-release-risks)
13. [Installation, configuration, and deployment](#13-installation-configuration-and-deployment)
14. [Known limitations and documentation drift](#14-known-limitations-and-documentation-drift)
15. [Recommended delivery roadmap](#15-recommended-delivery-roadmap)
16. [Release readiness checklist](#16-release-readiness-checklist)
17. [Project metrics and local demo snapshot](#17-project-metrics-and-local-demo-snapshot)
18. [Team working agreement and ownership](#18-team-working-agreement-and-ownership)
19. [Glossary](#19-glossary)
20. [Evidence used for this handout](#20-evidence-used-for-this-handout)

---

## 1. Executive summary

SkyLearn is a Django-based learning management system intended for schools, colleges, and training institutes. It brings student and lecturer administration, academic structures, course access, learning resources, quizzes, grading, results, news, and institutional updates into one server-rendered web application.

The project already supports the main academic journey:

1. An administrator creates users, academic sessions, semesters, programs, and courses.
2. Lecturers are allocated to courses.
3. Students are enrolled directly, through self-registration, or through course packages.
4. Lecturers publish files, videos, quizzes, and scores for their allocated courses.
5. Students access registered courses, attempt quizzes, and view academic results.
6. The system calculates totals, grades, grade points, GPA, and CGPA.

The application is currently strongest in its core student, lecturer, course, quiz, and result workflows. Recent local changes also introduce a more polished public landing page, a branded login experience, a live administrative dashboard, and clearer guided forms for common administrative tasks.

The most important conclusion is that the next milestone should be a **stabilization release**, not broad feature expansion. Before the team presents the application as production-ready, it should secure the uncommitted work, close the highest-risk authorization and account-creation gaps, make test discovery complete, reconcile documentation, establish backups and production configuration, and perform structured browser, accessibility, and security testing.

### Overall assessment

| Area | Current assessment | Meaning |
|---|---|---|
| Core LMS functionality | Strong development implementation | Most primary academic workflows exist and are testable. |
| UI and presentation | Improved, with remaining legacy screens | Public and common admin experiences are considerably stronger; specialist workflows need the same treatment. |
| Automated verification | Healthy baseline | The default suite passes 48 tests; important gaps remain in coverage and test discovery. |
| Security | Partial | Good Django foundations and object checks exist, but several release-blocking issues remain. |
| Production operations | Early | Docker and CI definitions exist, but backups, monitoring, durable jobs, and deployment runbooks are incomplete. |
| Documentation | Mixed | The README has improved, but multiple documents overstate features or conflict with actual configuration. |
| Release readiness | Not ready | The current local state must be reviewed, committed, secured, and validated before release. |

### Immediate team decisions

The team should agree on the following before adding major features:

- Is public student self-sign-up intentionally supported, or should all student accounts be created by administrators?
- Should parents and department heads be part of the next release, or explicitly remain out of scope?
- Is payment processing a real product requirement? If not, remove dormant claims and UI references. If yes, treat it as a separate security-sensitive workstream.
- What exact dates govern course registration and dropping? The current use of the next-semester date as a closing boundary is ambiguous.
- What is the target production environment, storage model, Python version, backup policy, and release owner?

---

## 2. Product purpose and scope

### 2.1 Problem statement

Academic institutions frequently manage users, course allocation, learning materials, assessments, and results across disconnected tools and manual records. SkyLearn aims to provide one authenticated environment where academic data and day-to-day learning activities are organized around institutional roles and academic periods.

### 2.2 Product objectives

SkyLearn should:

- give students a clear view of their registered courses, resources, quizzes, and results;
- give lecturers controlled access to the courses they teach and the students enrolled in them;
- give administrators reliable tools for user, program, course, session, semester, and enrollment management;
- enforce role and course-level authorization on sensitive academic information;
- calculate and present academic performance consistently;
- provide a responsive, understandable interface on common desktop and mobile sizes;
- remain deployable in local, Docker, and production-style environments;
- preserve academic and personal data with appropriate security, privacy, audit, and recovery controls.

### 2.3 Current in-scope capabilities

- public landing page and authenticated login;
- student and lecturer account administration;
- user profiles and academic placement;
- academic sessions and semesters;
- programs, courses, lecturer allocations, and course packages;
- direct and student-led course registration;
- learning file and video resources;
- news and events;
- multiple-choice and essay quiz workflows;
- quiz attempts, review, marking, and analytics;
- continuous-assessment and examination scores;
- grade, GPA, and CGPA calculation;
- student result views and selected PDF outputs;
- administrative dashboard and cross-module search;
- configurable session-expiry warning and extension.

### 2.4 Partial or currently out-of-scope capabilities

The repository contains early or placeholder concepts that should not be presented as complete:

- parent portal workflows;
- department-head workflows;
- payment collection and reconciliation;
- a complete academic calendar and explicit registration-window engine;
- comprehensive localization across all visible text;
- production-grade observability, backup, and disaster recovery;
- a public API or mobile application;
- complete accessibility and cross-browser certification.

---

## 3. Current status at a glance

### 3.1 Verified repository state

| Check | Result |
|---|---|
| Django system check | Passed |
| Full default test suite | 48 tests passed in 17.017 seconds |
| Migration drift check | No model changes requiring migrations |
| Template compilation | 91 templates compiled successfully |
| Project JavaScript syntax | Passed for `landing.js` and `form-enhancements.js` |
| Live asset smoke check | Landing page, logo, JavaScript, and CSS responded successfully |
| Deployment check | One warning: the active local `SECRET_KEY` is too weak for production |
| Working tree | 72 changed paths: 64 modified, 8 untracked |

The checks above demonstrate that the current development snapshot runs and that its default automated suite is green. They do not prove production readiness, security compliance, accessibility compliance, or performance under real load.

### 3.2 Status legend

| Label | Definition |
|---|---|
| Implemented | The requirement has a working code path and is materially usable. |
| Implemented with caveats | The primary workflow works, but an important policy, security, UX, or reliability gap remains. |
| Partial | Some models, pages, or behaviors exist, but the end-to-end requirement is incomplete. |
| Not implemented | No operational end-to-end workflow exists. |
| Needs verification | Evidence exists, but structured acceptance testing has not yet established the result. |

### 3.3 Recommended project status statement

The group can accurately describe SkyLearn as:

> A working Django LMS development build with implemented student, lecturer, course, learning-resource, quiz, scoring, and result workflows; an improved public and administrative interface; and a passing automated test baseline. The project is now entering stabilization, with authorization, account policy, production operations, accessibility, and documentation work required before release.

The group should avoid describing the project as production-ready, fully secure, payment-enabled, fully localized, or complete for parent and department-head users.

---

## 4. Users, roles, and permissions

SkyLearn uses a custom user model with role flags and associated role-specific profiles. Access is enforced through a combination of authentication checks, role decorators, course-allocation queries, and object-level validation.

### 4.1 Role matrix

| Role | Intended responsibilities | Current access | Current limitations |
|---|---|---|---|
| Administrator / superuser | Configure the institution and manage academic users and structures | Student and lecturer CRUD, profiles, programs, courses, sessions, semesters, allocations, enrollment, packages, news/events, dashboards, reports | Operational actions need fuller audit trails; some legacy forms remain; production policies are not yet documented. |
| Lecturer | Deliver allocated courses and evaluate enrolled students | Allocated course resources, quizzes, attempts, analytics, and score entry | One result-sheet PDF route needs stronger course ownership enforcement; essay and reporting workflows need further acceptance testing. |
| Student | Participate in registered courses and review academic progress | Course registration/drop, resources, quizzes, results, profile | Registration period semantics are ambiguous; PDF robustness and some result edge cases need improvement. |
| Parent | Review a linked student's information | A parent data model and limited creation support exist | No complete parent dashboard or authorized end-to-end journey. |
| Department head | Supervise department-level activity | A department-head data model exists | No complete department-level portal, reporting, or approval workflow. |
| Anonymous visitor | Understand the product and authenticate | Landing page and login; search and registration are technically reachable | Public search and public student creation require an explicit policy decision. |

### 4.2 Authorization model

The codebase includes role decorators such as administrator, lecturer, and student restrictions. Course-sensitive operations also use helpers such as lecturer course queries, lecturer-course requirements, and checks that a student can access a course.

The intended rule is:

```text
Authenticated identity
        ↓
Role authorization
        ↓
Object/course ownership or enrollment check
        ↓
Allowed operation
```

Role checks alone are not sufficient. For example, being a lecturer should not allow a user to retrieve another lecturer's result sheet simply by changing a course identifier in a URL. Every route handling grades, enrollments, quiz attempts, resources, or personal data should enforce both role and object scope.

### 4.3 Account policy questions

Two routes require explicit product decisions:

- `/accounts/register/` can currently create student accounts without an administrator-authenticated journey. If institutional onboarding is administrator-controlled, this route should be protected or removed.
- The search view does not clearly require authentication. If search results contain courses, quizzes, programs, or internal updates, access should be aligned with the institution's privacy policy.

---

## 5. System architecture and technology

### 5.1 Architectural style

SkyLearn is a Django monolith using server-rendered HTML templates. Business domains are divided into Django applications, while authentication, navigation, styling, and configuration are shared across the project.

```text
Browser
  │
  ├── Public landing and login
  └── Authenticated role interface
          │
          ▼
Django URL routing → views/forms/services → Django ORM
          │                              │
          ├── templates/static assets    ├── SQLite for local development
          ├── email backend              └── PostgreSQL in Docker/production
          ├── PDF generation
          └── filesystem media storage
```

This structure is appropriate for the current project size and team. It supports straightforward development and deployment, but background work, storage, observability, and very high scale would eventually need stronger infrastructure boundaries.

### 5.2 Technology stack

| Layer | Technology |
|---|---|
| Application framework | Django 4.0.8 |
| Language | Python; the reviewed local environment uses Python 3.11 |
| Front end | Django templates, HTML, Bootstrap 5.3.2, custom CSS, custom JavaScript |
| Icons | Font Awesome 6.5.1 |
| Forms and filters | `django-crispy-forms`, `django-filter`, `django-widget-tweaks` |
| Translation support | Django i18n and `django-modeltranslation` |
| Development utilities | `django-extensions` |
| Local database | SQLite |
| Docker/production database | PostgreSQL through `DATABASE_URL` |
| Static files | WhiteNoise |
| Media files | Local filesystem or Docker volumes |
| Application server | Gunicorn with three workers in the production container |
| PDF generation | ReportLab and xhtml2pdf |
| Email | SMTP by default; console, file, or in-memory backends can be configured |
| Containerization | Docker and Docker Compose |
| CI definitions | GitHub Actions, Jenkins, and Bitbucket pipeline files |

### 5.3 Important architectural constraints

- Media is filesystem-based. Multiple application instances will require shared or object storage.
- Email generation uses process-local background threading in places. A worker restart can lose unsent work.
- The cache and session design must be reviewed for multi-instance deployment.
- The application is server-rendered and has no documented public API contract.
- Operational reporting and audit data are not yet centralized.
- Dependency and Python-version expectations differ across local, Docker, and CI configurations.

---

## 6. Application modules and data model

### 6.1 `accounts`

**Purpose:** Identity, roles, student academic profiles, lecturer administration, and related profile operations.

Key data:

- `User`: custom authentication entity with unique email, role flags, gender, phone, address, and profile image;
- `Student`: connects a user to program, level, and year;
- `Parent`: represents a parent linked to student information;
- `DepartmentHead`: represents department-level responsibility.

Implemented behavior includes student and lecturer creation, listing, editing, deleting, viewing profiles, password operations, academic placement, filtering, and selected PDF output. Account-creation signals generate institutional-style usernames and temporary passwords and attempt to send credentials by email.

### 6.2 `core`

**Purpose:** Public entry, authenticated home experience, institutional updates, academic periods, dashboard data, and activity records.

Key data:

- `NewsAndEvents`: news or event posts;
- `Session`: academic session;
- `Semester`: academic semester;
- `ActivityLog`: selected activity records.

The module contains the public landing page, authenticated home/dashboard behavior, news and event CRUD, session and semester management, and general site-level UI.

### 6.3 `course`

**Purpose:** Academic catalog, teaching allocation, enrollment, packages, and course resources.

Key data:

- `Program`: academic program;
- `Course`: academic course and metadata;
- `CourseAllocation`: associates lecturers with courses;
- `CoursePackage`: defines a program/level/year group of courses;
- `Upload`: file-based course resource;
- `UploadVideo`: video resource;
- `CourseOffer`: placeholder or incomplete concept.

Enrollment records are stored in `TakenCourse` in the `result` application. The module supports program and course management, lecturer allocation, administrator enrollment, course packages, student registration/drop, course-specific resource access, and role-based course lists.

### 6.4 `quiz`

**Purpose:** Assessment authoring, attempts, scoring, manual marking, and quiz analysis.

Key data:

- `Quiz`: quiz settings and relationship to a course;
- `Question`: shared question base;
- `MCQuestion`: multiple-choice question;
- `Choice`: available multiple-choice answer;
- `EssayQuestion`: manually graded question;
- `Sitting`: a student's quiz attempt and state;
- `Progress`: accumulated performance information.

The module includes quiz configuration, question and choice authoring, attempt authorization, randomized order settings, pass marks, one-attempt behavior, answer review options, stored exam papers, manual essay marking, and lecturer analytics.

### 6.5 `result`

**Purpose:** Enrollment-linked scoring, grades, academic-period performance, GPA, and CGPA.

Key data:

- `TakenCourse`: connects a student and course and stores assignment, mid-exam, quiz, attendance, final-exam, total, grade, grade point, and result comment;
- `Result`: stores GPA/CGPA information by student, semester, session, and level.

The application enforces a unique student-course enrollment and a unique result record for the relevant academic period. Score updates derive total marks, grade, grade point, and pass/fail status, then update GPA/CGPA records.

### 6.6 `search`

**Purpose:** Cross-module search.

The search view queries news/events, programs, courses, and quizzes. It has no persistent model. Its anonymous-access policy should be reviewed.

### 6.7 `payment`

**Purpose:** Intended payment capability.

The application contains empty model/view/URL areas and some templates or dependency references, but no operational payment workflow. Payment should therefore be classified as **not implemented**.

### 6.8 Data relationship summary

```text
User
├── Student ── Program
├── Parent ── Student relationship (partial journey)
└── DepartmentHead (partial journey)

Program
├── Course
├── Student cohort
└── CoursePackage ── target level/year ── Courses

Course
├── CourseAllocation ── Lecturer/User
├── TakenCourse ── Student
├── Upload / UploadVideo
└── Quiz
      ├── Question
      │    ├── MCQuestion ── Choice
      │    └── EssayQuestion
      └── Sitting ── Student

Student
└── Result ── Session + Semester + Level
```

The repository contains approximately 21 concrete model classes and 22 project migration files.

---

## 7. Functional requirements

The following matrix records what the application should do, what currently exists, and what remains before the behavior can be accepted as release-ready.

### FR-01 — Public landing and login

**Requirement:** Anonymous visitors must see a clear SkyLearn landing page, understand the main product value, and be able to navigate to a dedicated login page. Authenticated users visiting the public root should be redirected to their home experience.

**Status:** Implemented.

**Current evidence:** The root page presents SkyLearn branding and product information; a login action opens the authentication page; authenticated root access redirects to `/home/`; landing assets and logo were live-smoke-tested.

**Acceptance notes:** Retain the restrained editorial design, keyboard-visible navigation, responsive behavior, and truthful product claims. Do not advertise unfinished payment or role capabilities.

### FR-02 — Authentication and role-based access control

**Requirement:** Protected functions must require authentication and must be limited by user role and, where relevant, ownership, allocation, or enrollment.

**Status:** Implemented with caveats.

**Current evidence:** Administrator, lecturer, and student restrictions exist. Course-aware helpers protect many resource, quiz, enrollment, and score operations.

**Remaining work:** Fix course scoping on the lecturer result-sheet PDF route; decide policies for public search and public registration; audit every identifier-based route for object-level authorization.

### FR-03 — User and profile management

**Requirement:** Administrators must create and manage student and lecturer accounts, including contact information, role, academic placement, profile access, password support, and appropriate reporting.

**Status:** Implemented with caveats.

**Current evidence:** Student/lecturer create, list, view, edit, delete, filter, profile, password, and selected PDF workflows exist.

**Remaining work:** Define deletion/retention rules for historical academic records, strengthen audit capture, verify profile-image handling, and review PDF content and branding.

### FR-04 — Credential generation and delivery

**Requirement:** New institutional users must receive secure, usable account activation instructions without exposing credentials to unrelated sessions or long-lived storage.

**Status:** Implemented with caveats.

**Current evidence:** Signals generate prefixed identifiers and passwords, store passwords using Django hashing, attempt email delivery, and restrict the temporary credential display to the creating administrator using creator-session and short-lived per-student cache behavior.

**Remaining work:** Replace plaintext password email with an activation or set-password link; move mail to a durable job queue; add delivery status/retry; ensure temporary secrets never enter logs or analytics.

### FR-05 — Academic sessions and semesters

**Requirement:** Administrators must create, update, and select the current academic session and semester, with only one current record of each type according to application rules.

**Status:** Implemented.

**Current evidence:** CRUD and current-period switching exist; selecting a current period unsets the previous current record.

**Remaining work:** Add database-level or transactional guarantees for concurrency and define the relationship to registration windows and result finalization.

### FR-06 — Programs and courses

**Requirement:** Administrators must manage the institutional program and course catalog, including program association and course metadata used by enrollment and results.

**Status:** Implemented.

**Current evidence:** Program and course creation, editing, listing, and deletion exist with refreshed guided forms for common operations.

**Remaining work:** Confirm archival rules for courses already used in results and validate all uniqueness/business constraints against institutional policy.

### FR-07 — Lecturer allocation

**Requirement:** Administrators must allocate one or more lecturers to courses, and lecturers must only manage allocated courses.

**Status:** Implemented.

**Current evidence:** Allocation workflows and lecturer-course query restrictions exist.

**Remaining work:** Complete the authorization audit for all lecturer exports and reporting routes and define how allocations change across academic periods.

### FR-08 — Administrator-led student enrollment

**Requirement:** Authorized staff must add or remove eligible students from a course while preserving academic records that already contain scores.

**Status:** Implemented.

**Current evidence:** Course rosters, eligible-candidate filtering, a 200-candidate handling cap, duplicate prevention, and protection against removal of scored enrollments are implemented.

**Remaining work:** Define behavior for cohorts larger than the cap, add bulk-operation feedback and export, and ensure period-specific enrollment policy is explicit.

### FR-09 — Course packages and automatic allocation

**Requirement:** Administrators must define a course package for a program, level, and year and apply it to matching students without assigning incompatible courses.

**Status:** Implemented with caveats.

**Current evidence:** Package targets, manual allotment, cohort validation, and automatic allotment during student creation are present.

**Remaining work:** The reviewed local database contains no packages, so the workflow needs realistic acceptance data; package changes after enrollment need a defined reconciliation policy.

### FR-10 — Student course registration and dropping

**Requirement:** Students must register eligible courses and drop permissible courses only within authorized periods. They must not register incompatible, duplicate, or unauthorized courses, and must not remove scored academic records.

**Status:** Implemented with caveats.

**Current evidence:** Server-side program and level validation, duplicate prevention, POST-only drop behavior, and scored-course protection exist.

**Remaining work:** Replace the overloaded `next_semester_begins` boundary with explicit open/close registration dates and documented late-registration/withdrawal rules.

### FR-11 — Course access and learning resources

**Requirement:** Registered students and allocated lecturers must access a course space. Lecturers must add, edit, and remove learning files or videos, and unauthorized users must be blocked.

**Status:** Implemented.

**Current evidence:** Course access checks, file upload, video upload, edit, and delete flows exist.

**Remaining work:** Add upload size, MIME, content, malware, and quota controls; move production media to appropriate isolated storage; verify inaccessible direct media URLs.

### FR-12 — News and events

**Requirement:** Authorized users must publish institutional news and event information with clear type, title, summary, and display behavior.

**Status:** Implemented with caveats.

**Current evidence:** Post creation and management exist; the post form has been redesigned with clearer grouping and actions.

**Remaining work:** Add an explicit calendar model if event dates, reminders, attendance, or registration are required; define who can publish and moderate content.

### FR-13 — Quiz authoring

**Requirement:** Lecturers must create course quizzes, configure assessment behavior, and add multiple-choice or essay questions only for courses they control.

**Status:** Implemented.

**Current evidence:** Quiz settings, question creation, choice creation, and course-ownership rules exist.

**Remaining work:** Improve the multi-step authoring UI, add clearer draft/publish state, question preview, validation summaries, and safe duplication/versioning.

### FR-14 — Quiz participation

**Requirement:** Eligible students must start and complete valid quizzes according to configured rules, with forged answers rejected and attempt state preserved correctly.

**Status:** Implemented with caveats.

**Current evidence:** Draft and empty-quiz checks, random order, pass mark, single-attempt mode, answer-at-end settings, stored exam papers, and answer validation exist.

**Remaining work:** Define interruption/resume behavior, time-limit enforcement, concurrent-session handling, and accommodations; essay questions require manual grading.

### FR-15 — Quiz review, marking, and analytics

**Requirement:** Lecturers must review authorized attempts, mark manual questions, and understand quiz performance.

**Status:** Implemented.

**Current evidence:** Sittings, manual marking, quiz dashboards, pass rates, score ranges, recent activity, and approximate question-difficulty reporting exist.

**Remaining work:** Validate metric definitions, distinguish auto-graded from pending-manual results, and add export/audit requirements where needed.

### FR-16 — Score entry and grade calculation

**Requirement:** Lecturers must enter approved components for enrolled students in allocated courses. The system must validate the aggregate and derive total, grade, grade point, pass/fail status, GPA, and CGPA consistently.

**Status:** Implemented.

**Current evidence:** Assignment, mid-exam, quiz, attendance, and final-exam components are supported; aggregate marks cannot exceed 100; updates are transactional; derived grade and result fields are maintained.

**Remaining work:** Document the grading scale as an institutional policy, add amendment/finalization workflows, and retain before/after audit history for grade changes.

### FR-17 — Student results and PDF reports

**Requirement:** Students must see only their results, and authorized staff must generate accurate, institutionally branded reports without exposing another course or student's data.

**Status:** Implemented with caveats.

**Current evidence:** Result screens and selected PDFs exist.

**Remaining work:** Correct lecturer course scoping on the result-sheet PDF; replace hardcoded institution text in the registration PDF; handle missing current-period results gracefully; review all PDF authorization, typography, and branding.

### FR-18 — Dashboard and search

**Requirement:** Users must receive role-relevant summaries and be able to locate permitted information efficiently.

**Status:** Implemented with caveats.

**Current evidence:** The administrative dashboard uses live metrics; quiz dashboards are data-backed; search covers news/events, programs, courses, and quizzes.

**Remaining work:** Enforce a clear search access policy, check query performance at scale, document metric definitions, and avoid exposing restricted objects in result snippets.

### FR-19 — Session timeout and extension

**Requirement:** Inactive authenticated sessions must warn users before expiry and allow an explicit extension without background polling silently keeping the session alive.

**Status:** Implemented.

**Current evidence:** A session warning and extension flow exists; polling does not refresh the session, while explicit extension does.

**Remaining work:** Validate behavior across multiple tabs, mobile sleep/wake, expired CSRF tokens, and long-running quiz or score-entry tasks.

### FR-20 — Internationalization

**Requirement:** The interface and translatable model content must support the institution's approved languages with complete, maintained catalogs.

**Status:** Partial.

**Current evidence:** English, French, Spanish, and Russian are configured and model translation support exists.

**Remaining work:** Only limited Spanish locale material is present and the visible interface is not comprehensively translated. Establish translation ownership, completeness checks, fallback behavior, and localization QA.

### FR-21 — Parent and department-head experiences

**Requirement:** If included in product scope, parents and department heads must have dedicated, authorized journeys with clearly defined data access.

**Status:** Partial.

**Current evidence:** Relevant models and limited parent creation support exist; a course-offer concept is also present.

**Remaining work:** Define use cases and permissions before building. Do not expose student grades or personal information based only on an incomplete relationship model.

### FR-22 — Payments

**Requirement:** If payment is in scope, users must initiate payments, receive verified status, and administrators must reconcile transactions, refunds, failures, and webhook events securely.

**Status:** Not implemented.

**Current evidence:** Empty application areas and dormant key settings exist, but no complete transaction workflow.

**Remaining work:** Make an explicit go/no-go decision. A real implementation needs provider-hosted or tokenized payment handling, server-side amount validation, signed webhook verification, idempotency, transaction ledgers, reconciliation, refund handling, audit records, security review, and dedicated tests.

---

## 8. End-to-end workflows

### 8.1 Student onboarding

1. An administrator opens the Add Student form.
2. The server validates user and academic fields.
3. A transaction creates the custom `User` and associated `Student` record.
4. Account signals generate an institution-prefixed username and temporary password.
5. Django stores the password as a secure hash.
6. The application attempts to email the credentials.
7. A short-lived credential view is made available only to the creating administrator through session/cache isolation.
8. Matching active course packages may automatically create course enrollments for the student's program, level, and year.

**What works well:** Atomic creation, credential isolation, password hashing, and package cohort validation.

**What must improve:** Replace plaintext credential email, make delivery durable and observable, decide whether public registration is permitted, and create a user-facing activation journey.

### 8.2 Course setup and delivery

1. An administrator creates a program and its courses.
2. A lecturer is allocated to a course.
3. Students are enrolled by administrators, packages, or eligible self-registration.
4. The lecturer opens an allocated course.
5. The lecturer publishes files, videos, and quizzes.
6. Registered students open the course and access its permitted material.
7. Object-level checks prevent unrelated lecturers or students from managing or consuming the course.

**What works well:** Clear domain separation, allocation/enrollment concepts, and reusable course access checks.

**What must improve:** Production-safe uploads, period-aware allocation/enrollment, bulk operation UX, and consistent authorization on every export.

### 8.3 Quiz lifecycle

1. A lecturer creates a quiz for an allocated course.
2. The lecturer configures settings and adds multiple-choice or essay questions.
3. Draft or empty assessments are blocked from normal participation.
4. An authorized student starts a `Sitting`.
5. Each submitted answer is validated against the expected question and available choices.
6. Auto-gradable answers update attempt and progress state.
7. Completion behavior applies pass marks, answer-review settings, single-attempt rules, and exam-paper retention.
8. The lecturer reviews sittings, manually grades essay content, and views analytics.

**What works well:** Forged-choice protection, configurable behavior, stored attempt state, and lecturer analysis.

**What must improve:** Authoring UX, interruption policy, timed-assessment guarantees, manual-grade status visibility, accommodations, and assessment audit history.

### 8.4 Score and result lifecycle

1. A lecturer selects an allocated course in the current academic context.
2. The application lists enrolled students.
3. The lecturer enters the configured component marks.
4. The server validates that every submitted student belongs to the course and that the aggregate does not exceed 100.
5. The update is saved atomically.
6. `TakenCourse` derives total, grade, grade point, and pass/fail comment.
7. The relevant period `Result` is created or updated for GPA and CGPA.
8. The student views the result; authorized staff may generate reports.

**What works well:** Enrollment validation, allocation constraints in core score views, aggregate validation, atomic persistence, and derived academic calculations.

**What must improve:** Grade finalization/amendment, audit history, missing-period handling, PDF course scoping, institutional branding, and formal grading-policy signoff.

---

## 9. Non-functional requirements

Functional requirements describe what the system does. Non-functional requirements describe how safely, reliably, efficiently, and clearly it must do it.

### NFR-01 — Security

**Required outcome:** Sensitive academic and personal operations are protected by secure authentication, authorization, input validation, session management, deployment configuration, and vulnerability management.

**Current status:** Partial.

**Controls present:**

- Django password hashing and validators;
- environment-driven secret and deployment settings;
- CSRF protection;
- HTTP-only and configurable secure cookies;
- SSL redirect and HSTS configuration options;
- content-type sniffing protection and frame denial;
- role and many object-level checks;
- POST-only destructive actions in improved flows;
- database uniqueness constraints and transactions;
- targeted tests for authorization, forged input, and score limits;
- configurable session timeout and explicit extension.

**Required improvements:**

- close the result-sheet PDF object-authorization gap;
- restrict or formally approve public account creation and search;
- use a strong production secret and explicit hosts/origins/TLS configuration;
- add login throttling, lockout policy, and preferably MFA for privileged accounts;
- strengthen file validation and storage isolation;
- replace plaintext temporary-password email;
- introduce dependency, container, and secret scanning;
- record security-sensitive changes with actor and context;
- perform a focused OWASP-style review before release.

### NFR-02 — Privacy and data governance

**Required outcome:** Personal information, contact details, grades, quiz attempts, and credentials are collected and retained only for defined institutional purposes and are disclosed only to authorized users.

**Current status:** Partial.

The data model necessarily stores personally identifiable and educational information. However, the repository does not yet establish a complete retention schedule, consent/legal-basis record, export/access procedure, correction process, deletion/anonymization policy, breach-response process, or production-data handling guide.

Before real institutional data is loaded, the team must document:

- the data owner and system administrator;
- each role's permitted data access;
- retention periods for accounts, attempts, results, logs, uploads, and backups;
- how a user requests access or correction;
- how departed users are disabled or anonymized while academic records remain valid;
- which environments may contain production data;
- how demonstration data is sanitized;
- breach escalation and notification responsibilities.

### NFR-03 — Usability

**Required outcome:** Common tasks should be understandable without specialized technical knowledge, provide clear feedback, prevent avoidable errors, and recover safely from invalid input.

**Current status:** Implemented with caveats.

The project now has a stronger landing/login journey, role-aware navigation, responsive layouts, messages, filters, and guided forms. Common create/edit forms use clearer grouping, context panels, progress cues, and action placement.

Remaining specialist flows—especially quiz authoring, bulk enrollment, package administration, uploads, and selected settings—should adopt the same interaction language. Destructive actions should consistently require clear confirmation and describe consequences.

### NFR-04 — Accessibility

**Required outcome:** The application should target WCAG 2.1 AA for core journeys, including keyboard operation, visible focus, semantic structure, labels, contrast, error identification, motion preferences, and screen-reader clarity.

**Current status:** Needs verification.

Positive foundations include a skip link, visible labels/ARIA in parts of the interface, keyboard-aware sidebar behavior, reduced-motion handling, and a semantic landing page. No formal accessibility audit has yet been recorded.

Required validation should cover:

- keyboard-only completion of login, navigation, student creation, course registration, quiz participation, score entry, and result viewing;
- automated checks using axe or an equivalent tool;
- screen-reader spot checks;
- contrast in default, hover, focus, error, and disabled states;
- zoom to 200–400% and reflow at narrow widths;
- accessible validation summaries and field-level errors;
- reduced-motion behavior for dynamic landing-page effects.

### NFR-05 — Performance

**Required outcome:** Common pages and administrative operations should remain responsive for realistic institutional data volumes.

**Current status:** Partial.

The code uses pagination, relationship preloading/selection, annotations, and a 200-record enrollment candidate cap in relevant areas. No formal response-time objective, query budget, load profile, or benchmark report exists.

The team should define representative sizes—for example users, courses, enrollments, concurrent quiz attempts, and uploads—then measure dashboard queries, search, student lists, course rosters, score entry, result calculation, and PDF generation. Add query-count regression tests for high-value pages.

### NFR-06 — Scalability

**Required outcome:** The application should support the target institution size and allow safe horizontal growth where required.

**Current status:** Partial.

PostgreSQL and a three-worker Gunicorn container provide a reasonable initial deployment base. Filesystem media, in-process email threads, cache assumptions, synchronous PDF generation, and monolithic reporting limit horizontal scale.

If scale requires multiple application instances, introduce shared sessions/cache, object storage, a durable job queue, worker monitoring, and database/index review.

### NFR-07 — Reliability and data integrity

**Required outcome:** Academic operations must either complete consistently or fail without leaving partial or contradictory data.

**Current status:** Partial.

Transactions, uniqueness constraints, score validation, and protected enrollment removal improve integrity. The project still needs durable asynchronous processing, retry/idempotency rules, service health checks, failure-mode tests, and operational recovery procedures.

Particular attention is required for account creation plus email delivery, bulk enrollment, package reapplication, quiz interruption, grade updates, and PDF generation.

### NFR-08 — Maintainability

**Required outcome:** New contributors should be able to understand, test, review, and change the system without introducing unrelated regressions.

**Current status:** Partial.

Strengths include domain-oriented Django applications, migrations, tests, environment configuration, reusable templates, and recent UI components. Risks include large view modules, legacy commented code, a growing CSS override layer, old specialist templates, inconsistent documentation, and broad uncommitted changes.

The stabilization milestone should split changes into intentional commits, remove dead code, isolate domain services where views are too large, document grading/authorization rules, and establish code-review ownership.

### NFR-09 — Portability

**Required outcome:** The project should run consistently on supported developer and deployment platforms.

**Current status:** Implemented with caveats.

Local Windows development and Docker workflows exist. Python targets are inconsistent: GitHub workflows reference 3.8/3.9, Docker uses 3.10, and the reviewed local environment uses 3.11. Select and document a supported version range, then use it in development, CI, and containers.

### NFR-10 — Browser and device compatibility

**Required outcome:** Core journeys should work on the institution's supported evergreen browsers and responsive viewport sizes.

**Current status:** Needs verification.

Bootstrap and progressive JavaScript behavior provide a sound baseline, but no recorded compatibility matrix exists. At minimum, test current Chrome, Edge, Firefox, and Safari, plus representative Android and iOS widths. Include JavaScript-disabled fallback expectations where relevant.

### NFR-11 — Localization

**Required outcome:** Approved languages should provide complete, accurate interface text, consistent dates/numbers, and sensible fallback behavior.

**Current status:** Partial.

Language configuration exceeds the actual translated catalog. Translation completeness and review ownership must be established before multilingual support is advertised.

### NFR-12 — Observability and auditability

**Required outcome:** Operators should know whether the system is healthy, investigate failures, and reconstruct sensitive administrative actions.

**Current status:** Not implemented to a production standard.

Console logs and a selective `ActivityLog` exist, but there is no centralized structured logging, error tracking, metrics, alerting, request correlation, or complete audit trail.

Production readiness requires:

- structured application and security logs;
- error capture with environment/release context;
- uptime, latency, error-rate, worker, database, storage, and email-delivery metrics;
- alerts with named responders;
- immutable audit events for user, allocation, enrollment, grade, result, and configuration changes;
- actor, timestamp, target, action, outcome, and appropriate before/after metadata;
- safeguards that prevent passwords, tokens, or unnecessary PII from entering logs.

### NFR-13 — Deployability

**Required outcome:** A versioned build should move through test, staging, production, smoke verification, and rollback using documented repeatable steps.

**Current status:** Partial.

Docker and several CI definitions exist, but deployment steps are partly placeholders and environments are inconsistent. A release needs one authoritative pipeline, immutable image tagging, migration strategy, static/media strategy, health checks, staging approval, smoke tests, and rollback ownership.

### NFR-14 — Backup and recoverability

**Required outcome:** The institution must be able to recover database and media data after accidental deletion, corruption, or infrastructure failure within agreed recovery objectives.

**Current status:** Not implemented/documented.

Define recovery point objective (acceptable data loss) and recovery time objective (acceptable downtime), automate encrypted database and media backups, store copies outside the primary environment, restrict access, monitor backup success, and conduct restore drills. A backup that has never been restored is not verified.

---

## 10. User interface and experience

### 10.1 Current design direction

The recent UI direction is more restrained and presentable than a generic template-heavy LMS. The public experience uses an editorial layout, clear typography, SkyLearn branding, controlled motion, and concise product content. The authenticated application retains a practical sidebar/topbar structure suited to frequent institutional use.

The design should continue to favor:

- a limited blue-led color system with purposeful accent use;
- strong information hierarchy instead of decorative card grids;
- real data and role-specific context;
- consistent spacing, radii, input states, and actions;
- subtle motion that helps orientation rather than distracting from tasks;
- progressive disclosure for complex academic workflows;
- accessible focus, error, disabled, and loading states.

### 10.2 Improvements currently present

- a public SkyLearn landing page with logo, sticky header, scroll progress, active navigation, subtle section reveals, role-oriented content, and login calls to action;
- a dedicated branded login page;
- responsive authenticated navigation with sidebar/topbar patterns;
- flash-message presentation, language access, and session-expiry warning;
- an administrative dashboard backed by live data rather than fixed placeholder counts;
- guided create forms for posts, students, lecturers, programs, courses, sessions, and semesters;
- guided edit forms for student and lecturer records;
- contextual side panels, clearer section grouping, responsive field grids, and improved action bars in common forms.

### 10.3 Remaining UI priorities

#### Quiz authoring

Convert the current sequence into a visible draft workflow: Basics → Rules → Questions → Preview → Publish. Show question counts and validation problems, support reorder/duplicate, and clearly distinguish unpublished, available, closed, and graded states.

#### Enrollment and course packages

Make eligibility rules visible before selection. Add search, select-all within the filtered set, persistent selection counts, a summary of additions/removals, and precise warnings when scored enrollment records cannot be removed.

#### Resource upload

Show permitted file types and maximum size before submission; provide progress, validation, retry, and upload status. Separate files, videos, and external links with appropriate metadata.

#### Score entry

Use a spreadsheet-like but accessible table with sticky identity columns, component limits, unsaved-change indication, row validation, aggregate preview, and confirmation before finalization. Avoid silent overwrites.

#### Results and reports

Show the academic period and grading legend consistently, handle empty states without errors, and align screen and PDF branding. Clearly label provisional versus finalized grades.

#### Dynamic behavior

Dynamic effects should communicate state: progress through a long form, saved/unsaved changes, upload progress, new dashboard data, session expiry, or filtered results. Decorative animation should remain subtle and honor reduced-motion preferences.

### 10.4 UI acceptance checklist

For each primary screen, verify:

- the page title answers “where am I?”;
- the primary action is obvious and unique;
- secondary/cancel actions are consistent;
- required fields and constraints are stated before submission;
- server errors appear both in a summary and beside the relevant field where practical;
- loading, empty, success, permission-denied, and failure states are designed;
- keyboard focus follows dialogs, menus, and validation correctly;
- content reflows without horizontal loss on narrow screens;
- data shown belongs to the current role and academic context;
- motion is purposeful and can be reduced.

---

## 11. Testing and verification

### 11.1 Latest verified results

The reviewed project completed the following checks successfully:

```text
Django system check:                  PASS
Default automated suite:              48 tests PASS
Default suite runtime:                17.017 seconds
Pending model migration check:        PASS — no changes detected
Template compilation:                 PASS — 91 templates
Project JavaScript syntax checks:     PASS
Landing/logo/CSS/JS HTTP smoke check: PASS
Deployment check:                     1 warning — weak local SECRET_KEY
```

### 11.2 Existing automated coverage

The current tests cover meaningful security and workflow cases, including:

- account credential isolation;
- POST-only deletion behavior;
- role decorators and user filtering;
- session timeout behavior;
- landing and authenticated root routing;
- guided administrative forms;
- academic-period changes and post deletion;
- live administrative dashboard data;
- lecturer allocation and course authorization;
- enrollment restrictions and forged registration attempts;
- protected course dropping;
- course-package cohort validation;
- forged multiple-choice answer protection;
- lecturer score scope;
- forged enrollment rows in score submission;
- valid score updates and aggregate mark limits.

### 11.3 Test discovery gap

Approximately 50 `def test_...` methods exist in the repository, while the default test run discovers 48. Two tests under `quiz/tests/test_quiz_access.py` are not included by default. The project also has a `quiz/tests.py` module, and the `quiz/tests/` directory lacks the package structure needed for reliable discovery.

**Required action:** Normalize the test layout—prefer a package such as `quiz/tests/__init__.py` with all quiz tests inside it—and confirm the expected test count in CI. A green suite is only meaningful when the intended tests are actually discovered.

### 11.4 Required test expansion

#### Unit and model tests

- grade boundaries, grade points, GPA, and CGPA across edge cases;
- current session/semester concurrency behavior;
- package edits and repeated allotment idempotency;
- upload validation;
- account activation and email retry behavior after redesign;
- result behavior when no current academic period exists.

#### Authorization tests

- every user-controlled identifier on view, edit, delete, download, PDF, and export routes;
- lecturer result-sheet PDF access to another lecturer's course;
- anonymous search and registration policy;
- direct media access;
- parent and department-head access before those roles are enabled.

#### Integration tests

- full student onboarding including email/activation and package enrollment;
- course setup through student access;
- quiz creation through grading;
- score submission through result display and PDF generation;
- transaction rollback on partial failures.

#### Browser end-to-end tests

- landing → login → role dashboard;
- administrator creates a student and sees activation state;
- lecturer uploads a resource and student accesses it;
- student registers/drops a course under permitted conditions;
- student completes a quiz including invalid/expired states;
- lecturer enters scores and student views results;
- session warning and extension;
- mobile navigation and long forms.

#### Quality tests

- accessibility scan and keyboard test;
- cross-browser matrix;
- database query budgets for high-use pages;
- load tests for login, dashboards, rosters, quiz submissions, and result reads;
- dependency/container/security scans;
- backup restore exercise;
- migration rehearsal against production-like PostgreSQL data.

### 11.5 Suggested definition of done

A feature is done only when:

1. its business rule and permitted roles are written down;
2. server-side validation and object authorization are implemented;
3. success, empty, invalid, forbidden, and failure states are handled;
4. automated tests cover the happy path and important abuse/edge cases;
5. the UI is keyboard-usable and responsive;
6. migrations and configuration are documented;
7. logs do not expose secrets or unnecessary personal data;
8. the relevant handout/README information is updated;
9. the change is reviewed in an intentional commit or pull request.

---

## 12. Security, privacy, and release risks

### 12.1 Priority definitions

- **P0 — release blocker:** Must be resolved before a production or institutional pilot release.
- **P1 — high priority:** Should be resolved during stabilization or explicitly accepted by the project owner with controls.
- **P2 — improvement:** Important for maintainability, polish, or later scale, but not necessarily a pilot blocker.

### 12.2 P0 release blockers

| Risk | Why it matters | Required response |
|---|---|---|
| Broad uncommitted working tree | The 72 pre-handout changed paths cannot be reliably reviewed, reproduced, or rolled back as one informal snapshot. Untracked migrations/assets/tests can be omitted accidentally. | Create a stabilization branch, inventory every change, split it into coherent commits, review diffs, and run the full verification suite on the committed state. |
| Public student account creation | An anonymous route can create student records even though institutional onboarding appears administrator-oriented. | Decide the policy. Protect/remove the route if public signup is not required; otherwise add a secure approval, verification, anti-abuse, and activation process. |
| Result-sheet PDF course authorization | A lecturer-protected PDF view does not appear to scope the requested course through the lecturer's allocations. A lecturer may be able to change the identifier and retrieve another course's results. | Apply the same lecturer-course ownership helper used elsewhere and add a regression test for cross-course access. |
| Production secret/TLS/host configuration | The deployment check reports a weak local secret. Reusing it or permissive host settings in production compromises security. | Generate a strong production-only secret, set allowed hosts and trusted origins, enable HTTPS cookie/redirect/HSTS settings after TLS is proven, and keep secrets out of source control. |
| No verified backup and restore process | Academic records and uploaded resources could be lost without an operational recovery path. | Implement encrypted database and media backups, off-primary storage, monitoring, documented RPO/RTO, and a successful restore drill. |

### 12.3 P1 high-priority risks

| Risk | Recommended treatment |
|---|---|
| Upload validation relies mainly on extensions | Enforce size, MIME/content checks, safe names, quotas, storage isolation, download headers, and malware scanning appropriate to the environment. |
| Temporary passwords are emailed in plaintext | Use time-limited activation/set-password links and a durable email queue with retry and delivery status. |
| Process-local email threading | Replace with a managed queue/worker or a reliable synchronous strategy for the initial deployment. |
| Search access policy is unclear | Require login or intentionally limit and sanitize anonymous results. Add tests. |
| No rate limiting, lockout, or MFA | Add throttling and account protections, especially for administrators and lecturers. |
| Audit coverage is incomplete | Record actor, target, action, outcome, timestamp, and selected before/after changes for accounts, enrollment, allocation, grades, and configuration. |
| No documented PII lifecycle | Establish retention, access, correction, deletion/anonymization, environment, and breach procedures. |
| Older dependency baseline | Run dependency and container scanning, review Django support status, and schedule controlled upgrades. |
| Registration boundary is ambiguous | Introduce explicit registration open/close and withdrawal dates with timezone-aware tests. |
| PDF branding and edge-case behavior | Remove hardcoded institution text, fix typos, use configured school identity, and handle missing results/current periods safely. |
| Product claims exceed implementation | Remove or qualify payment, parent, department-head, and localization claims until they are complete. |
| CI/environment drift | Select supported Python and database versions and make all pipelines install and test the same project baseline. |

### 12.4 P2 improvement risks

- large view modules and commented legacy code;
- inconsistent specialist templates and CSS overrides;
- incomplete centralized observability;
- no documented public API strategy if external integrations are later required;
- incomplete browser/device evidence;
- limited quantitative performance baselines.

### 12.5 Security review questions for every route

For each view, export, file, and API-like endpoint, reviewers should answer:

1. Is authentication required?
2. Which roles are allowed?
3. Does the current user own, teach, administer, or enroll in the requested object?
4. Can a URL/form identifier be changed to access another user's data?
5. Is the action state-changing, and if so, is it POST-only with CSRF protection?
6. Are all submitted relationships revalidated server-side?
7. Can uploaded or rendered content execute active code?
8. Does the response reveal personal, academic, or credential data?
9. Is the event auditable without logging secrets?
10. What happens when the related record, academic period, or file is missing?

---

## 13. Installation, configuration, and deployment

### 13.1 Local Windows setup

From the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The default local development address is typically:

```text
http://127.0.0.1:8000/
```

Before starting, edit `.env` with development-only values. Never reuse development secrets in production.

### 13.2 Docker development

```powershell
docker compose up --build
```

The development Compose configuration exposes the application on port `9000` and uses PostgreSQL 15 with persistent volumes.

```text
http://127.0.0.1:9000/
```

### 13.3 Production-style Docker

```powershell
docker compose -f docker-compose.prod.yml up --build -d
```

The production-style container uses a non-root user, Gunicorn, and port `8000`. This configuration is a starting point, not a complete production platform. TLS termination, secrets management, database hosting, object/media storage, backups, monitoring, health checks, and rollback must still be designed for the target environment.

### 13.4 Configuration variables

The example environment file includes the main variables below. Values must be supplied per environment and must not be pasted into team documents, issues, or chat.

| Variable group | Purpose |
|---|---|
| `SECRET_KEY` | Cryptographic signing secret; must be strong and production-specific. |
| `DEBUG` | Must be false in production. |
| `ALLOWED_HOSTS` | Explicit production hostnames. |
| `CSRF_TRUSTED_ORIGINS` | Trusted HTTPS origins for CSRF validation. |
| `EMAIL_BACKEND` | SMTP, console, file, or in-memory email behavior. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS` | Mail server connection. |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | Mail credentials and sender identity. |
| `SESSION_COOKIE_AGE` | Authenticated session lifetime. |
| `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` | HTTPS-only cookie behavior. |
| `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` | HTTPS and HSTS deployment controls. |

Settings also contain institution name, student/lecturer identifier prefixes, and dormant Stripe key references. Payment keys should not be configured until a real payment design exists.

### 13.5 Pre-commit verification commands

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py check --deploy
```

The deployment check is expected to warn in a deliberately local environment if production-only secret/TLS settings are not active. It must pass against the actual production configuration before release.

### 13.6 Continuous integration status

The repository contains GitHub, Jenkins, and Bitbucket pipeline definitions that check/test/build portions of the application. These should be consolidated or clearly assigned by environment.

Known issues include:

- GitHub tests reference Python 3.8 and 3.9;
- Docker uses Python 3.10;
- the reviewed local environment uses Python 3.11;
- one lint workflow installs `pylint` without clearly installing all project dependencies, so Django imports may fail;
- deployment sections are placeholders rather than an approved production release path.

### 13.7 Production deployment requirements

A production plan must specify:

- supported Python, Django, PostgreSQL, and browser versions;
- managed PostgreSQL or an equivalent backed-up database service;
- static and media storage, including private-resource access;
- TLS certificate and proxy/load-balancer configuration;
- secret storage and rotation;
- database migration ordering and rollback constraints;
- application health/readiness checks;
- centralized logs, error tracking, metrics, and alerts;
- background job infrastructure if email/reporting becomes asynchronous;
- image registry and immutable release versioning;
- staging validation and production approval;
- smoke test and rollback commands;
- backup and restore ownership.

---

## 14. Known limitations and documentation drift

### 14.1 Product limitations

- Payment processing is not operational.
- Parent and department-head journeys are incomplete.
- Course registration timing is not represented by a dedicated calendar/window model.
- Localization configuration is broader than actual translated content.
- Email delivery is not durable.
- Upload protection is insufficient for untrusted production users.
- Audit history is selective rather than comprehensive.
- Production monitoring, backup, and disaster recovery are not implemented.
- No formal browser, accessibility, security, or load-test report exists.
- Some complex forms still use the older UI pattern.

### 14.2 Documentation inconsistencies

The project documentation is not fully aligned with the code:

- the README's Docker development port is `9000`, while the setup guide references `8000` for a similar journey;
- some README statements overstate payment, parent, and department-head functionality;
- the TODO material describes the dashboard as static even though current dashboard metrics are substantially live;
- the setup guide references `README.DOCKER.md` and `README.CI_CD.md`, but those files are not present;
- Python version expectations differ across documentation, CI, Docker, and the reviewed local environment.

Until documentation is reconciled, this handout should be treated as the more conservative status baseline. Code and passing tests remain the final authority for actual behavior.

### 14.3 Local data warning

The local `db.sqlite3` and media directory may contain demonstration accounts, contact details, images, grades, quiz activity, or generated credentials. Do not distribute these files to group members, public repositories, presentations, or hosting providers without data-owner approval and sanitization.

---

## 15. Recommended delivery roadmap

### Phase 1 — Stabilization and security baseline

**Goal:** Produce one clean, reviewable build whose current functionality can be demonstrated safely.

1. Create a stabilization branch and inventory all 72 pre-handout changed paths, plus this handout as the additional documentation artifact.
2. Separate landing/UI work, form improvements, backend/security fixes, tests, migrations, and documentation into coherent commits.
3. Protect or remove public student creation unless it is an approved requirement.
4. Fix lecturer course authorization for result-sheet PDFs and test all sensitive identifier routes.
5. Normalize quiz test discovery and add the missing regression cases.
6. Resolve production secret, hosts, origins, TLS-cookie, and environment configuration.
7. Reconcile README/setup/TODO claims and ports.
8. Run structured responsive, keyboard, accessibility, and browser reviews of the core journeys.
9. Define and test database/media backups and restore.
10. Tag a stabilization release candidate only after the working tree is clean and CI is reproducible.

**Exit criteria:** Clean versioned source, all intended tests discovered and green, no open P0 risk, accurate documentation, and a demonstrated backup restore.

### Phase 2 — Product completion and workflow depth

**Goal:** Turn partial features and operational caveats into explicit product behavior.

1. Introduce an academic calendar with registration open/close and withdrawal rules.
2. Replace temporary-password email with secure activation and durable delivery.
3. Add login throttling and privileged-user security controls.
4. Improve quiz authoring, attempt-resume policy, manual-grade status, and reporting.
5. Add grade finalization, amendment reasons, and before/after audit history.
6. Complete and standardize PDF/report branding and exports.
7. Decide whether parent and department-head roles are in scope; build only from written permissions and journeys.
8. Make a formal payment go/no-go decision. If “go,” plan it as a separate audited integration.
9. Finish translation catalogs only for languages the group can maintain.

**Exit criteria:** Approved product scope, complete core workflows, traceable grades and enrollment changes, and no misleading placeholder capability.

### Phase 3 — Production operations and institutional pilot

**Goal:** Operate SkyLearn safely with real users and recoverable data.

1. Provision production-like PostgreSQL, storage, cache/session, TLS, secrets, and registry.
2. Add structured logs, error monitoring, service metrics, alerts, and audit reporting.
3. Establish deployment, migration, smoke, rollback, incident, and support runbooks.
4. Add browser E2E, accessibility, load, security, and restore testing to release gates.
5. Rehearse deployment and rollback in staging with a production-like dataset.
6. Complete privacy, retention, user-support, training, and administrative procedures.
7. Conduct user acceptance testing with administrators, lecturers, and students.
8. Obtain named product, security, operational, and institutional signoff.

**Exit criteria:** Measured service objectives, verified recovery, monitored production environment, trained owners, completed UAT, and an approved rollback path.

---

## 16. Release readiness checklist

### Source and change control

- [ ] All intended files, migrations, assets, and tests are tracked.
- [ ] The working tree is clean.
- [ ] Changes are split into reviewable commits.
- [ ] A peer has reviewed authorization, migrations, and grading changes.
- [ ] Release notes identify features, fixes, configuration changes, and known limitations.
- [ ] The release is tagged with an immutable version.

### Functional verification

- [ ] `python manage.py check` passes.
- [ ] `python manage.py makemigrations --check --dry-run` reports no pending changes.
- [ ] All intended tests are discovered and pass.
- [ ] Core browser journeys pass against the release build.
- [ ] PDFs and downloads show correct institution branding and authorized data.
- [ ] No screen uses placeholder metrics or claims unfinished functionality.

### Security and privacy

- [ ] Public registration and search policies are approved and enforced.
- [ ] All sensitive object routes have ownership/allocation/enrollment tests.
- [ ] Strong production secrets and approved hosts/origins are configured.
- [ ] HTTPS, cookie, CSRF, HSTS, and proxy settings are verified in the target environment.
- [ ] Upload type, size, content, storage, and download controls are implemented.
- [ ] Temporary passwords are not sent or logged in plaintext.
- [ ] Privileged authentication throttling/lockout is enabled.
- [ ] Dependency, container, and secret scans have no unaccepted high-severity findings.
- [ ] PII retention, access, correction, deletion, and breach procedures are documented.
- [ ] Audit records cover account, allocation, enrollment, score, result, and configuration changes.

### UX and accessibility

- [ ] Chrome, Edge, Firefox, Safari, Android-width, and iOS-width checks are recorded.
- [ ] Core workflows are keyboard-completable.
- [ ] Automated accessibility checks have no unaccepted serious findings.
- [ ] Focus, contrast, zoom/reflow, errors, empty states, and reduced motion are verified.
- [ ] Legacy specialist forms meet the current design system or have documented follow-up.

### Operations and recovery

- [ ] PostgreSQL, static/media storage, and environment ownership are defined.
- [ ] Database and media backups are encrypted, monitored, and retained off-primary.
- [ ] A restore has been successfully rehearsed.
- [ ] Health checks, centralized logs, error tracking, metrics, and alerts are active.
- [ ] Deployment, migrations, smoke testing, and rollback are documented and rehearsed.
- [ ] Support, incident, and on-call contacts are named.
- [ ] Production email delivery and retry are observable.

### Approval

- [ ] Product owner confirms the delivered scope and known exclusions.
- [ ] Technical reviewer confirms tests, migrations, and architecture.
- [ ] Security/privacy reviewer accepts residual risk.
- [ ] Operations owner accepts deployment and recovery responsibility.
- [ ] Institutional representatives complete user acceptance testing.

---

## 17. Project metrics and local demo snapshot

### 17.1 Repository size indicators

These figures help the group understand the current maintenance surface. They are approximate and exclude third-party/vendor and migration noise where noted.

| Indicator | Approximate count |
|---|---:|
| URL `path(...)` declarations across application URL files | 97 |
| Concrete model classes | 21 |
| Project migration files | 22 |
| HTML templates | 91 |
| Project CSS files | 2 |
| Project JavaScript files | 3 |
| Non-vendor, non-migration Python lines | 8,171 |
| HTML lines | 8,300 |
| CSS lines | 3,034 |
| JavaScript lines | 224 |

### 17.2 Local demonstration database

The following counts describe only the reviewed local database. They are not production usage figures and should not be used as business KPIs.

| Record type | Local count |
|---|---:|
| Users | 319 |
| Students | 206 |
| Programs | 276 |
| Courses | 56 |
| Academic sessions | 24 |
| Semesters | 5 |
| News/event posts | 40 |
| Lecturer allocations | 12 |
| Course packages | 0 |
| Uploaded files | 15 |
| Uploaded videos | 1 |
| Quizzes | 4 |
| Quiz sittings | 3 |
| Course enrollments (`TakenCourse`) | 4 |
| Period result records | 0 |

These counts reveal two useful test-data gaps: course packages have no local examples, and period result records have no local examples despite result functionality. Acceptance testing should seed representative records rather than depend on the existing database.

### 17.3 Route-family map

| Route family | Main responsibility |
|---|---|
| Root / core | Landing, home/dashboard, news/events, sessions, semesters, supporting actions |
| `/accounts/...` | Login-related account journeys, students, lecturers, profiles, passwords, role records |
| `/programs/...` and course routes | Programs, courses, allocations, enrollments, packages, registration, resources |
| `/quiz/...` | Quiz settings, questions, attempts, sittings, marking, analysis |
| `/results/...` | Score entry, result views, grade reports, PDFs |
| Search route | Cross-module content lookup |
| Payment route area | Placeholder only; no operational flow |

---

## 18. Team working agreement and ownership

### 18.1 Recommended ownership areas

One person may hold more than one area in a small team, but each area should have a named owner.

| Area | Owner responsibility |
|---|---|
| Product/scope | Confirms target institution, roles, grading rules, registration rules, and excluded features. |
| Backend/domain | Owns Django models, services, transactions, migrations, and domain tests. |
| Security/privacy | Reviews access control, uploads, credentials, secrets, audit, and data governance. |
| Frontend/UX | Owns design system, forms, responsive behavior, accessibility, and browser QA. |
| QA | Maintains test plan, discovery, regression suite, E2E coverage, and release evidence. |
| DevOps/operations | Owns CI, containers, environments, deploy/rollback, monitoring, backup, and restore. |
| Documentation/training | Keeps README, setup, handout, release notes, and user instructions aligned with the build. |

### 18.2 Change workflow

1. Start from an approved issue or requirement with acceptance criteria.
2. Create a focused branch.
3. Add or update tests with the behavior.
4. Run local checks and inspect migrations.
5. Review security and privacy impact for user-controlled identifiers or personal data.
6. Open a reviewable pull request with screenshots for UI changes and commands/results for backend changes.
7. Obtain at least one peer review; require domain/security review for grades, accounts, permissions, and payments.
8. Merge only when CI passes and documentation is accurate.
9. Promote an immutable version through staging and release approval.

### 18.3 Demonstration script for group presentations

For a reliable presentation, use a seeded, sanitized environment and follow this order:

1. Show the public landing page and explain the product scope.
2. Log in as an administrator and show live dashboard information.
3. Create or open a student, program, course, and lecturer allocation.
4. Demonstrate a guided form and its validation feedback.
5. Log in as a lecturer and open an allocated course.
6. Show a resource, quiz, and score-entry flow.
7. Log in as a student and show course access, quiz participation, and results.
8. End with the roadmap and be explicit that payments, parent, and department-head portals are not complete.

Do not demonstrate with real personal information or distribute the local database.

---

## 19. Glossary

| Term | Meaning in SkyLearn |
|---|---|
| Academic session | A broader academic period, commonly an academic year. |
| Semester | A subdivision of an academic session used for course/result context. |
| Program | A student's academic program or course of study. |
| Course | A teachable academic unit associated with a program and metadata such as level or credit. |
| Course allocation | The relationship that authorizes a lecturer to manage a course. |
| Enrollment / `TakenCourse` | The relationship connecting a student to a course, also storing score components and derived grade data. |
| Course package | A predefined set of courses targeted at a program, level, and year cohort. |
| Quiz | An assessment attached to a course. |
| Sitting | One student's quiz attempt and its state. |
| GPA | Grade point average for an applicable academic period. |
| CGPA | Cumulative grade point average across applicable periods. |
| RBAC | Role-based access control. It restricts functions by role, such as administrator, lecturer, or student. |
| Object-level authorization | A check that the current user may access the specific requested student, course, quiz, result, or file—not merely that the user has a broad role. |
| PII | Personally identifiable information such as names, email addresses, phone numbers, and profile information. |
| RPO | Recovery point objective: the maximum acceptable amount of data loss measured in time. |
| RTO | Recovery time objective: the maximum acceptable service restoration time. |
| UAT | User acceptance testing by representative real users or institutional stakeholders. |

---

## 20. Evidence used for this handout

This handout was prepared from direct inspection and verification of the repository rather than feature claims alone. Evidence included:

- Django settings, root and application URL files;
- models, forms, views, decorators, signals, and migrations in `accounts`, `core`, `course`, `quiz`, `result`, `search`, and `payment`;
- templates and project-owned CSS/JavaScript assets;
- automated tests and their discovery behavior;
- Docker, Compose, CI, requirements, example environment, and setup files;
- Git branch, revision, and working-tree status;
- local Django checks, migration drift check, test run, template compilation, JavaScript syntax checks, deployment check, and HTTP asset smoke checks;
- aggregate local demonstration database counts, without including or publishing record-level personal data.

### Final project position

SkyLearn already has enough working depth to demonstrate a credible learning management system. The strongest next move is to protect that progress: turn the current local snapshot into a clean reviewed release candidate, close the authorization and onboarding policy gaps, make operations recoverable, and prove the main journeys across real browsers and roles. Once that foundation is stable, the team can confidently expand incomplete areas without increasing hidden risk.

---

**End of handout**
