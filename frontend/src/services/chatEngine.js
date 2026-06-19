// ─── Smart AI Chat Engine — answers any question ───

const KNOWLEDGE = {
  // Programming Languages
  python: "Python is a versatile, high-level language popular in AI/ML, web dev (Django, Flask, FastAPI), data science, automation, and scripting. It's the #1 language for machine learning with libraries like TensorFlow, PyTorch, and Scikit-learn. Average salary: $120K-$180K.",
  javascript: "JavaScript is the language of the web. Used for frontend (React, Vue, Angular), backend (Node.js), mobile (React Native), and even desktop (Electron). It's the most widely-used programming language globally. Average salary: $110K-$170K.",
  java: "Java is an enterprise-grade language used in Android development, banking systems, big data (Hadoop, Spark), and microservices (Spring Boot). Strong type safety and massive ecosystem. Average salary: $115K-$175K.",
  typescript: "TypeScript adds static typing to JavaScript, catching bugs at compile time. It's now the standard for large-scale React, Angular, and Node.js projects. Rapidly growing adoption in 2026.",
  rust: "Rust offers memory safety without garbage collection. Used in systems programming, WebAssembly, blockchain, and increasingly in cloud infrastructure. One of the fastest-growing languages.",
  go: "Go (Golang) is designed by Google for concurrent, scalable backend systems. Popular for microservices, cloud tools (Docker, Kubernetes are written in Go), and CLI tools.",
  cpp: "C++ is used in game engines, embedded systems, high-frequency trading, operating systems, and performance-critical applications. Foundation of many modern technologies.",

  // Frameworks & Tools
  react: "React is a JavaScript library by Meta for building user interfaces. Features: Component-based, Virtual DOM, Hooks, large ecosystem. Used by Facebook, Instagram, Netflix, Airbnb.",
  angular: "Angular is a full-featured TypeScript framework by Google. Features: Two-way binding, dependency injection, CLI tools. Best for enterprise-scale applications.",
  vue: "Vue.js is a progressive JavaScript framework. Easy learning curve, excellent documentation, flexible architecture. Used by Alibaba, GitLab, Nintendo.",
  nextjs: "Next.js is a React framework for production. Features: Server-side rendering, static generation, API routes, middleware. The most popular React meta-framework.",
  docker: "Docker containerizes applications for consistent deployment across environments. Essential DevOps tool. Used with Kubernetes for orchestration at scale.",
  kubernetes: "Kubernetes (K8s) orchestrates containerized applications at scale. Auto-scaling, self-healing, rolling updates. The industry standard for container orchestration.",
  aws: "AWS (Amazon Web Services) is the leading cloud platform with 200+ services. Key services: EC2, S3, Lambda, RDS, ECS, SageMaker. Market leader with ~32% cloud market share.",
  tensorflow: "TensorFlow is Google's open-source ML framework. Used for deep learning, computer vision, NLP, and production ML. Supports Python, JavaScript, and mobile deployment.",
  pytorch: "PyTorch is Meta's ML framework, preferred in research. Dynamic computation graphs, intuitive API. Dominant in academia and increasingly in production.",

  // Career Topics
  resume: "Resume best practices:\n• Keep 1-2 pages\n• Use ATS-friendly formatting (no tables/graphics)\n• Start with a strong summary\n• Quantify achievements (e.g., 'Increased revenue by 30%')\n• Use action verbs: Led, Developed, Architected\n• Tailor keywords to each job description\n• Include: Contact, Summary, Experience, Skills, Education\n• Proofread thoroughly",
  interview: "Interview preparation guide:\n\n📚 Technical: Practice LeetCode (medium), system design, your project architectures\n🗣️ Behavioral: STAR method, prepare stories for leadership, conflict, failure\n🔍 Research: Company mission, recent news, tech stack, interviewer background\n💡 Tips: Think aloud, ask clarifying questions, discuss trade-offs\n📝 Follow up with thank-you email within 24 hours",
  salary: "Salary negotiation strategies:\n\n1. Research market rates (Glassdoor, Levels.fyi, Payscale)\n2. Know your value based on skills and experience\n3. Always negotiate (85% of companies expect it)\n4. Aim 10-20% above initial offer\n5. Consider total compensation: base + bonus + equity + benefits\n6. Get the offer in writing before accepting\n7. Practice negotiation with a friend",
  freelancing: "Freelancing guide:\n\n🌐 Platforms: Upwork, Toptal, Fiverr, Freelancer\n💰 Rates: Start competitive, increase with reputation\n📋 Portfolio: Build 3-5 strong showcase projects\n📝 Contracts: Always use written agreements\n🏦 Finance: Set aside 25-30% for taxes\n⏰ Time management: Use Pomodoro, time tracking tools\n🤝 Networking: LinkedIn, Twitter, tech communities",
  remote: "Remote work tips:\n\n🏠 Setup: Dedicated workspace, ergonomic chair, good internet\n📅 Routine: Fixed schedule, regular breaks\n💬 Communication: Over-communicate, async-first, document everything\n🛠️ Tools: Slack, Zoom, Notion, GitHub, Linear\n🧠 Mental health: Social interactions, exercise, boundaries\n📈 Visibility: Share progress, attend virtual meetings with camera on",

  // Tech Concepts
  microservices: "Microservices architecture splits applications into small, independently deployable services. Benefits: scalability, tech flexibility, team autonomy. Challenges: complexity, data consistency, observability. Use for large-scale systems, not small projects.",
  devops: "DevOps combines development and operations for faster, reliable software delivery. Key practices: CI/CD, Infrastructure as Code, monitoring, automated testing, containerization. Tools: Jenkins, GitHub Actions, Docker, Terraform, Prometheus.",
  ml: "Machine Learning workflow:\n1. Data collection & cleaning\n2. Feature engineering\n3. Model selection (Linear, Tree, Neural Network)\n4. Training & validation\n5. Hyperparameter tuning\n6. Evaluation (accuracy, precision, recall, F1)\n7. Deployment & monitoring\n\nTypes: Supervised, Unsupervised, Reinforcement Learning",
  api: "API Design best practices:\n• RESTful conventions (GET, POST, PUT, DELETE)\n• Consistent naming (/api/v1/users)\n• Proper HTTP status codes\n• Pagination for lists\n• Authentication (JWT, OAuth 2.0)\n• Rate limiting\n• Versioning\n• Documentation (OpenAPI/Swagger)",
  database: "Database selection guide:\n• Relational (PostgreSQL, MySQL): Structured data, ACID transactions\n• Document (MongoDB): Flexible schemas, rapid development\n• Key-Value (Redis): Caching, sessions, real-time data\n• Graph (Neo4j): Relationship-heavy data\n• Time-Series (InfluxDB): IoT, metrics, logs\n• Search (Elasticsearch): Full-text search, analytics",
  security: "Application security essentials:\n• Input validation & sanitization\n• Parameterized queries (prevent SQL injection)\n• HTTPS everywhere\n• JWT/OAuth for authentication\n• CORS configuration\n• Rate limiting\n• Security headers (CSP, HSTS)\n• Regular dependency updates\n• Penetration testing\n• OWASP Top 10 awareness",
  git: "Git best practices:\n• Write clear commit messages\n• Use feature branches\n• Pull requests for code review\n• Conventional commits (feat:, fix:, chore:)\n• Rebase vs merge strategy\n• .gitignore for sensitive files\n• Tag releases with semantic versioning\n• Protect main branch",
  testing: "Testing strategies:\n• Unit tests: Individual functions/components\n• Integration tests: Module interactions\n• E2E tests: Full user workflows\n• TDD: Write tests before code\n• Coverage: Aim for 80%+ on critical paths\n• Tools: Jest, Pytest, Cypress, Playwright\n• CI/CD integration for automated testing",
  systemdesign: "System design fundamentals:\n• Load balancing (round-robin, least connections)\n• Caching (Redis, CDN, browser cache)\n• Database sharding & replication\n• Message queues (Kafka, RabbitMQ)\n• CAP theorem trade-offs\n• Horizontal vs vertical scaling\n• Rate limiting & circuit breakers\n• Monitoring & observability",
  cloud: "Cloud computing overview:\n☁️ IaaS: VMs, storage, networking (EC2, Azure VMs)\n📦 PaaS: Managed platforms (Heroku, App Engine)\n⚡ Serverless: Event-driven functions (Lambda, Cloud Functions)\n🐳 Containers: Docker + Kubernetes\n💾 Storage: Object (S3), Block (EBS), File (EFS)\n🔒 Security: IAM, VPC, encryption at rest/transit",
};

