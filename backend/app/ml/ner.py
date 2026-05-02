"""
Named Entity Recognition (NER) Pipeline for Resume Parsing.

Uses spaCy for base NER + custom rule-based extraction for:
- Skills (from a curated skill taxonomy)
- Experience entries
- Education entries
- Contact information
- Certifications

This hybrid approach (statistical NER + pattern matching) gives us
high accuracy without needing a custom-trained NER model.
"""
import re
import spacy
from typing import Dict, List, Any, Optional

# ── Skill Taxonomy ──
# Comprehensive list of technical and soft skills for matching.
# In production, this would be loaded from a database or config file.
SKILL_TAXONOMY = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "lua",
    "dart", "elixir", "haskell", "clojure", "objective-c",
    # Web Frameworks
    "react", "angular", "vue", "vue.js", "next.js", "nuxt.js", "svelte",
    "django", "flask", "fastapi", "express", "express.js", "spring boot",
    "rails", "laravel", "asp.net", "gin", "fiber",
    # Data & ML
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "scipy", "matplotlib", "seaborn", "plotly", "opencv", "spacy", "nltk",
    "hugging face", "transformers", "bert", "gpt", "llm", "mlops",
    "machine learning", "deep learning", "natural language processing",
    "computer vision", "reinforcement learning", "data science",
    "data analysis", "data engineering", "feature engineering",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "sqlite", "oracle", "sql server",
    "neo4j", "influxdb", "firebase",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "terraform", "ansible", "jenkins", "github actions", "gitlab ci",
    "circleci", "nginx", "apache", "linux", "bash",
    "ci/cd", "devops", "microservices", "serverless",
    # Tools & Practices
    "git", "jira", "confluence", "figma", "agile", "scrum",
    "kanban", "tdd", "rest api", "graphql", "grpc", "websockets",
    "oauth", "jwt", "api design", "system design",
    # Soft Skills
    "leadership", "project management", "communication",
    "problem solving", "teamwork", "mentoring", "strategic planning",
}

# ── Section Header Patterns ──
SECTION_PATTERNS = {
    "experience": re.compile(
        r'(?i)^(work\s+)?experience|employment\s+history|professional\s+experience|work\s+history',
        re.MULTILINE
    ),
    "education": re.compile(
        r'(?i)^education|academic|qualifications|degrees?',
        re.MULTILINE
    ),
    "skills": re.compile(
        r'(?i)^(technical\s+)?skills|competenc|technologies|tools|expertise',
        re.MULTILINE
    ),
    "certifications": re.compile(
        r'(?i)^certifications?|licenses?|accreditations?',
        re.MULTILINE
    ),
    "summary": re.compile(
        r'(?i)^(professional\s+)?summary|objective|profile|about\s+me',
        re.MULTILINE
    ),
}

# ── Contact Patterns ──
EMAIL_PATTERN = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
PHONE_PATTERN = re.compile(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}')
LINKEDIN_PATTERN = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)

# ── Lazy-load spaCy model ──
_nlp = None


def get_nlp():
    """Lazy-load spaCy model to avoid startup overhead."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback: download the model if not installed
            from spacy.cli import download
            download("en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract contact information using regex patterns."""
    nlp = get_nlp()
    # Use spaCy NER for person name (first PERSON entity found)
    doc = nlp(text[:1000])  # Only process first 1000 chars for contact
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    # If no PERSON entity found, use the first non-empty line as name
    if not name:
        for line in text.split('\n'):
            line = line.strip()
            if line and not EMAIL_PATTERN.search(line) and not PHONE_PATTERN.search(line):
                name = line
                break

    email_match = EMAIL_PATTERN.search(text)
    phone_match = PHONE_PATTERN.search(text)
    linkedin_match = LINKEDIN_PATTERN.search(text)

    # Extract location using spaCy GPE entities
    location = None
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            location = ent.text
            break

    return {
        "name": name,
        "email": email_match.group() if email_match else None,
        "phone": phone_match.group() if phone_match else None,
        "location": location,
        "linkedin": linkedin_match.group() if linkedin_match else None,
    }


def extract_skills(text: str) -> List[str]:
    """
    Extract skills by matching against our skill taxonomy.
    Uses case-insensitive matching with word boundary awareness.
    """
    text_lower = text.lower()
    found_skills = []

    for skill in SKILL_TAXONOMY:
        # Use word boundary matching for short skill names to avoid false positives
        if len(skill) <= 3:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title() if len(skill) > 2 else skill.upper())
        else:
            if skill in text_lower:
                # Capitalize properly
                found_skills.append(skill.title())

    return sorted(set(found_skills))


