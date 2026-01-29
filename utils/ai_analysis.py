import google.generativeai as genai
import streamlit as st
import re

def initialize_ai():
    """Initialize AI API with error handling."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        # Using a generic check for "demo_mode" or similar if needed
        if api_key and api_key != "demo_mode":
            genai.configure(api_key=api_key)
            return True
        return False
    except Exception:
        return False

def analyze_resume(resume_text, job_category):
    """
    Analyze resume using AI model with a detailed prompt.
    Returns the analysis text or None if failed.
    """
    # First, extract structured data from the resume
    from utils.pdf_processor import extract_structured_data
    structured_data = extract_structured_data(resume_text)
    
    prompt = f"""
    ACT as a Senior Certified Professional Resume Writer (CPRW) with 15+ years of experience and a former hiring manager.
    
    **RESUME TO ANALYZE:**
    {resume_text}
    
    **STRUCTURED DATA EXTRACTED:**
    Skills: {structured_data['skills']}
    Experience: {structured_data['experience']}
    Projects: {structured_data['projects']}
    Education: {structured_data['education']}
    
    **TARGET ROLE:** {job_category}
    
    Provide a comprehensive analysis in this EXACT format:
    
    ## 📊 QUICK SUMMARY (TL;DR)
    - 5 bullet points highlighting the most critical findings
    
    ## 💯 RESUME SCORE & BREAKDOWN
    Overall Score: X/100
    - Role Alignment: X/25
    - Impact Clarity: X/25
    - ATS Friendliness: X/25
    - Project Relevance: X/25
    
    ## 🎯 ROLE FIT ANALYSIS
    How well does this resume align with {job_category}?
    
    ## 🧩 SKILL GAP MATRIX
    | Skill Category | Strong Match | Partial Match | Missing But Important |
    |----------------|--------------|---------------|----------------------|
    | Technical Skills | ... | ... | ... |
    | Tools & Technologies | ... | ... | ... |
    | Soft Skills | ... | ... | ... |
    
    ## 🔍 HIRING MANAGER SIMULATION
    Simulate how a real recruiter would read this resume in 30 seconds:
    - First impression summary
    - What stands out
    - What raises doubts
    - Likely shortlist decision (Yes / Maybe / No + reason)
    
    ## ⚠️ RESUME RISK DETECTION
    Identify potential red flags:
    - Skill dumping
    - Buzzwords without proof
    - Too many technologies for experience level
    - Inconsistent timelines
    
    ## 🛠️ IMPROVEMENT ACTIONS (PRIORITIZED)
    1. Most impactful change
    2. Second most important
    3. Third priority improvement
    
    ## ✏️ EXAMPLE REWRITES
    Rewrite one weak experience bullet → strong, impact-driven version
    Rewrite one weak project description → problem-solution-result format
    Explain why the rewritten version is better.
    
    Be extremely specific, direct, and provide exact phrasing suggestions where needed.
    """
    
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key or api_key == "demo_mode":
            return None

        # Assuming we are using a specific model family
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Fail silently to allow fallback to mock_analysis
        print(f"AI Analysis failed: {e}") 
        return None

def calculate_resume_score(structured_data, job_category):
    """
    Calculate a Resume Strength Score (0-100) based on:
    - Role alignment
    - Impact clarity (metrics, results)
    - ATS friendliness
    - Project relevance
    """
    score_components = {
        'role_alignment': 0,
        'impact_clarity': 0,
        'ats_friendly': 0,
        'project_relevance': 0
    }
    
    # Role alignment score (25 points max)
    job_keywords = get_job_keywords(job_category)
    skills = structured_data['skills']
    
    tech_match_count = 0
    for tech_skill in skills['technical']:
        if tech_skill.lower() in job_keywords:
            tech_match_count += 1
    
    # Calculate percentage match
    if job_keywords:
        role_alignment_score = min(25, (tech_match_count / len(job_keywords)) * 25)
    else:
        role_alignment_score = 10  # Default score if we can't determine keywords
    score_components['role_alignment'] = round(role_alignment_score)
    
    # Impact clarity score (25 points max)
    raw_text = structured_data['raw_text']
    # Look for numbers and metrics in the resume
    metric_patterns = [r'\d+%', r'\$?\d+,?\d+', r'\d+\s*(million|thousand|hundred)', r'#\d+', r'top\s*\d+']
    metrics_found = 0
    for pattern in metric_patterns:
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        metrics_found += len(matches)
    
    impact_score = min(25, metrics_found * 5)  # Up to 5 metrics * 5 points each
    score_components['impact_clarity'] = impact_score
    
    # ATS friendliness score (25 points max)
    # Check for common ATS issues
    ats_issues = 0
    
    # Check for proper section headers
    sections_present = 0
    for section in ['experience', 'skills', 'education', 'projects']:
        if structured_data['sections'].get(section):
            sections_present += 1
    
    # Check for contact info
    contact_info = structured_data['contact_info']
    if contact_info.get('email') or contact_info.get('phone'):
        sections_present += 1
    
    ats_score = min(25, (sections_present / 5) * 25)
    score_components['ats_friendly'] = round(ats_score)
    
    # Project relevance score (25 points max)
    projects = structured_data['projects']
    project_score = min(25, len(projects) * 8)  # Up to 3 projects * 8 points each
    score_components['project_relevance'] = min(25, project_score)
    
    # Calculate total score
    total_score = sum(score_components.values())
    
    return total_score, score_components


def get_job_keywords(job_category):
    """
    Return relevant keywords for a given job category
    """
    keyword_mapping = {
        'Software Engineer': ['python', 'java', 'javascript', 'react', 'angular', 'node.js', 'sql', 'git', 'agile', 'oop', 'algorithms', 'data structures'],
        'Data Scientist': ['python', 'r', 'sql', 'machine learning', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'statistics', 'data analysis', 'matplotlib', 'jupyter'],
        'Product Manager': ['product strategy', 'roadmap', 'agile', 'scrum', 'stakeholder', 'requirements', 'ux', 'analytics', 'market research', 'feature prioritization'],
        'Full Stack Developer': ['javascript', 'react', 'node.js', 'express', 'html', 'css', 'sql', 'rest', 'api', 'database', 'frontend', 'backend'],
        'DevOps Engineer': ['docker', 'kubernetes', 'aws', 'azure', 'ci/cd', 'jenkins', 'terraform', 'linux', 'bash', 'monitoring', 'infrastructure'],
        'Machine Learning Engineer': ['python', 'tensorflow', 'pytorch', 'deep learning', 'neural networks', 'data preprocessing', 'model deployment', 'computer vision', 'nlp'],
        'Frontend Developer': ['javascript', 'react', 'angular', 'vue', 'html', 'css', 'typescript', 'redux', 'webpack', 'responsive design', 'css frameworks'],
        'Backend Developer': ['python', 'java', 'node.js', 'express', 'sql', 'nosql', 'api', 'microservices', 'database', 'authentication', 'security'],
        'UX Designer': ['ui/ux', 'wireframing', 'prototyping', 'user research', 'usability', 'design systems', 'figma', 'sketch', 'user flows', 'interaction design'],
        'Cybersecurity Specialist': ['security', 'network security', 'penetration testing', 'risk assessment', 'encryption', 'firewalls', 'siem', 'incident response', 'vulnerability'],
        'Data Analyst': ['sql', 'excel', 'tableau', 'power bi', 'python', 'r', 'data visualization', 'statistical analysis', 'reporting', 'dashboards']
    }
    
    return keyword_mapping.get(job_category, [])


def simulate_hiring_manager_review(structured_data, job_category):
    """
    Simulate how a real recruiter would read this resume in 30 seconds
    """
    # Extract key information
    skills = structured_data['skills']
    experience = structured_data['experience']
    projects = structured_data['projects']
    education = structured_data['education']
    raw_text = structured_data['raw_text']
    
    # Simulate quick review
    first_impression = []
    standout_items = []
    concerns = []
    decision_reasoning = []
    
    # First impression
    if skills['technical']:
        first_impression.append(f"Has some technical skills: {', '.join(skills['technical'][:3])}")
    else:
        first_impression.append("Limited technical skills visible")
        
    if experience:
        first_impression.append(f"Has {len(experience)} role(s) of experience")
    else:
        first_impression.append("Limited work experience shown")
    
    # What stands out
    if len(skills['technical']) > 3:
        standout_items.append(f"Impressive technical breadth: {', '.join(skills['technical'][:3])}")
    elif skills['technical']:
        standout_items.append(f"Relevant technical skills: {', '.join(skills['technical'][:2])}")
    
    if len(experience) > 2:
        standout_items.append(f"Solid experience with {len(experience)} positions")
    
    # Concerns
    if not any(metric in raw_text.lower() for metric in ['%', '$', 'users', 'customers', 'increase', 'decrease', 'improve', 'reduce']):
        concerns.append("No quantifiable metrics or achievements")
    
    if len(skills['technical']) > 8 and len(experience) < 2:
        concerns.append("Many skills but limited experience - seems unrealistic")
    
    if not projects:
        concerns.append("No projects to demonstrate practical application")
    
    # Decision reasoning
    score = len(standout_items) - len(concerns)
    
    if score > 1:
        decision = "YES - Worth a closer look"
        decision_reasoning.append("Positive indicators outweigh concerns")
    elif score == 1 or score == 0:
        decision = "MAYBE - Needs improvement but potential"
        decision_reasoning.append("Mixed signals, could be viable with improvements")
    else:
        decision = "NO - Significant improvements needed"
        decision_reasoning.append("Concerns outweigh positive aspects")
    
    return {
        'first_impression': first_impression,
        'stands_out': standout_items,
        'raises_doubts': concerns,
        'decision': decision,
        'reasoning': decision_reasoning
    }


def suggest_rewrite_with_intent(raw_text, job_category):
    """
    Suggest rewrites for weak experience bullets and project descriptions
    """
    # Find potential weak experience bullets (ones without numbers or impact)
    experience_bullets = []
    project_descriptions = []
    
    # Look for common phrases that indicate weak bullets
    weak_expressions = [
        r'worked on',
        r'was responsible for',
        r'helped with',
        r'part of',
        r'did',
        r'made',
        r'created',
        r'used',
        r'implemented',
        r'developed'
    ]
    
    # Extract potential experience bullets from raw text
    lines = raw_text.split('\n')
    for line in lines:
        line_lower = line.lower().strip()
        if any(re.search(pattern, line_lower) for pattern in weak_expressions):
            if len(line) > 10 and len(line) < 200:  # Reasonable length for a bullet
                experience_bullets.append(line.strip())
    
    # If we couldn't find any obvious weak bullets, just pick a few lines that look like experience bullets
    if not experience_bullets:
        for line in lines:
            line_clean = line.strip()
            if (line_clean.startswith('- ') or line_clean.startswith('* ') or 
                line_clean.startswith('• ') or line_clean.startswith('◦ ')) and len(line_clean) > 15:
                experience_bullets.append(line_clean)
    
    # Extract potential project descriptions
    # Look for project-like sections in the raw text
    project_section_start = -1
    for i, line in enumerate(lines):
        if any(word in line.lower() for word in ['project', 'portfolio', 'case study']):
            project_section_start = i
            break
    
    if project_section_start != -1:
        # Extract next few lines as potential project descriptions
        for i in range(project_section_start + 1, min(project_section_start + 6, len(lines))):
            line = lines[i].strip()
            if line and len(line) > 20:
                project_descriptions.append(line)
    
    # Prepare rewrite suggestions
    rewrites = {
        'experience_bullet': None,
        'project_description': None
    }
    
    # Suggest a rewrite for an experience bullet if we found one
    if experience_bullets:
        original_bullet = experience_bullets[0]
        
        # Create a stronger, impact-driven version
        # This is a simplified approach - in practice, you'd want more sophisticated NLP
        improved_bullet = create_impact_driven_bullet(original_bullet, job_category)
        
        rewrites['experience_bullet'] = {
            'original': original_bullet,
            'improved': improved_bullet,
            'explanation': 'The improved version uses strong action verbs, adds quantifiable impact, and relates directly to the target role.'
        }
    
    # Suggest a rewrite for a project description if we found one
    if project_descriptions:
        original_project = project_descriptions[0]
        
        # Create a problem-solution-result format
        improved_project = create_problem_solution_result_format(original_project)
        
        rewrites['project_description'] = {
            'original': original_project,
            'improved': improved_project,
            'explanation': 'The improved version follows the problem-solution-result format, which clearly demonstrates impact and outcomes.'
        }
    
    return rewrites


def create_impact_driven_bullet(original, job_category):
    """
    Create an impact-driven bullet point from a weaker one
    """
    # Map job categories to strong action verbs
    action_verbs = {
        'Software Engineer': ['Developed', 'Implemented', 'Engineered', 'Built', 'Optimized', 'Designed'],
        'Data Scientist': ['Analyzed', 'Built', 'Developed', 'Created', 'Implemented', 'Modeled'],
        'Product Manager': ['Led', 'Managed', 'Defined', 'Delivered', 'Prioritized', 'Spearheaded'],
        'Full Stack Developer': ['Developed', 'Integrated', 'Built', 'Implemented', 'Optimized', 'Architected'],
        'DevOps Engineer': ['Automated', 'Deployed', 'Configured', 'Optimized', 'Maintained', 'Secured'],
        'Machine Learning Engineer': ['Developed', 'Trained', 'Implemented', 'Optimized', 'Evaluated', 'Deployed'],
        'Frontend Developer': ['Built', 'Designed', 'Implemented', 'Optimized', 'Developed', 'Architected'],
        'Backend Developer': ['Built', 'Designed', 'Implemented', 'Optimized', 'Developed', 'Architected'],
        'UX Designer': ['Designed', 'Prototyped', 'Conducted', 'Improved', 'Created', 'Iterated'],
        'Cybersecurity Specialist': ['Secured', 'Monitored', 'Assessed', 'Implemented', 'Audited', 'Mitigated'],
        'Data Analyst': ['Analyzed', 'Visualized', 'Reported', 'Identified', 'Processed', 'Modeled']
    }
    
    verbs = action_verbs.get(job_category, ['Developed', 'Implemented', 'Built', 'Optimized'])
    
    # Simple transformation - in practice, you'd want more nuanced NLP
    original_lower = original.lower()
    
    # Remove weak starting phrases
    improved = original
    weak_starts = ['worked on', 'was responsible for', 'helped with', 'part of', 'did', 'made']
    
    for weak_start in weak_starts:
        if original_lower.startswith(weak_start):
            # Replace with a strong action verb
            improved = f"{verbs[0]} {original[len(weak_start)+1:].strip()}"
            break
    
    # Add impact if possible (simple approach)
    if 'improved' not in improved.lower() and 'increased' not in improved.lower():
        # Add a placeholder for metrics
        if 'application' in improved.lower() or 'system' in improved.lower() or 'software' in improved.lower():
            improved += ', resulting in improved performance and user satisfaction'
    
    # Ensure it starts with a strong action verb
    if not any(improved.startswith(verb) for verb in verbs):
        improved = f"{verbs[0]} {improved[0].lower() + improved[1:] if len(improved) > 1 else improved}"
    
    return improved


def create_problem_solution_result_format(original):
    """
    Transform a project description into problem-solution-result format
    """
    # Simple transformation - in practice, you'd want more sophisticated NLP
    # For now, we'll create a template example
    
    # Identify if the original has elements that could be classified
    parts = original.split('. ')
    
    # Create a problem-solution-result structure
    problem = f"Problem: Identified an opportunity to improve [specific challenge] in [context]."
    solution = f"Solution: Designed and implemented [approach/technology/solution] to address the challenge."
    result = f"Result: Achieved [quantifiable outcome] and [business impact]."
    
    return f"{problem} {solution} {result}"


def detect_resume_risks(structured_data):
    """
    Detect red flags in the resume:
    - Skill dumping
    - Buzzwords without proof
    - Too many technologies for experience level
    - Inconsistent timelines
    """
    risks = []
    
    skills = structured_data['skills']
    experience = structured_data['experience']
    raw_text = structured_data['raw_text']
    
    # Risk 1: Skill dumping - too many skills listed without evidence
    total_skills = len(skills['technical']) + len(skills['tools']) + len(skills['soft_skills'])
    if total_skills > 15 and len(experience) < 2:
        risks.append({
            'type': 'Skill Dumping',
            'description': f'Listed {total_skills} skills but only has {len(experience)} experience entries - appears to be skill dumping without evidence of use.',
            'severity': 'high'
        })
    
    # Risk 2: Buzzwords without proof
    buzzwords = ['synergize', 'paradigm', 'disruptive', 'cutting-edge', 'innovative', 'proactive', 'dynamic', 'robust', 'scalable', 'agile']
    buzzword_count = 0
    for buzzword in buzzwords:
        if buzzword.lower() in raw_text.lower():
            buzzword_count += 1
    
    if buzzword_count > 3:
        risks.append({
            'type': 'Buzzword Overload',
            'description': f'Detected {buzzword_count} buzzwords ({", ".join([bw for bw in buzzwords if bw in raw_text.lower()][:5])}) - lacks specific, concrete examples.',
            'severity': 'medium'
        })
    
    # Risk 3: Too many technologies for experience level
    if len(skills['technical']) > 10 and len(experience) < 2:
        risks.append({
            'type': 'Unrealistic Tech Breadth',
            'description': f'Lists {len(skills["technical"])} technical skills but has limited work experience - difficult to gain proficiency in all these technologies.',
            'severity': 'high'
        })
    
    # Risk 4: Inconsistent timelines (basic check)
    # Look for date patterns in the text
    import re
    date_patterns = [r'\b\d{4}\b', r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b', r'\b\d{1,2}/\d{4}\b']
    dates_found = []
    
    for pattern in date_patterns:
        matches = re.findall(pattern, raw_text)
        dates_found.extend(matches)
    
    # Convert to actual years for basic timeline validation
    years = []
    for date in dates_found:
        year_match = re.search(r'\b(19|20)\d{2}\b', str(date))
        if year_match:
            years.append(int(year_match.group()))
    
    if years:
        min_year = min(years)
        max_year = max(years)
        
        # Check if there are gaps or impossible timelines
        if max_year > 2026:  # Future dates
            risks.append({
                'type': 'Invalid Timeline',
                'description': f'Found future dates ({max_year}) in resume.',
                'severity': 'high'
            })
        elif min_year < 1980:  # Unlikely early dates
            risks.append({
                'type': 'Timeline Concern',
                'description': f'Found very early dates ({min_year}), possibly indicating inaccurate timeline.',
                'severity': 'medium'
            })
    
    # Risk 5: Grammatical errors or typos
    # Basic check for repeated characters (possible typos)
    typo_indicators = re.findall(r'\b(\w)\1{2,}\b', raw_text)  # Triple letters like 'booook'
    if len(typo_indicators) > 2:
        risks.append({
            'type': 'Possible Typos',
            'description': f'Detected {len(typo_indicators)} potential typos (words with repeated letters).',
            'severity': 'medium'
        })
    
    # Risk 6: Formatting issues
    if '\t' not in raw_text and '\n\n' not in raw_text:
        risks.append({
            'type': 'Poor Formatting',
            'description': 'Resume appears to have poor formatting with insufficient spacing.',
            'severity': 'low'
        })
    
    return risks


def mock_analysis(resume_text, job_category):
    """
    Mock analysis for testing purposes or when API is unavailable.
    """
    # First, extract structured data from the resume
    from utils.pdf_processor import extract_structured_data
    structured_data = extract_structured_data(resume_text)
    
    # Calculate resume score
    total_score, score_components = calculate_resume_score(structured_data, job_category)
    
    return f"""
