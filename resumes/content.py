"""Resume content for every role-targeted version.

Facts come from the original resume and the live product sites. Each version changes the headline,
summary, skill order and which bullets lead; the history itself is shared.
"""
import os

CONTACT = {
    "name": "Prabhanjan Sharma",
    "email": "mprabhanjan18@gmail.com",
    # Kept out of the public repo: set RESUME_PHONE when building copies to send.
    "phone": os.environ.get("RESUME_PHONE", ""),
    "linkedin": "https://www.linkedin.com/in/prabhanjan-sharma-38a48a221/",
    "linkedin_label": "linkedin.com/in/prabhanjan-sharma-38a48a221",
    "github": "https://github.com/prab002",
    "github_label": "github.com/prab002",
}

LOC_BLR = "Bengaluru, India"
LOC_REMOTE = "Bengaluru, India (IST, UTC+5:30) | Open to remote, flexible hours for EU and US overlap"

EDUCATION = ("B.Tech, Computer Science (Artificial Intelligence)", "ITM SLS Baroda University, Vadodara", "2020 – 2024")

WEBKNOT = ("Webknot Technologies", "Bengaluru", "Senior Software Developer", "Oct 2025 – Present")
INV = ("Invennico TechnoLabs", "Vadodara", "Jun 2024 – Sep 2025")
INV_LEAD = ("Software Developer Team Lead", "Apr 2025 – Sep 2025")
INV_JR = ("Junior Software Developer (MERN)", "Jun 2024 – Mar 2025")
ADRIXUS = ("Adrixus Tech Studio", "Vadodara", "Software Developer Intern (MERN)", "Dec 2023 – Jun 2024")

# Products built and launched independently. Descriptions come from each site's
# own indexed pages; SoundCraft had none indexed, so it carries no description yet.
PROJECTS = [
    {
        "name": "Traders Zone",
        "url": "https://traders-zone.in/",
        "label": "traders-zone.in",
        "desc": (
            "AI trading journal for crypto traders. Users upload their trades; it checks 12 trading habits against "
            "that history and reports win rate, sample size and money made or lost per habit. Chat with your own "
            "record in English, Hindi or Hinglish. Covers 1,529 Binance spot and perpetual markets without ever "
            "asking for exchange API keys. Free, Pro and Max plans."
        ),
    },
    {
        "name": "Free Mac",
        "url": "https://free-mac.online/",
        "label": "free-mac.online",
        "desc": (
            "Mac disk cleaner that maps the whole drive, shows what is using space and clears it. Runs on "
            "macOS 10.15+ on Apple Silicon and Intel; 11.4 MB download, no account needed. Free scan, with a paid "
            "licence key that unlocks cleaning."
        ),
    },
    {
        "name": "AI Skill Up",
        "url": "https://aiskillup.online/",
        "label": "aiskillup.online",
        "desc": "AI skills learning site with paid access delivered through licence keys, plus a technical blog.",
    },
    {
        "name": "SoundCraft",
        "url": "https://soundcraft.online/",
        "label": "soundcraft.online",
        "desc": "",
    },
]

PROJECTS_SENTENCE = "I have also built and launched four products on my own, including the paid apps Traders Zone and Free Mac."

# Versions where the projects sit right under the summary; the rest list them after experience.
PROJECTS_FIRST = {"tech-lead", "senior-full-stack-engineer-remote", "senior-frontend-engineer-nextjs", "founding-engineer"}