def extract_experience(text: str) -> List[Dict[str, Any]]:
    """
    Extract work experience entries using pattern matching and spaCy NER.
    Looks for patterns like: "Title at Company (Date - Date)"
    """
    nlp = get_nlp()
    experiences = []

    # Find the experience section
    exp_match = SECTION_PATTERNS["experience"].search(text)
    if not exp_match:
        return experiences

    # Get text from experience section to next section
    exp_start = exp_match.end()
    next_section_start = len(text)
    for key, pattern in SECTION_PATTERNS.items():
        if key == "experience":
            continue
        match = pattern.search(text[exp_start:])
        if match:
            next_section_start = min(next_section_start, exp_start + match.start())

    exp_text = text[exp_start:next_section_start]

    # Parse experience entries using date patterns as delimiters
    date_pattern = re.compile(
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[\s,]+\d{4})\s*[-–]\s*'
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[\s,]+\d{4}|Present|Current)',
        re.IGNORECASE
    )

    # Split by common separators and look for structure
    lines = [l.strip() for l in exp_text.split('\n') if l.strip()]
    current_entry = {}

    for i, line in enumerate(lines):
        date_match = date_pattern.search(line)
        if date_match or (i > 0 and any(keyword in line.lower() for keyword in
                                         ['engineer', 'developer', 'manager', 'analyst',
                                          'designer', 'architect', 'lead', 'director',
                                          'consultant', 'specialist', 'coordinator'])):
            # Save previous entry if exists
            if current_entry.get('title'):
                experiences.append(current_entry)
                current_entry = {}

            # Use spaCy to extract ORG entities for company name
            doc = nlp(line)
            company = None
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    company = ent.text
                    break

            current_entry = {
                "title": line.split(' at ')[0].split(' - ')[0].strip() if ' at ' in line or ' - ' in line else line.strip(),
                "company": company or (line.split(' at ')[-1].strip() if ' at ' in line else ""),
                "dates": date_match.group() if date_match else "",
                "description": "",
            }
        elif current_entry:
            # Append to current entry description
            current_entry["description"] += line + " "

    # Don't forget the last entry
    if current_entry.get('title'):
        experiences.append(current_entry)

    # Clean up descriptions
    for exp in experiences:
        exp["description"] = exp["description"].strip()

    return experiences[:10]  # Cap at 10 entries


def extract_education(text: str) -> List[Dict[str, Any]]:
    """Extract education entries."""
    education = []

    edu_match = SECTION_PATTERNS["education"].search(text)
    if not edu_match:
        return education

    edu_start = edu_match.end()
    next_section_start = len(text)
    for key, pattern in SECTION_PATTERNS.items():
        if key == "education":
            continue
        match = pattern.search(text[edu_start:])
        if match:
            next_section_start = min(next_section_start, edu_start + match.start())

    edu_text = text[edu_start:next_section_start]

    # Common degree patterns
    degree_pattern = re.compile(
        r"(Bachelor|Master|Ph\.?D|MBA|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|"
        r"B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?|Associate|Diploma)",
        re.IGNORECASE
    )

    nlp = get_nlp()
    lines = [l.strip() for l in edu_text.split('\n') if l.strip()]

    for line in lines:
        degree_match = degree_pattern.search(line)
        if degree_match:
            doc = nlp(line)
            institution = None
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    institution = ent.text
                    break

            year_match = re.search(r'20\d{2}|19\d{2}', line)
            gpa_match = re.search(r'(?:GPA|CGPA)[:\s]*(\d+\.?\d*)', line, re.IGNORECASE)

            education.append({
                "degree": line.strip(),
                "institution": institution or "",
                "year": year_match.group() if year_match else None,
                "gpa": gpa_match.group(1) if gpa_match else None,
            })

    return education[:5]  # Cap at 5 entries


def extract_summary(text: str) -> Optional[str]:
    """Extract professional summary/objective section."""
    summary_match = SECTION_PATTERNS["summary"].search(text)
    if not summary_match:
        # If no explicit summary section, use first paragraph
        paragraphs = text.split('\n\n')
        for p in paragraphs[1:3]:  # Skip name line, check next 2 paragraphs
            if len(p.strip()) > 50:
                return p.strip()[:500]
        return None

    summary_start = summary_match.end()
    next_section_start = len(text)
    for key, pattern in SECTION_PATTERNS.items():
        if key == "summary":
            continue
        match = pattern.search(text[summary_start:])
        if match:
            next_section_start = min(next_section_start, summary_start + match.start())

    return text[summary_start:next_section_start].strip()[:500]


def extract_certifications(text: str) -> List[str]:
    """Extract certification entries."""
    cert_match = SECTION_PATTERNS["certifications"].search(text)
    if not cert_match:
        return []

    cert_start = cert_match.end()
    next_section_start = len(text)
    for key, pattern in SECTION_PATTERNS.items():
        if key == "certifications":
            continue
        match = pattern.search(text[cert_start:])
        if match:
            next_section_start = min(next_section_start, cert_start + match.start())

    cert_text = text[cert_start:next_section_start]
    certs = [l.strip().lstrip('•-*').strip() for l in cert_text.split('\n') if l.strip()]
    return certs[:10]


def extract_all(text: str) -> Dict[str, Any]:
    """
    Master extraction function — runs all NER extractors on the resume text
    and returns a unified structured data dictionary.
    """
    return {
        "contact": extract_contact_info(text),
        "summary": extract_summary(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "certifications": extract_certifications(text),
        "raw_text": text,
    }
