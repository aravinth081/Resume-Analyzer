// ─── NLP Resume Analyzer — extracts real data from resume text ───

const SKILL_DB = {
  languages: ['Python','JavaScript','TypeScript','Java','C++','C#','C','Go','Rust','Kotlin','Swift','Ruby','PHP','Scala','R','MATLAB','Perl','Dart','Lua','Shell','Bash','PowerShell','Objective-C','Haskell','Elixir','Clojure','Groovy','VHDL','Verilog','Assembly','COBOL','Fortran','Julia'],
  frameworks: ['React','Angular','Vue.js','Vue','Next.js','Nuxt.js','Svelte','Django','Flask','FastAPI','Spring Boot','Spring','Express.js','Express','Nest.js','Rails','Ruby on Rails','Laravel','ASP.NET','.NET','Gatsby','Remix','Astro','Flutter','React Native','SwiftUI','Jetpack Compose','Electron','Qt','Streamlit','Gradio'],
  databases: ['MySQL','PostgreSQL','MongoDB','Redis','SQLite','Oracle','SQL Server','DynamoDB','Cassandra','Firebase','Firestore','CouchDB','Neo4j','MariaDB','Elasticsearch','Supabase','PlanetScale','CockroachDB','InfluxDB','TimescaleDB'],
  cloud: ['AWS','Azure','GCP','Google Cloud','Heroku','Vercel','Netlify','DigitalOcean','Cloudflare','Oracle Cloud','IBM Cloud','Alibaba Cloud','Lambda','EC2','S3','CloudFront','Route 53','ECS','EKS','Fargate','SageMaker','Bedrock'],
  devops: ['Docker','Kubernetes','Terraform','Ansible','Jenkins','GitHub Actions','GitLab CI','CircleCI','Travis CI','ArgoCD','Helm','Prometheus','Grafana','Nginx','Apache','Caddy','Vagrant','Puppet','Chef','Packer','Consul','Vault','Istio','Envoy'],
  ai_ml: ['TensorFlow','PyTorch','Keras','Scikit-learn','OpenCV','NLTK','spaCy','Hugging Face','LangChain','LlamaIndex','Pandas','NumPy','SciPy','Matplotlib','Seaborn','Plotly','XGBoost','LightGBM','CatBoost','YOLO','Stable Diffusion','GPT','BERT','Transformers','RAG','Fine-tuning','MLflow','Kubeflow','Weights & Biases','DVC','ONNX','TensorRT','OpenAI','Gemini'],
  tools: ['Git','GitHub','GitLab','Bitbucket','Jira','Confluence','Slack','Notion','Figma','Adobe XD','Sketch','Postman','Swagger','VS Code','IntelliJ','Eclipse','Vim','Linux','Unix','Windows Server','macOS','Webpack','Vite','Babel','ESLint','Prettier','npm','yarn','pnpm','pip','conda','Maven','Gradle','CMake','Make'],
  data: ['SQL','NoSQL','ETL','Data Pipeline','Apache Spark','Hadoop','Kafka','Airflow','dbt','Snowflake','BigQuery','Redshift','Databricks','Tableau','Power BI','Looker','Metabase','Data Warehouse','Data Lake','Data Modeling','Star Schema','OLAP','Data Governance'],
  concepts: ['REST API','GraphQL','gRPC','WebSocket','Microservices','Monolith','Event-Driven','CQRS','Domain-Driven Design','Clean Architecture','MVC','MVVM','SOLID','Design Patterns','OOP','Functional Programming','Agile','Scrum','Kanban','TDD','BDD','CI/CD','DevOps','MLOps','DataOps','SRE','Cloud Native','Serverless','Edge Computing','IoT','Blockchain','Web3','Cybersecurity','Zero Trust','OAuth','JWT','SAML','SSO','RBAC','Penetration Testing'],
};

const SECTION_HEADERS = {
  experience: /\b(experience|work\s*history|employment|professional\s*experience|work\s*experience|career\s*history)\b/i,
  education: /\b(education|academic|qualification|degree|university|college|school|certification|certifications)\b/i,
  skills: /\b(skills|technical\s*skills|technologies|competencies|proficiencies|tools|expertise|tech\s*stack)\b/i,
  projects: /\b(projects|personal\s*projects|portfolio|key\s*projects|side\s*projects)\b/i,
  summary: /\b(summary|objective|profile|about\s*me|professional\s*summary|career\s*objective|overview)\b/i,
  contact: /\b(contact|email|phone|address|linkedin|github|portfolio|website)\b/i,
};

// Extract real skills from text
export function extractSkills(text) {
  const lower = text.toLowerCase();
  const found = new Set();
  for (const category of Object.values(SKILL_DB)) {
    for (const skill of category) {
      const escaped = skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`\\b${escaped}\\b`, 'i');
      if (regex.test(text) || lower.includes(skill.toLowerCase())) {
        found.add(skill);
      }
    }
  }
  return [...found];
}