VERSIONS = [
    {
        "slug": "associate-engineering-manager",
        "role": "Associate Engineering Manager",
        "headline": "Associate Engineering Manager | Full Stack Tech Lead (Next.js, Node.js)",
        "location": LOC_BLR,
        "summary": (
            "Engineer with close to 3 years of experience building web products, including a team lead role at "
            "Invennico and mentoring developers at Webknot. I run sprints, set code review and coding standards, "
            "and act as the technical contact for clients. Still hands-on in Next.js, Node.js and AWS; most recently "
            "redesigned a backend that now responds about 70% faster."
        ),
        "skills": [
            ("Team leadership", "Sprint planning, stand-ups, retrospectives, code review process, coding standards, mentoring, onboarding documentation"),
            ("Delivery", "Full SDLC ownership, requirement gathering, client and stakeholder communication, Agile/Scrum, progress reporting"),
            ("Architecture", "Microservices, event-driven systems, REST, GraphQL, Apache Kafka, RabbitMQ, AWS SQS, Redis"),
            ("Stack", "Next.js, React, JavaScript, Node.js, Express.js, Go, PostgreSQL, MySQL, MongoDB, AWS, Docker, GitHub Actions, Vercel"),
        ],
        "webknot": [
            "Mentor junior developers through code reviews and pairing, and maintain the coding standards and technical docs the team works from.",
            "Redesigned the backend architecture of a client product, cutting API response time by about 70% while keeping near-zero downtime.",
            "Work with the AI/ML team to plan and ship AI features into our backend, coordinating scope and timelines across both teams.",
            "Gather requirements from clients and internal stakeholders and turn them into technical plans and sprint tasks.",
            "Keep releases on schedule within Agile sprints through estimates, sprint commitments and regular status updates.",
        ],
        "lead": [
            "Led the development team through the full SDLC, from planning and architecture to deployment and post-launch support.",
            "Ran daily stand-ups, sprint planning and retrospectives, which raised team velocity and kept releases production-ready.",
            "Set up CI/CD pipelines with automated deployments and made code review mandatory for every change.",
            "Was the main technical contact for clients: gathered requirements, proposed solutions and sent regular progress updates.",
        ],
        "junior": [
            "Built a responsive web application with Next.js and the MERN stack, from API design to UI.",
            "Added server-side rendering in Next.js to improve page speed and SEO, which lifted user retention.",
            "Worked with designers and the product team to match features to business goals and ship on time.",
        ],
        "intern": [
            "Built reusable React components with Styled Components and documented them in Storybook for the team.",
            "Wrote REST APIs with Node.js, Express.js and MongoDB and connected them to frontend modules.",
        ],
        "achievements": [
            "1st place, Codeathon programming competition",
            "Wrote the internal workflow and best-practice docs used to onboard new developers",
            "Write technical articles on Medium about Next.js, API design, performance and system design",
        ],
        "keywords": "Associate Engineering Manager, Engineering Lead, Team Lead, Tech Lead, Full Stack, Next.js, React, Node.js, Agile, Scrum, Mentoring, Stakeholder Management, SDLC, CI/CD, Microservices, AWS, Bengaluru",
    },
    {
        "slug": "sde-2-senior-software-engineer",
        "role": "Senior Software Engineer (SDE-2)",
        "headline": "Senior Software Engineer (SDE-2) | Full Stack | Next.js, Node.js, Microservices",
        "location": LOC_BLR,
        "summary": (
            "Full-stack engineer with close to 3 years of experience building web products in Next.js, React and "
            "Node.js. At Webknot I redesigned a backend that now responds about 70% faster and integrate AI features "
            "built by the ML team. Previously led a development team at Invennico, where I owned architecture, CI/CD "
            "and code reviews."
        ),
        "skills": [
            ("Languages", "JavaScript (ES6+), Go, SQL, HTML5, CSS3"),
            ("Frontend", "React, Next.js (SSR, SSG), Redux, Zustand, TanStack Query, Tailwind CSS, Styled Components, Storybook"),
            ("Backend", "Node.js, Express.js, REST APIs, GraphQL, Firebase, JWT authentication"),
            ("Data and messaging", "PostgreSQL, MySQL, MongoDB, Redis, Apache Kafka, RabbitMQ, AWS SQS"),
            ("Cloud and DevOps", "AWS (S3), Docker, GitHub Actions, Vercel, CI/CD"),
            ("Design", "Microservices, event-driven architecture, system design, performance tuning, SEO"),
        ],
        "webknot": [
            "Redesigned the backend architecture of a client product; API response time dropped by about 70% and the service stayed at near-zero downtime.",
            "Integrated AI-driven features from the ML team into our backend services.",
            "Rebuilt large parts of the frontend so core user flows are simpler and faster to use.",
            "Review code for the team, maintain technical documentation and mentor junior developers.",
            "Turn client requirements into technical designs and deliver them in Agile sprints.",
        ],
        "lead": [
            "Designed the system architecture for client projects and owned them from planning to deployment and post-launch support.",
            "Built CI/CD pipelines with automated deployments, which removed manual release steps.",
            "Led the team's stand-ups, sprint planning and retrospectives, and set up the code review process.",
            "Worked directly with clients on requirements, technical proposals and progress updates.",
        ],
        "junior": [
            "Built a responsive web application with Next.js, React, Node.js, Express.js and MongoDB.",
            "Implemented server-side rendering in Next.js to improve load time and SEO, which lifted user retention.",
            "Designed REST APIs and MongoDB data models; used JWT for authentication and AWS S3 for file storage.",
            "Kept the codebase clean through regular code reviews and shared conventions.",
        ],
        "intern": [
            "Built reusable, responsive React components with Styled Components and documented them in Storybook.",
            "Wrote REST APIs with Node.js, Express.js and MongoDB and wired them into frontend features.",
        ],
        "achievements": [
            "1st place, Codeathon programming competition",
            "Technical writer on Medium: articles on Next.js, API design, SSR and SEO, and system design",
        ],
        "keywords": "SDE 2, SDE-2, Senior Software Engineer, Full Stack Developer, MERN, Next.js, React, Node.js, Express.js, Microservices, Kafka, Redis, PostgreSQL, MongoDB, System Design, AWS, Bengaluru",
    },
    {
        "slug": "tech-lead",
        "role": "Tech Lead",
        "headline": "Tech Lead | Full Stack (Next.js, Node.js) | Architecture, CI/CD, Team Delivery",
        "location": LOC_BLR + " | Open to remote",
        "summary": (
            "Full-stack engineer who leads small teams and still ships a lot of the code. As team lead at Invennico "
            "I owned architecture, CI/CD, sprints and client calls end to end. At Webknot I redesigned a backend that "
            "now responds about 70% faster, integrate AI features with the ML team, and mentor junior developers. "
            "Close to 3 years of experience with Next.js, Node.js and AWS."
        ),
        "skills": [
            ("Architecture", "System design, microservices, event-driven architecture, REST, GraphQL, Apache Kafka, RabbitMQ, AWS SQS, Redis"),
            ("Engineering", "Next.js, React, JavaScript, Node.js, Express.js, Go, PostgreSQL, MySQL, MongoDB"),
            ("Delivery", "CI/CD, GitHub Actions, Docker, AWS, Vercel, code review, Agile/Scrum, technical documentation"),
            ("Leadership", "Mentoring, sprint planning, requirement gathering, client communication"),
        ],
        "webknot": [
            "Redesigned the backend architecture of a client product, cutting API response time by about 70% with near-zero downtime.",
            "Plan and ship AI features with the AI/ML team, owning how they fit into our backend systems.",
            "Mentor junior developers and run code reviews against the coding standards I maintain.",
            "Work directly with clients and internal stakeholders to turn requirements into technical designs.",
            "Rebuilt major parts of the UI to make core user flows simpler and faster.",
        ],
        "lead": [
            "Owned architecture and delivery for client projects across the full SDLC, from planning to post-launch support.",
            "Set up CI/CD pipelines and automated deployments, and made code review part of every change.",
            "Ran stand-ups, sprint planning and retrospectives; team velocity improved and releases went out production-ready.",
            "Acted as the technical point of contact for clients, with proposals and regular progress updates.",
        ],
        "junior": [
            "Built a responsive web application on Next.js and the MERN stack, frontend to database.",
            "Implemented server-side rendering in Next.js for faster pages and better SEO, which lifted user retention.",
            "Designed REST APIs and backend services with Node.js, Express.js and MongoDB.",
        ],
        "intern": [
            "Built a reusable React component set with Styled Components, documented in Storybook.",
            "Wrote REST APIs with Node.js, Express.js and MongoDB for frontend features.",
        ],
        "achievements": [
            "1st place, Codeathon programming competition",
            "Wrote the team's workflow and best-practice docs, used for onboarding new developers",
            "Technical writer on Medium: Next.js, API design and system design",
        ],
        "keywords": "Tech Lead, Technical Lead, Lead Engineer, Full Stack, Next.js, React, Node.js, System Design, Architecture, Microservices, CI/CD, GitHub Actions, Docker, AWS, Agile, Mentoring, Startup",
    },
    {
        "slug": "senior-full-stack-engineer-remote",
        "role": "Senior Full Stack Engineer",
        "headline": "Senior Full Stack Engineer | Next.js, React, Node.js | Remote",
        "location": LOC_REMOTE,
        "summary": (
            "Full-stack engineer with close to 3 years of experience shipping Next.js and Node.js products for "
            "clients. I redesigned a backend that now responds about 70% faster, integrate AI features with ML teams, "
            "and have led a development team through full release cycles. Used to working through written specs, "
            "documentation and regular client updates."
        ),
        "skills": [
            ("Frontend", "React, Next.js (SSR, SSG), JavaScript (ES6+), Redux, Zustand, TanStack Query, Tailwind CSS, Styled Components, Storybook"),
            ("Backend", "Node.js, Express.js, Go, REST APIs, GraphQL, Firebase, JWT authentication"),
            ("Data and messaging", "PostgreSQL, MySQL, MongoDB, Redis, Apache Kafka, RabbitMQ, AWS SQS"),
            ("Infrastructure", "AWS, Docker, GitHub Actions, Vercel, CI/CD"),
            ("Ways of working", "Async written communication, technical documentation, code review, Agile/Scrum"),
        ],
        "webknot": [
            "Redesigned the backend architecture of a client product; API response time fell by about 70% with near-zero downtime.",
            "Integrated AI-driven features from the ML team into our backend services.",
            "Rebuilt large parts of the UI so core user flows are simpler and faster to use.",
            "Write and maintain technical documentation, review code and mentor junior developers.",
            "Work with clients and internal stakeholders to turn requirements into technical designs.",
        ],
        "lead": [
            "Designed system architecture for client projects and owned the full SDLC through post-launch support.",
            "Built CI/CD pipelines with automated deployments and a code review step for every change.",
            "Ran sprint planning, stand-ups and retrospectives for the team.",
            "Kept clients informed through requirement sessions, solution proposals and progress updates.",
        ],
        "junior": [
            "Built a responsive web application with Next.js, React, Node.js, Express.js and MongoDB.",
            "Added server-side rendering in Next.js to speed up pages and improve SEO, which lifted user retention.",
            "Designed REST APIs and data models; used JWT for authentication and AWS S3 for file storage.",
        ],
        "intern": [
            "Built reusable React components with Styled Components and documented them in Storybook.",
            "Wrote REST APIs with Node.js, Express.js and MongoDB for frontend features.",
        ],
        "achievements": [
            "1st place, Codeathon programming competition",
            "Technical writer on Medium: Next.js, API design, SSR and SEO, system design",
        ],
        "keywords": "Senior Full Stack Engineer, Full Stack Developer, Remote, Next.js, React, Node.js, JavaScript, GraphQL, REST, PostgreSQL, MongoDB, Redis, Kafka, AWS, Docker, CI/CD, Async",
    },
    {
        "slug": "senior-frontend-engineer-nextjs",
        "role": "Senior Frontend Engineer (Next.js)",
        "headline": "Senior Frontend Engineer | Next.js, React | Performance, SSR and SEO",
        "location": "Bengaluru, India (IST, UTC+5:30) | Open to remote",
        "summary": (
            "Frontend-focused engineer with close to 3 years of experience building Next.js and React applications. "
            "I have shipped server-side rendering for speed and SEO, built component libraries in Storybook, and "
            "reworked product UIs to make core flows easier to use. Enough backend experience (Node.js, REST, "
            "GraphQL) to own a feature from API to screen, and have led a small team."
        ),
        "skills": [
            ("Frontend", "Next.js (SSR, SSG), React, JavaScript (ES6+), HTML5, CSS3"),
            ("State and data", "Redux, Zustand, TanStack Query, REST APIs, GraphQL"),
            ("Styling and UI", "Tailwind CSS, Styled Components, Storybook, responsive design, component libraries"),
            ("Quality", "Performance optimization, SEO best practices, code review, documentation"),
            ("Backend and tools", "Node.js, Express.js, Firebase, MongoDB, PostgreSQL, AWS, Vercel, Docker, GitHub Actions"),
        ],
        "webknot": [
            "Reworked the application's UI and UX, simplifying core user flows and making the product noticeably easier to use.",
            "Redesigned the backend the frontend depends on, cutting API response time by about 70% with near-zero downtime.",
            "Brought AI-driven features from the ML team into the product.",
            "Review frontend code, maintain coding standards and mentor junior developers.",
        ],
        "lead": [
            "Led the development team on client projects, owning architecture and delivery from planning to post-launch support.",
            "Set up CI/CD with automated deployments and a code review step for every change.",
            "Ran sprint planning, stand-ups and retrospectives, and handled client requirements and updates.",
        ],
        "junior": [
            "Built a responsive web application in Next.js and React, working closely with UI/UX designers.",
            "Implemented server-side rendering in Next.js to cut load time and improve SEO, which lifted user retention.",
            "Managed client state with Redux and Zustand, and deployed on Vercel.",
            "Built the Node.js and Express.js APIs behind the UI, with JWT authentication and AWS S3 file storage.",
        ],
        "intern": [
            "Built reusable, responsive React components with Styled Components that worked across devices.",
            "Documented the component set in Storybook, which made UI work more consistent across the team.",
            "Built data-driven UI components with the backend team.",
        ],
        "achievements": [
            "1st place, Codeathon programming competition",
            "Technical writer on Medium: Next.js, SSR and SEO, frontend performance",
        ],
        "keywords": "Senior Frontend Engineer, Frontend Developer, React Developer, Next.js, React, JavaScript, SSR, SSG, SEO, Web Performance, Redux, Zustand, TanStack Query, Tailwind CSS, Storybook, Design System",
    },
    {
        "slug": "founding-engineer",
        "role": "Founding Engineer",
        "headline": "Founding Engineer | Full Stack (Next.js, Node.js, AWS) | Idea to production",
        "location": "Bengaluru, India (IST, UTC+5:30) | Open to remote",
        "summary": (
            "Full-stack engineer who has owned products end to end: talking to clients, designing the architecture, "
            "writing frontend and backend, setting up CI/CD and supporting the product after launch. Close to 3 years "
            "across Next.js, Node.js, event-driven backends and AWS, including leading a small team and shipping AI "
            "features with an ML team. Looking to join an early-stage product company as one of its first engineers."
        ),
        "skills": [
            ("Product engineering", "Next.js (SSR, SSG), React, Node.js, Express.js, Go, REST APIs, GraphQL, Firebase"),
            ("Data and infrastructure", "PostgreSQL, MySQL, MongoDB, Redis, Apache Kafka, RabbitMQ, AWS SQS, AWS, Docker, Vercel"),
            ("Shipping", "CI/CD with GitHub Actions, automated deployments, code review, technical documentation"),
            ("Beyond code", "Requirement gathering, client communication, sprint planning, mentoring"),
        ],
        "webknot": [
            "Redesigned a client product's backend architecture, cutting API response time by about 70% with near-zero downtime.",
            "Shipped AI-driven features into production by working with the ML team on the backend side.",
            "Reworked the product's UI and UX to make core flows simpler and faster.",
            "Take requirements straight from clients and turn them into designs, tickets and releases.",
            "Mentor junior developers and keep code quality up through reviews and written standards.",
        ],
        "lead": [
            "Took client projects from the first requirements call through architecture, build, deployment and post-launch support.",
            "Set up CI/CD pipelines and automated deployments from scratch, with code review on every change.",
            "Led the team's sprints: planning, stand-ups and retrospectives.",
        ],
        "junior": [
            "Built a web application from zero with Next.js, React, Node.js, Express.js and MongoDB.",
            "Added server-side rendering in Next.js for speed and SEO, which lifted user retention.",
            "Handled authentication with JWT, file storage on AWS S3 and deployment on Vercel.",
        ],
        "intern": [
            "Built reusable React components and REST APIs with Node.js, Express.js and MongoDB, documented in Storybook.",
        ],
        "achievements": [
            "1st place, Codeathon programming competition",
            "Technical writer on Medium: Next.js, API design and system design",
        ],
        "keywords": "Founding Engineer, Founding Full Stack Engineer, Early Stage Startup, 0 to 1, Full Stack, Next.js, React, Node.js, AWS, Docker, CI/CD, Kafka, AI Features, Product Engineering, Remote",
    },
]
