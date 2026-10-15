"""Tech keywords that ATS filters and recruiters scan for, and how well a resume covers a job's set.

Used by fetch_remote.py (rank leads by how many of a job's keywords the candidate really has) and tailor.py
(report which of the job's keywords the tailored resume shows, which true ones it still misses, and the gaps).
"""
import re

# canonical name -> regex. Order does not matter; matching is case-insensitive on plain text.
VOCAB = {
    "JavaScript": r"\bjavascript\b|\bjs\b|es6", "TypeScript": r"typescript|\bts\b", "Node.js": r"node\.?js|\bnode\b",
    "React": r"\breact(\.?js)?\b(?! native)", "React Native": r"react native", "Next.js": r"next\.?js",
    "Vue": r"\bvue", "Angular": r"angular", "Svelte": r"svelte", "Remix": r"\bremix\b", "Astro": r"\bastro\b",
    "Redux": r"redux", "Zustand": r"zustand", "TanStack Query": r"tanstack|react query",
    "Tailwind CSS": r"tailwind", "Styled Components": r"styled.components", "Storybook": r"storybook",
    "HTML": r"\bhtml5?\b", "CSS": r"\bcss3?\b", "Design systems": r"design system|component librar",
    "Accessibility": r"accessibility|\ba11y\b|wcag", "Responsive design": r"responsive",
    "SSR": r"\bssr\b|server[- ]side render", "SEO": r"\bseo\b", "Web performance": r"web performance|core web vitals|performance optimi[sz]",
    "Express.js": r"express(\.js)?\b", "NestJS": r"nest\.?js", "Fastify": r"fastify", "Deno": r"\bdeno\b", "Bun": r"\bbun\b",
    "REST APIs": r"\brest(ful)?\b", "GraphQL": r"graphql", "gRPC": r"grpc", "WebSockets": r"websocket",
    "tRPC": r"trpc", "Microservices": r"microservice", "Event-driven architecture": r"event[- ]driven",
    "System design": r"system design|distributed system|scalab",
    "Python": r"\bpython\b", "Rust": r"\brust\b", "Java": r"\bjava\b", "Ruby": r"\bruby\b|rails", "PHP": r"\bphp\b",
    "Elixir": r"elixir", "C#": r"c#|\.net", "Kotlin": r"kotlin", "Swift": r"\bswift\b",
    "PostgreSQL": r"postgres", "MySQL": r"mysql", "MongoDB": r"mongo", "Redis": r"redis", "SQL": r"\bsql\b",
    "Prisma": r"prisma", "Drizzle": r"drizzle", "Supabase": r"supabase", "Firebase": r"firebase",
    "Elasticsearch": r"elasticsearch|opensearch", "ClickHouse": r"clickhouse", "DynamoDB": r"dynamodb",
    "Kafka": r"kafka", "RabbitMQ": r"rabbitmq", "AWS SQS": r"\bsqs\b", "Queues": r"\bqueue",
    "Temporal": r"\btemporal\b", "AWS": r"\baws\b|amazon web services", "GCP": r"\bgcp\b|google cloud",
    "Azure": r"\bazure\b", "Docker": r"docker|container", "Kubernetes": r"kubernetes|\bk8s\b",
    "Terraform": r"terraform", "Serverless": r"serverless|lambda", "Vercel": r"vercel", "Cloudflare": r"cloudflare",
    "CI/CD": r"ci/cd|continuous (integration|deploy)", "GitHub Actions": r"github actions",
    "Testing": r"\btest(s|ing)\b|tdd", "Jest": r"\bjest\b", "Playwright": r"playwright", "Cypress": r"cypress",
    "Observability": r"observability|monitoring|datadog|sentry|grafana", "Auth": r"\bauth(entication|orization)?\b|oauth|\bjwt\b|\bsso\b",
    "Payments": r"stripe|payment", "AI features": r"\bai\b|\bllm|openai|anthropic|machine learning|\bml\b",
    "RAG": r"\brag\b|retrieval", "Vector DB": r"vector (db|database|search)|pgvector|pinecone",
    "Web3": r"web3|blockchain|crypto|ethereum|solana", "Solidity": r"solidity",
    "Agile": r"agile|scrum|sprint", "Code review": r"code review", "Documentation": r"documentation|technical writing|written communication",
    "Mentoring": r"mentor", "Remote/async": r"\basync(hronous)?\b(?! ?/ ?await)|remote[- ]first|distributed team",
    "Product mindset": r"product[- ](minded|mindset|engineer|sense)|ownership|end[- ]to[- ]end",
    "Startup": r"startup|early[- ]stage|seed|series [ab]", "SaaS": r"\bsaas\b", "B2B": r"\bb2b\b",
    "Mobile": r"\bios\b|android|mobile app", "Figma": r"figma",
}
_COMPILED = {k: re.compile(v, re.I) for k, v in VOCAB.items()}
# Go is matched case-sensitively, and not as a verb ("go over", "go live").
_COMPILED["Go"] = re.compile(r"[Gg]olang|(?<=[ ,(/])Go(?=[ ,)/.]|$)(?! (ahead|through|over|to|live|beyond|back|further|deeper))")

# Soft or context keywords that say little about fit; reported but not counted in the match score.
SOFT = {"Remote/async", "Product mindset", "Startup", "SaaS", "B2B", "Agile", "Documentation", "Code review",
        "Mentoring", "Responsive design", "Testing", "Queues", "SQL"}


def extract(text):
    """Canonical keywords present in the text."""
    return {k for k, rx in _COMPILED.items() if rx.search(text or "")}


def coverage(job_text, have_text):
    """Split the job's hard keywords into ones the candidate has (per have_text) and gaps; return (pct, have, gaps)."""
    job = extract(job_text) - SOFT
    have = job & extract(have_text)
    gaps = job - have
    pct = round(100 * len(have) / len(job)) if job else 0
    return pct, sorted(have), sorted(gaps)