// Topic detection keywords mapped to knowledge keys
const TOPIC_MAP = [
  { keywords: ['python', 'django', 'flask', 'fastapi'], topic: 'python' },
  { keywords: ['javascript', 'node.js', 'nodejs', 'npm', 'deno', 'bun'], topic: 'javascript' },
  { keywords: ['java', 'spring boot', 'jvm', 'maven', 'gradle'], topic: 'java' },
  { keywords: ['typescript', 'type script'], topic: 'typescript' },
  { keywords: ['rust', 'cargo', 'rustlang'], topic: 'rust' },
  { keywords: ['golang', 'go lang', 'go programming'], topic: 'go' },
  { keywords: ['c++', 'cpp', 'c plus plus'], topic: 'cpp' },
  { keywords: ['react', 'jsx', 'hooks', 'redux', 'react.js', 'reactjs'], topic: 'react' },
  { keywords: ['angular', 'angularjs', 'rxjs'], topic: 'angular' },
  { keywords: ['vue', 'vuejs', 'vue.js', 'vuex', 'pinia'], topic: 'vue' },
  { keywords: ['next.js', 'nextjs', 'next js'], topic: 'nextjs' },
  { keywords: ['docker', 'container', 'dockerfile'], topic: 'docker' },
  { keywords: ['kubernetes', 'k8s', 'kubectl', 'helm'], topic: 'kubernetes' },
  { keywords: ['aws', 'amazon web', 'ec2', 's3', 'lambda'], topic: 'aws' },
  { keywords: ['tensorflow', 'tf', 'keras'], topic: 'tensorflow' },
  { keywords: ['pytorch', 'torch'], topic: 'pytorch' },
  { keywords: ['resume', 'cv', 'curriculum vitae'], topic: 'resume' },
  { keywords: ['interview', 'interviewing', 'behavioral', 'technical interview'], topic: 'interview' },
  { keywords: ['salary', 'compensation', 'pay', 'negotiate', 'negotiation', 'offer'], topic: 'salary' },
  { keywords: ['freelanc', 'upwork', 'fiverr', 'contract work'], topic: 'freelancing' },
  { keywords: ['remote', 'work from home', 'wfh', 'hybrid'], topic: 'remote' },
  { keywords: ['microservice', 'micro service', 'monolith'], topic: 'microservices' },
  { keywords: ['devops', 'ci/cd', 'cicd', 'pipeline', 'deployment'], topic: 'devops' },
  { keywords: ['machine learning', 'ml', 'deep learning', 'neural network', 'ai', 'artificial intelligence', 'nlp', 'computer vision'], topic: 'ml' },
  { keywords: ['api', 'rest', 'graphql', 'endpoint', 'grpc'], topic: 'api' },
  { keywords: ['database', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'db'], topic: 'database' },
  { keywords: ['security', 'authentication', 'authorization', 'oauth', 'jwt', 'xss', 'csrf', 'injection'], topic: 'security' },
  { keywords: ['git', 'github', 'gitlab', 'version control', 'branch', 'merge', 'commit'], topic: 'git' },
  { keywords: ['test', 'testing', 'unit test', 'integration test', 'tdd', 'jest', 'pytest', 'cypress'], topic: 'testing' },
  { keywords: ['system design', 'scalab', 'load balanc', 'caching', 'distributed', 'architecture'], topic: 'systemdesign' },
  { keywords: ['cloud', 'azure', 'gcp', 'google cloud', 'serverless', 'iaas', 'paas', 'saas'], topic: 'cloud' },
];