// Extract email
export function extractEmail(text) {
  const match = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
  return match ? match[0] : null;
}

// Extract phone
export function extractPhone(text) {
  const match = text.match(/(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}/);
  return match ? match[0] : null;
}

// Extract LinkedIn
export function extractLinkedIn(text) {
  const match = text.match(/linkedin\.com\/in\/[\w-]+/i);
  return match ? match[0] : null;
}

// Extract GitHub
export function extractGitHub(text) {
  const match = text.match(/github\.com\/[\w-]+/i);
  return match ? match[0] : null;
}

// Extract name (first line heuristic)
export function extractName(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  for (const line of lines.slice(0, 5)) {
    const clean = line.replace(/[^a-zA-Z\s.]/g, '').trim();
    if (clean.length > 2 && clean.length < 50 && !clean.match(/@|http|www|phone|email|address/i)) {
      const words = clean.split(/\s+/);
      if (words.length >= 2 && words.length <= 5 && words.every(w => /^[A-Z]/.test(w))) return clean;
    }
  }
  return lines[0]?.substring(0, 40) || 'Candidate';
}

// Split text into sections
export function extractSections(text) {
  const lines = text.split('\n');
  const sections = {};
  let currentSection = 'header';
  sections[currentSection] = [];
  for (const line of lines) {
    let matched = false;
    for (const [name, regex] of Object.entries(SECTION_HEADERS)) {
      if (regex.test(line) && line.trim().length < 60) {
        currentSection = name;
        sections[currentSection] = sections[currentSection] || [];
        matched = true;
        break;
      }
    }
    if (!matched) {
      sections[currentSection] = sections[currentSection] || [];
      sections[currentSection].push(line);
    }
  }
  return sections;
}

// Extract experience entries
export function extractExperience(text) {
  const sections = extractSections(text);
  const expText = (sections.experience || []).join('\n');
  const entries = [];
  const datePattern = /(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{0,4}\s*[-–to]*\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)?\s*\d{0,4}|(?:\d{4}\s*[-–to]*\s*(?:\d{4}|Present|Current|Now)))/gi;
  const titlePattern = /\b(engineer|developer|manager|analyst|designer|architect|lead|director|intern|consultant|specialist|scientist|administrator|coordinator|associate|officer|executive|head|vp|cto|ceo|cfo|founder|co-founder)\b/gi;
  const companyPattern = /\b(?:at|@)\s+([A-Z][a-zA-Z\s&.]+)/g;
  const lines = expText.split('\n').filter(l => l.trim());
  let currentEntry = null;
  for (const line of lines) {
    const hasTitle = titlePattern.test(line);
    titlePattern.lastIndex = 0;
    const dateMatch = line.match(datePattern);
    if (hasTitle || (dateMatch && line.trim().length < 100)) {
      if (currentEntry) entries.push(currentEntry);
      currentEntry = { title: line.trim().substring(0, 80), company: '', dates: dateMatch ? dateMatch[0] : '', description: '' };
      const cm = line.match(companyPattern);
      if (cm) currentEntry.company = cm[0].replace(/^(?:at|@)\s+/i, '');
    } else if (currentEntry && line.trim()) {
      currentEntry.description += (currentEntry.description ? '; ' : '') + line.trim();
    }
  }
  if (currentEntry) entries.push(currentEntry);
  return entries.length > 0 ? entries : [{ title: 'Experience details found in resume', company: '', dates: '', description: expText.substring(0, 200) }];
}

// Extract education
export function extractEducation(text) {
  const sections = extractSections(text);
  const eduText = (sections.education || []).join('\n');
  const entries = [];
  const degreePattern = /\b(B\.?Tech|B\.?E|B\.?Sc|B\.?A|B\.?Com|M\.?Tech|M\.?E|M\.?Sc|M\.?A|MBA|Ph\.?D|Diploma|Bachelor|Master|Associate|Doctorate|B\.?S|M\.?S|BCA|MCA|BBA)\b/gi;
  const lines = eduText.split('\n').filter(l => l.trim());
  let currentEntry = null;
  for (const line of lines) {
    const degreeMatch = line.match(degreePattern);
    if (degreeMatch) {
      if (currentEntry) entries.push(currentEntry);
      const yearMatch = line.match(/\b(19|20)\d{2}\b/);
      currentEntry = { degree: line.trim().substring(0, 100), institution: '', year: yearMatch ? yearMatch[0] : '' };
    } else if (currentEntry && line.trim()) {
      if (!currentEntry.institution) currentEntry.institution = line.trim().substring(0, 80);
    }
  }
  if (currentEntry) entries.push(currentEntry);
  return entries;
}