## 📊 QUICK SUMMARY (TL;DR)
- Resume shows basic technical skills relevant to {job_category}
- Lacks quantifiable achievements and metrics
- Good structure but could improve with more impact-focused descriptions
- Needs more specific keywords for {job_category} role
- Contact information should be more prominent

## 💯 RESUME SCORE & BREAKDOWN
Overall Score: {total_score}/100
- Role Alignment: {score_components['role_alignment']}/25
- Impact Clarity: {score_components['impact_clarity']}/25
- ATS Friendliness: {score_components['ats_friendly']}/25
- Project Relevance: {score_components['project_relevance']}/25

## 🎯 ROLE FIT ANALYSIS
The resume shows foundational skills for {job_category} but needs strengthening in key areas:
- More specific examples of relevant work
- Quantified achievements with metrics
- Better alignment with {job_category} requirements

## 🧩 SKILL GAP MATRIX
| Skill Category | Strong Match | Partial Match | Missing But Important |
|----------------|--------------|---------------|----------------------|
| Technical Skills | {', '.join(structured_data['skills']['technical'][:2]) if structured_data['skills']['technical'] else 'None'} | {', '.join(structured_data['skills']['technical'][2:4]) if len(structured_data['skills']['technical']) > 2 else 'Few'} | {', '.join(get_job_keywords(job_category)[:3]) if get_job_keywords(job_category) else 'Various'} |
| Tools & Technologies | {', '.join(structured_data['skills']['tools'][:2]) if structured_data['skills']['tools'] else 'None'} | {', '.join(structured_data['skills']['tools'][2:4]) if len(structured_data['skills']['tools']) > 2 else 'Few'} | Various industry tools |
| Soft Skills | {', '.join(structured_data['skills']['soft_skills'][:2]) if structured_data['skills']['soft_skills'] else 'None'} | {', '.join(structured_data['skills']['soft_skills'][2:4]) if len(structured_data['skills']['soft_skills']) > 2 else 'Few'} | Leadership, communication skills |