// General response patterns
const PATTERNS = [
  { test: /\b(what is|what's|what are|define|explain|tell me about|describe)\b/i, prefix: "Great question! Here's what you should know:\n\n" },
  { test: /\b(how to|how do|how can|how should|steps to|guide|tutorial)\b/i, prefix: "Here's a helpful guide:\n\n" },
  { test: /\b(best|top|recommend|suggest|should i|which)\b/i, prefix: "Here are my recommendations:\n\n" },
  { test: /\b(difference|vs|versus|compare|comparison|between)\b/i, prefix: "Here's a comparison:\n\n" },
  { test: /\b(why|reason|benefit|advantage|important)\b/i, prefix: "Here's why this matters:\n\n" },
  { test: /\b(example|sample|show me|demo|code)\b/i, prefix: "Here's a practical example:\n\n" },
];

const GREETINGS = [
  { test: /^(hi|hello|hey|howdy|hola|good morning|good evening|good afternoon|namaste|vanakkam)/i,
    response: "Hello! 👋 I'm your AI Career Copilot. I can help you with:\n\n📄 Resume tips & ATS optimization\n💻 Technical skills & learning paths\n🎯 Career guidance & job search\n🗣️ Interview preparation\n💰 Salary negotiation\n🔧 Programming & tech questions\n\nAsk me anything!" },
  { test: /\b(thank|thanks|thx|ty|appreciate)\b/i,
    response: "You're welcome! 😊 I'm always here to help. Feel free to ask me anything else about your career, tech skills, or resume. Good luck on your journey! 🚀" },
  { test: /\b(bye|goodbye|see you|later|gtg)\b/i,
    response: "Goodbye! 👋 Best of luck with your career journey. Come back anytime you need help with resumes, interviews, or career advice. You've got this! 💪" },
  { test: /\b(who are you|what are you|your name|about you)\b/i,
    response: "I'm ResumeIQ's AI Career Copilot! 🤖✨\n\nI'm designed to help you with:\n• Resume analysis & improvement\n• Career guidance & planning\n• Technical skill recommendations\n• Interview preparation\n• Job market insights\n\nI use NLP and knowledge from the latest industry trends to provide personalized advice. Ask me anything!" },
];

const CAREER_RESPONSES = {
  roadmap: "Career roadmap planning:\n\n🗺️ 1. Define your target role\n📚 2. Identify required skills (check job postings)\n🎯 3. Gap analysis (what you have vs need)\n📅 4. Create a 3-6 month learning plan\n🛠️ 5. Build portfolio projects\n🤝 6. Network actively (LinkedIn, meetups)\n📝 7. Apply strategically (quality > quantity)\n📈 8. Track progress and iterate\n\nWhat role are you targeting?",
  portfolio: "Building a strong portfolio:\n\n🌐 Personal website/blog\n💻 3-5 quality projects on GitHub\n📊 Case studies with problem → solution → impact\n🎨 Clean documentation and READMEs\n📹 Demo videos or live links\n✍️ Technical blog posts\n\nProject ideas:\n• Full-stack web app with auth\n• ML model with deployed API\n• Mobile app on app stores\n• Open-source contribution\n• Data visualization dashboard",
  networking: "Professional networking guide:\n\n🔗 LinkedIn: Optimize profile, post regularly, engage with others\n🤝 Conferences: Attend tech meetups, hackathons\n💬 Communities: Discord, Reddit, Stack Overflow\n📧 Cold outreach: Personalized, value-first messages\n☕ Coffee chats: 15-min informational interviews\n🎤 Speaking: Give talks at local meetups\n✍️ Writing: Technical blogs on Medium, Dev.to\n👥 Mentorship: Both seeking and offering",
  burnout: "Dealing with developer burnout:\n\n🧘 Recognition: Accept it's real and common\n⏰ Boundaries: Set work hours, disconnect evenings/weekends\n🏃 Physical health: Exercise, sleep 7-8h, eat well\n🎮 Hobbies: Non-tech activities you enjoy\n🗣️ Talk: Therapist, mentor, trusted colleague\n📅 Breaks: Use vacation days, take mental health days\n🔄 Change: Switch projects, learn something fun\n💪 Say no: Guard your time and energy",
  learning: "Effective learning strategies for developers:\n\n📖 Learn by doing (projects > tutorials)\n🔁 Spaced repetition for concepts\n👥 Teach others to solidify understanding\n📝 Take notes and build a knowledge base\n🎯 Focus on fundamentals, then specialize\n⏱️ Pomodoro technique (25min focus, 5min break)\n🔧 Build, break, fix, repeat\n📚 Resources: Coursera, Udemy, freeCodeCamp, YouTube\n🏆 Set measurable goals (e.g., 'Build X by date Y')",
};

export function generateSmartResponse(message) {
  const lower = message.toLowerCase().trim();

  // 1. Check greetings first
  for (const g of GREETINGS) {
    if (g.test.test(lower)) return g.response;
  }

  // 2. Check SPECIFIC tech topics FIRST (highest priority)
  let matchedTopic = null;
  let bestMatchLen = 0;
  for (const { keywords, topic } of TOPIC_MAP) {
    for (const kw of keywords) {
      if (lower.includes(kw) && kw.length > bestMatchLen) {
        matchedTopic = topic;
        bestMatchLen = kw.length;
      }
    }
  }

  if (matchedTopic && KNOWLEDGE[matchedTopic]) {
    let prefix = '';
    for (const p of PATTERNS) {
      if (p.test.test(lower)) { prefix = p.prefix; break; }
    }
    return (prefix || "Here's what I know:\n\n") + KNOWLEDGE[matchedTopic];
  }

  // 3. Check exact career-specific keywords
  if (lower.match(/\b(roadmap|career path|career plan)\b/)) return CAREER_RESPONSES.roadmap;
  if (lower.match(/\b(portfolio|showcase|project ideas)\b/)) return CAREER_RESPONSES.portfolio;
  if (lower.match(/\b(networking|professional network|meetup)\b/)) return CAREER_RESPONSES.networking;
  if (lower.match(/\b(burnout|stress|overwhelm|tired|exhausted|demotivat)\b/)) return CAREER_RESPONSES.burnout;

  // 4. Comparison questions
  if (lower.match(/\b(vs|versus|compare|between|difference)\b/)) {
    return `That's a great comparison question! Here's my analysis:\n\nBoth technologies have their strengths. The best choice depends on:\n\n📋 **Project requirements** — Scale, performance, team size\n🎯 **Use case** — What problem are you solving?\n👥 **Team expertise** — What does your team know?\n📈 **Market demand** — Check job postings in your area\n🔮 **Future growth** — Community size, corporate backing\n\nCould you tell me more specifics about your use case? I can give a more tailored recommendation! 🎯`;
  }

  // 5. Learning/study questions (only if no specific topic matched above)
  if (lower.match(/\b(how to learn|study plan|learning path|upskill|self.taught|where to start|beginner|fresher)\b/)) {
    return CAREER_RESPONSES.learning;
  }

  // 6. ATS / score questions
  if (lower.match(/\b(ats|score|rating)\b/)) {
    return `Your ATS (Applicant Tracking System) score is calculated based on:\n\n📋 **Contact Info** — Name, email, phone, LinkedIn\n💼 **Work Experience** — Relevant roles, achievements, dates\n🛠️ **Skills** — Technical & soft skills matching job requirements\n🎓 **Education** — Degrees, certifications, coursework\n📝 **Formatting** — Clean structure, proper headings\n🔑 **Keywords** — Industry-specific terms and phrases\n\nUpload your resume on the Upload page to get your detailed ATS score breakdown! The AI will analyze each section and provide improvement suggestions.`;
  }

  // 7. Job/career questions
  if (lower.match(/\b(job|career|hire|hiring|recruit|apply|application|company|startup|faang|maang)\b/)) {
    return `Career & job search guidance:\n\n🎯 **Strategy**:\n• Target roles matching your skills\n• Research companies thoroughly\n• Tailor resume for each application\n\n📝 **Application Tips**:\n• Apply early (within first 48 hours)\n• Use job boards: LinkedIn, Indeed, AngelList, HN Who's Hiring\n• Referrals increase success rate by 5-10x\n\n💡 **Stand Out**:\n• Personal projects on GitHub\n• Technical blog posts\n• Open-source contributions\n• Relevant certifications\n\nWhat specific role or company are you interested in?`;
  }

  // 8. General fallback — still give a good answer
  return `That's a thoughtful question! Here's my perspective:\n\n🤔 Based on current industry trends and best practices:\n\n1. **Research thoroughly** — Look into the latest developments in this area\n2. **Practice hands-on** — Build projects to solidify your understanding\n3. **Learn from experts** — Follow industry leaders on LinkedIn, Twitter, YouTube\n4. **Join communities** — Reddit, Discord, Stack Overflow for peer support\n5. **Stay consistent** — Daily practice beats occasional cramming\n\n💡 **Pro tip**: The tech industry values practical skills over theoretical knowledge. Focus on building things!\n\nWant me to go deeper on any specific topic? I can help with:\n• 📄 Resume & career advice\n• 💻 Programming & frameworks\n• 🎯 Interview preparation\n• 📈 Skill development paths\n• 🔧 Tech architecture & tools\n\nJust ask! 🚀`;
}