// Score the resume based on real content
export function scoreResume(text, skills, experience, education) {
  const scores = {};
  // Contact info scoring
  const hasEmail = !!extractEmail(text);
  const hasPhone = !!extractPhone(text);
  const hasLinkedin = !!extractLinkedIn(text);
  const hasGithub = !!extractGitHub(text);
  const contactScore = Math.min(100, (hasEmail ? 30 : 0) + (hasPhone ? 25 : 0) + (hasLinkedin ? 25 : 0) + (hasGithub ? 20 : 0));
  scores.contact_info = { score: contactScore, feedback: `${[hasEmail && 'Email', hasPhone && 'Phone', hasLinkedin && 'LinkedIn', hasGithub && 'GitHub'].filter(Boolean).join(', ')} found. ${contactScore < 80 ? 'Add missing contact details.' : 'Complete contact section!'}` };

  // Skills scoring
  const skillScore = Math.min(100, skills.length * 6 + 10);
  scores.skills = { score: skillScore, feedback: `${skills.length} technical skills detected. ${skillScore < 60 ? 'Consider adding more relevant skills.' : 'Strong technical skill set!'}` };

  // Experience scoring
  const expScore = Math.min(100, experience.length * 20 + (text.match(/\d+%|\d+x|\$[\d,]+/g)?.length || 0) * 10 + 20);
  const hasMetrics = (text.match(/\d+%|\d+x|increased|improved|reduced|optimized|delivered|achieved/gi) || []).length;
  scores.work_experience = { score: expScore, feedback: `${experience.length} experience entries found. ${hasMetrics > 0 ? `${hasMetrics} quantified achievements detected.` : 'Add measurable achievements for higher score.'}` };

  // Education scoring
  const eduScore = education.length > 0 ? Math.min(100, education.length * 35 + 30) : 20;
  scores.education = { score: eduScore, feedback: education.length > 0 ? `${education.length} education entries found.` : 'No education section detected. Add your educational background.' };

  // Formatting scoring
  const sections = extractSections(text);
  const sectionCount = Object.keys(sections).filter(k => (sections[k] || []).length > 0).length;
  const formatScore = Math.min(100, sectionCount * 15 + (text.length > 500 ? 20 : 0) + (text.length > 1500 ? 10 : 0));
  scores.formatting = { score: formatScore, feedback: `${sectionCount} resume sections identified. ${formatScore >= 70 ? 'Well-structured resume.' : 'Consider adding more distinct sections.'}` };

  // Keywords scoring
  const actionVerbs = (text.match(/\b(developed|designed|implemented|created|built|managed|led|optimized|deployed|analyzed|architected|integrated|automated|delivered|launched|scaled|mentored|collaborated)\b/gi) || []).length;
  const keywordScore = Math.min(100, actionVerbs * 5 + skills.length * 3 + 10);
  scores.keywords = { score: keywordScore, feedback: `${actionVerbs} action verbs and ${skills.length} technical keywords found. ${keywordScore < 60 ? 'Use more industry-specific terms.' : 'Good keyword density!'}` };

  // Overall score
  const overall = Math.round(Object.values(scores).reduce((sum, s) => sum + s.score, 0) / Object.keys(scores).length);

  // Suggestions
  const suggestions = [];
  if (contactScore < 80) suggestions.push('Add LinkedIn profile and GitHub links to your contact section');
  if (skillScore < 60) suggestions.push('List more technical skills relevant to your target role');
  if (!hasMetrics) suggestions.push('Add quantified achievements (e.g., "Improved load time by 40%")');
  if (education.length === 0) suggestions.push('Add education section with degrees and certifications');
  if (actionVerbs < 5) suggestions.push('Use more action verbs like Developed, Architected, Optimized');
  if (formatScore < 70) suggestions.push('Organize resume with clear section headers (Experience, Skills, Education)');
  if (keywordScore < 70) suggestions.push('Include more industry-specific keywords matching your target roles');
  if (suggestions.length < 3) suggestions.push('Consider adding a professional summary section at the top');

  return { overall, section_scores: scores, suggestions: suggestions.slice(0, 6) };
}

// Full analysis
export function analyzeResume(text, fileName) {
  const skills = extractSkills(text);
  const experience = extractExperience(text);
  const education = extractEducation(text);
  const name = extractName(text);
  const email = extractEmail(text);
  const phone = extractPhone(text);
  const linkedin = extractLinkedIn(text);
  const github = extractGitHub(text);
  const { overall, section_scores, suggestions } = scoreResume(text, skills, experience, education);

  return {
    overall_score: overall,
    section_scores,
    suggestions,
    parsed_data: {
      name, email, phone, linkedin, github,
      skills,
      experience,
      education,
      raw_text_length: text.length,
    },
  };
}