## 🔍 HIRING MANAGER SIMULATION
Simulating a 30-second review by a hiring manager:
- First impression: Resume has basic structure and relevant skills
- What stands out: Some technical competencies shown
- What raises doubts: Lack of specific achievements and metrics
- Shortlist decision: MAYBE - needs improvement before serious consideration

## ⚠️ RESUME RISK DETECTION
Potential red flags identified:
- Limited quantifiable achievements
- Generic language without specific impact
- Could have more relevant keywords for {job_category}
- Experience descriptions lack specific metrics

## 🛠️ IMPROVEMENT ACTIONS (PRIORITIZED)
1. Add 3-5 quantifiable achievements with specific metrics
2. Include more keywords relevant to {job_category}
3. Strengthen experience descriptions with impact-focused language

## ✏️ EXAMPLE REWRITES
**Before:** Worked on software development projects using various technologies.
**After:** Developed and deployed 3 web applications using React and Node.js, resulting in 25% increase in user engagement.
**Why better:** Contains specific technologies, quantifiable result, and impact statement.

**Before:** Part of team that built a mobile app.
**After:** Collaborated with cross-functional team to architect and develop a mobile application serving 10K+ users, improving customer satisfaction by 40%.
**Why better:** Specifies team collaboration, user impact, and measurable outcome.
"""
