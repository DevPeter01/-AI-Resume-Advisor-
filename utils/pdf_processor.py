import io
import re
from pypdf import PdfReader
import streamlit as st


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from an uploaded PDF file with error handling.
    """
    try:
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        
        if not text.strip():
            return None
            
        return text.strip()
        
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")
        return None


def extract_structured_data(text):
    """
    Extract structured data from resume text including:
    - Skills (technical, tools, soft skills)
    - Experience (role, duration, impact)
    - Projects (problem -> action -> result)
    - Education & certifications
    """
    # Extract sections based on common headings
    sections = {}
    
    # Define section patterns
    patterns = {
        'education': [
            r'(education|academic|qualifications).*?(experience|skills|projects|certifications|$)',
            r'(school|university|degree|diploma|bachelor|master|phd).*?(experience|skills|projects|certifications|$)'
        ],
        'skills': [
            r'(skills|technologies|competencies|technical skills).*?(experience|projects|education|certifications|$)',
            r'(technical|programming|languages|frameworks|tools).*?(experience|projects|education|certifications|$)'
        ],
        'experience': [
            r'(experience|work experience|employment|professional experience).*?(skills|projects|education|certifications|$)',
            r'(professional|career|job|position|employment).*?(skills|projects|education|certifications|$)'
        ],
        'projects': [
            r'(projects|portfolio|personal projects).*?(experience|skills|education|certifications|$)'
        ],
        'certifications': [
            r'(certifications|certificates|credentials|licenses).*?(experience|skills|projects|education|$)'
        ]
    }
    
    # Process each section
    lower_text = text.lower()
    for section, section_patterns in patterns.items():
        extracted = []
        for pattern in section_patterns:
            match = re.search(pattern, lower_text, re.IGNORECASE | re.DOTALL)
            if match:
                section_start = match.end()
                # Look for the next section to determine the end
                next_sections = [p for p in patterns.keys() if p != section]
                next_section_pos = len(text)
                
                for next_sec in next_sections:
                    for next_pattern in patterns[next_sec]:
                        next_match = re.search(next_pattern, text[section_start:], re.IGNORECASE)
                        if next_match:
                            next_section_pos = min(next_section_pos, section_start + next_match.start())
                
                section_text = text[section_start:next_section_pos].strip()
                if section_text:
                    extracted.append(section_text)
        
        sections[section] = extracted
    
    # Extract contact info
    contact_patterns = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'(\\+\\d{1,3}[\\s-]?)?\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}',
        'linkedin': r'linkedin\\.com\\/in\\/[a-zA-Z0-9-]+',
        'github': r'github\\.com\\/[a-zA-Z0-9-]+'
    }
    
    contact_info = {}
    for key, pattern in contact_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        contact_info[key] = matches if matches else None
    
    # Extract skills specifically
    skills = extract_skills(text)
    
    # Extract experience details
    experience_details = extract_experience(text)
    
    # Extract projects
    projects = extract_projects(text)
    
    # Extract education
    education = extract_education(text)
    
    structured_data = {
        'raw_text': text,
        'contact_info': contact_info,
        'skills': skills,
        'experience': experience_details,
        'projects': projects,
        'education': education,
        'sections': sections
    }
    
    return structured_data


def extract_skills(text):
    """
    Extract skills grouped by type: technical, tools, soft skills
    """
    # Common skill keywords by category
    skill_keywords = {
        'programming_languages': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
            'scala', 'swift', 'kotlin', 'r', 'matlab', 'sql', 'html', 'css', 'sass', 'less'
        ],
        'technologies_frameworks': [
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'node.js', 'express',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'tensorflow', 'pytorch', 'mongodb',
            'postgresql', 'mysql', 'redis', 'git', 'jenkins', 'ansible', 'terraform'
        ],
        'soft_skills': [
            'leadership', 'communication', 'teamwork', 'problem-solving', 'adaptability',
            'critical thinking', 'creativity', 'time management', 'collaboration', 'negotiation',
            'conflict resolution', 'decision making', 'emotional intelligence'
        ],
        'tools': [
            'excel', 'powerpoint', 'jira', 'confluence', 'slack', 'figma', 'adobe', 'tableau',
            'salesforce', 'sap', 'oracle', 'photoshop', 'illustrator', 'indesign', 'autocad'
        ]
    }
    
    found_skills = {'technical': [], 'tools': [], 'soft_skills': []}
    
    text_lower = text.lower()
    
    for category, keywords in skill_keywords.items():
        for keyword in keywords:
            if re.search(r'\\b' + re.escape(keyword) + r'\\b', text_lower, re.IGNORECASE):
                if category == 'programming_languages' or category == 'technologies_frameworks':
                    if keyword not in found_skills['technical']:
                        found_skills['technical'].append(keyword)
                elif category == 'tools':
                    if keyword not in found_skills['tools']:
                        found_skills['tools'].append(keyword)
                elif category == 'soft_skills':
                    if keyword not in found_skills['soft_skills']:
                        found_skills['soft_skills'].append(keyword)
    
    return found_skills


def extract_experience(text):
    """
    Extract experience details: role, duration, impact
    """
    # Pattern to match job positions with company and duration
    experience_pattern = r'([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*\\s*(?:Engineer|Developer|Manager|Analyst|Designer|Scientist|Architect|Lead|Director|Specialist|Consultant|Administrator|Coordinator|Officer|Executive|Technician|Associate|Intern))\\s*at\\s*([A-Z][a-zA-Z\\s&\\-0-9]*)'
    
    # Alternative patterns for different formats
    alt_patterns = [
        r'([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*\\s*(?:Engineer|Developer|Manager|Analyst|Designer|Scientist|Architect|Lead|Director|Specialist|Consultant|Administrator|Coordinator|Officer|Executive|Technician|Associate|Intern)).*?([A-Z][a-zA-Z\\s&\\-0-9]+)(?:,|\\n)',
        r'([A-Z][a-zA-Z\\s&\\-0-9]+).*?([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*\\s*(?:Engineer|Developer|Manager|Analyst|Designer|Scientist|Architect|Lead|Director|Specialist|Consultant|Administrator|Coordinator|Officer|Executive|Technician|Associate|Intern))'
    ]
    
    experiences = []
    
    matches = re.findall(experience_pattern, text)
    for match in matches:
        role, company = match
        experiences.append({
            'role': role.strip(),
            'company': company.strip(),
            'duration': 'Duration not specified',
            'impact': 'Impact not detailed'
        })
    
    # Try alternative patterns if primary didn't yield results
    if not experiences:
        for pattern in alt_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2:
                    # Heuristic to determine which is role and which is company
                    role, company = match[0], match[1]
                    # Check if first element looks more like a role
                    if any(title in role.lower() for title in ['engineer', 'developer', 'manager', 'analyst', 'designer', 'scientist']):
                        pass  # role, company are in correct order
                    else:
                        role, company = company, role
                    
                    experiences.append({
                        'role': role.strip(),
                        'company': company.strip(),
                        'duration': 'Duration not specified',
                        'impact': 'Impact not detailed'
                    })
    
    return experiences


def extract_projects(text):
    """
    Extract projects with problem -> action -> result format
    """
    project_keywords = ['projects', 'project', 'portfolio', 'case study', 'work sample']
    
    # Find project sections
    project_matches = []
    for keyword in project_keywords:
        pattern = r'(' + keyword + r'.*?)(?=' + '|'.join([k for k in project_keywords if k != keyword]) + r'|education|skills|experience|$)'
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        project_matches.extend(matches)
    
    projects = []
    if project_matches:
        # Simplified extraction - in practice, this would need more sophisticated NLP
        project_text = ' '.join(project_matches)
        
        # Look for project-like entries
        project_entries = re.split(r'\\n\\s*\\n|\\n\\d+\\.|•', project_text)
        
        for entry in project_entries:
            entry = entry.strip()
            if len(entry) > 20:  # Filter out small fragments
                projects.append({
                    'title': 'Project title not extracted',
                    'description': entry[:200] + ('...' if len(entry) > 200 else ''),
                    'technologies': [],
                    'impact': 'Impact not detailed'
                })
    
    return projects


def extract_education(text):
    """
    Extract education details
    """
    education_patterns = [
        r'(Bachelor|Master|PhD|Doctorate|Degree|Diploma|Certificate).*?([A-Z][a-zA-Z\\s]+University|[A-Z][a-zA-Z\\s]+College|[A-Z][a-zA-Z\\s]+Institute)',
        r'([A-Z][a-zA-Z\\s]+University|[A-Z][a-zA-Z\\s]+College|[A-Z][a-zA-Z\\s]+Institute).*?(Bachelor|Master|PhD|Doctorate|Degree|Diploma|Certificate)',
        r'(BS|MS|MBA|PhD|BA|MA).*?([A-Z][a-zA-Z\\s]+University|[A-Z][a-zA-Z\\s]+College|[A-Z][a-zA-Z\\s]+Institute)',
        r'([A-Z][a-zA-Z\\s]+University|[A-Z][a-zA-Z\\s]+College|[A-Z][a-zA-Z\\s]+Institute).*?(BS|MS|MBA|PhD|BA|MA)'
    ]
    
    educations = []
    
    for pattern in education_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            degree = next((item for item in match if any(deg in item.upper() for deg in ['BACHELOR', 'MASTER', 'PHD', 'DOCTORATE', 'DEGREE', 'DIPLOMA', 'CERTIFICATE', 'BS', 'MS', 'MBA', 'BA', 'MA'])), '')
            institution = next((item for item in match if 'university' in item.lower() or 'college' in item.lower() or 'institute' in item.lower()), '')
            
            if degree and institution:
                educations.append({
                    'degree': degree.strip(),
                    'institution': institution.strip(),
                    'field': 'Field not specified',
                    'year': 'Year not specified'
                })
    
    return educations
