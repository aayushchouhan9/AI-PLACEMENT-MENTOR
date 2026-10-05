from sqlalchemy.orm import Session
from app.models import (
    Skill, SkillAlias, RoleArchetype, RoleArchetypeSkill,
    Assessment, AssessmentQuestion
)

INITIAL_SKILLS = [
    # Core CS
    {"name": "Data Structures & Algorithms", "category": "Core CS", "aliases": ["DSA", "Algorithms", "Data Structures"]},
    {"name": "Object-Oriented Programming", "category": "Core CS", "aliases": ["OOP", "OOPs"]},
    {"name": "Database Management Systems", "category": "Core CS", "aliases": ["DBMS", "SQL", "Relational Databases"]},
    {"name": "Operating Systems", "category": "Core CS", "aliases": ["OS", "Linux"]},
    {"name": "Computer Networks", "category": "Core CS", "aliases": ["CN", "Networking", "TCP/IP"]},
    
    # Languages
    {"name": "Python", "category": "Languages", "aliases": ["Py", "Python3"]},
    {"name": "Java", "category": "Languages", "aliases": ["JDK", "Java 8+"]},
    {"name": "JavaScript", "category": "Languages", "aliases": ["JS", "ES6"]},
    {"name": "TypeScript", "category": "Languages", "aliases": ["TS"]},
    {"name": "C++", "category": "Languages", "aliases": ["CPP", "CPlusPlus"]},

    # Frameworks & Libraries
    {"name": "React", "category": "Frameworks", "aliases": ["ReactJS", "React.js"]},
    {"name": "FastAPI", "category": "Frameworks", "aliases": ["FastAPI Python"]},
    {"name": "Node.js", "category": "Frameworks", "aliases": ["Node", "Express.js"]},

    # Tools & Platforms
    {"name": "Git & GitHub", "category": "Tools", "aliases": ["Git", "GitHub", "Version Control"]},
    {"name": "Docker", "category": "Tools", "aliases": ["Containerization", "Docker Compose"]},
    
    # QA & Data
    {"name": "Software Testing & QA", "category": "QA & Data", "aliases": ["QA", "Unit Testing", "Test Automation"]},
    {"name": "Data Analysis & Pandas", "category": "QA & Data", "aliases": ["Pandas", "Data Analytics", "Numpy"]}
]

INITIAL_ROLE_ARCHETYPES = [
    {
        "title": "SDE-1 Backend",
        "description": "Designs, develops, and maintains server-side web APIs, database models, microservices, and system architecture.",
        "typical_experience_level": "Entry-Level / Graduate",
        "skills": [
            {"skill_name": "Data Structures & Algorithms", "is_essential": True, "required_proficiency": 80.0},
            {"skill_name": "Database Management Systems", "is_essential": True, "required_proficiency": 75.0},
            {"skill_name": "Object-Oriented Programming", "is_essential": True, "required_proficiency": 75.0},
            {"skill_name": "Python", "is_essential": True, "required_proficiency": 70.0},
            {"skill_name": "FastAPI", "is_essential": False, "required_proficiency": 60.0},
            {"skill_name": "Git & GitHub", "is_essential": True, "required_proficiency": 70.0},
            {"skill_name": "Docker", "is_essential": False, "required_proficiency": 50.0}
        ]
    },
    {
        "title": "SDE-1 Frontend",
        "description": "Builds responsive, intuitive, and high-performance web interfaces using modern frameworks like React and TypeScript.",
        "typical_experience_level": "Entry-Level / Graduate",
        "skills": [
            {"skill_name": "JavaScript", "is_essential": True, "required_proficiency": 80.0},
            {"skill_name": "React", "is_essential": True, "required_proficiency": 75.0},
            {"skill_name": "TypeScript", "is_essential": False, "required_proficiency": 65.0},
            {"skill_name": "Data Structures & Algorithms", "is_essential": True, "required_proficiency": 65.0},
            {"skill_name": "Git & GitHub", "is_essential": True, "required_proficiency": 70.0}
        ]
    },
    {
        "title": "Full Stack Engineer",
        "description": "Handles both frontend UI development and backend APIs, business logic, and databases.",
        "typical_experience_level": "Entry-Level / Graduate",
        "skills": [
            {"skill_name": "JavaScript", "is_essential": True, "required_proficiency": 75.0},
            {"skill_name": "React", "is_essential": True, "required_proficiency": 70.0},
            {"skill_name": "Python", "is_essential": True, "required_proficiency": 70.0},
            {"skill_name": "Database Management Systems", "is_essential": True, "required_proficiency": 70.0},
            {"skill_name": "Data Structures & Algorithms", "is_essential": True, "required_proficiency": 75.0},
            {"skill_name": "Git & GitHub", "is_essential": True, "required_proficiency": 70.0}
        ]
    },
    {
        "title": "Data Analyst",
        "description": "Analyzes complex datasets, builds metrics/dashboards, writes SQL queries, and derives business insights.",
        "typical_experience_level": "Entry-Level / Graduate",
        "skills": [
            {"skill_name": "Database Management Systems", "is_essential": True, "required_proficiency": 85.0},
            {"skill_name": "Python", "is_essential": True, "required_proficiency": 75.0},
            {"skill_name": "Data Analysis & Pandas", "is_essential": True, "required_proficiency": 80.0},
            {"skill_name": "Git & GitHub", "is_essential": False, "required_proficiency": 50.0}
        ]
    },
    {
        "title": "QA / Automation Engineer",
        "description": "Ensures software quality through manual testing, test case creation, and automated test scripts.",
        "typical_experience_level": "Entry-Level / Graduate",
        "skills": [
            {"skill_name": "Software Testing & QA", "is_essential": True, "required_proficiency": 80.0},
            {"skill_name": "Python", "is_essential": True, "required_proficiency": 65.0},
            {"skill_name": "Database Management Systems", "is_essential": False, "required_proficiency": 60.0},
            {"skill_name": "Git & GitHub", "is_essential": True, "required_proficiency": 60.0}
        ]
    }
]

def seed_database(db: Session):
    # 1. Seed Skills & Aliases
    skill_map = {}
    for sk in INITIAL_SKILLS:
        existing_skill = db.query(Skill).filter(Skill.name == sk["name"]).first()
        if not existing_skill:
            existing_skill = Skill(name=sk["name"], category=sk["category"])
            db.add(existing_skill)
            db.flush()
            for alias in sk.get("aliases", []):
                db.add(SkillAlias(skill_id=existing_skill.id, alias_name=alias))
        skill_map[sk["name"]] = existing_skill

    # 2. Seed Role Archetypes
    for role_data in INITIAL_ROLE_ARCHETYPES:
        existing_role = db.query(RoleArchetype).filter(RoleArchetype.title == role_data["title"]).first()
        if not existing_role:
            existing_role = RoleArchetype(
                title=role_data["title"],
                description=role_data["description"],
                typical_experience_level=role_data["typical_experience_level"]
            )
            db.add(existing_role)
            db.flush()

            for r_skill in role_data["skills"]:
                sk_obj = skill_map.get(r_skill["skill_name"])
                if sk_obj:
                    db.add(RoleArchetypeSkill(
                        role_archetype_id=existing_role.id,
                        skill_id=sk_obj.id,
                        is_essential=r_skill["is_essential"],
                        required_proficiency=r_skill["required_proficiency"]
                    ))

    # 3. Seed Curated Assessment Question Bank
    dsa_skill = skill_map.get("Data Structures & Algorithms")
    if dsa_skill:
        dsa_assessment = db.query(Assessment).filter(Assessment.skill_id == dsa_skill.id).first()
        if not dsa_assessment:
            dsa_assessment = Assessment(
                title="Data Structures & Algorithms Fundamentals",
                description="Core concepts including arrays, hash tables, trees, time complexity, and dynamic programming.",
                skill_id=dsa_skill.id,
                difficulty_tier="intermediate",
                time_limit_minutes=15
            )
            db.add(dsa_assessment)
            db.flush()

            db.add_all([
                AssessmentQuestion(
                    assessment_id=dsa_assessment.id,
                    skill_id=dsa_skill.id,
                    question_text="What is the worst-case time complexity of quicksort algorithm?",
                    question_type="mcq",
                    options=["O(N log N)", "O(N)", "O(N^2)", "O(1)"],
                    correct_answer="O(N^2)",
                    explanation="Quicksort degrades to O(N^2) when the pivot selection consistently picks the smallest or largest element.",
                    points=10
                ),
                AssessmentQuestion(
                    assessment_id=dsa_assessment.id,
                    skill_id=dsa_skill.id,
                    question_text="Which data structure provides O(1) average time complexity for lookups?",
                    question_type="mcq",
                    options=["Binary Search Tree", "Hash Table", "LinkedList", "Array"],
                    correct_answer="Hash Table",
                    explanation="Hash tables use direct indexing via key hashing, providing average O(1) retrieval.",
                    points=10
                ),
                AssessmentQuestion(
                    assessment_id=dsa_assessment.id,
                    skill_id=dsa_skill.id,
                    question_text="Which algorithmic approach uses memoization to avoid redundant subproblem calculations?",
                    question_type="mcq",
                    options=["Greedy Algorithm", "Dynamic Programming", "Divide and Conquer", "Backtracking"],
                    correct_answer="Dynamic Programming",
                    explanation="Dynamic programming optimizes recursive problems by caching intermediate subproblem results.",
                    points=10
                )
            ])

    py_skill = skill_map.get("Python")
    if py_skill:
        py_assessment = db.query(Assessment).filter(Assessment.skill_id == py_skill.id).first()
        if not py_assessment:
            py_assessment = Assessment(
                title="Python Programming & Backend Core",
                description="Assessment covering Python data structures, list comprehensions, decorators, and memory management.",
                skill_id=py_skill.id,
                difficulty_tier="intermediate",
                time_limit_minutes=15
            )
            db.add(py_assessment)
            db.flush()

            db.add_all([
                AssessmentQuestion(
                    assessment_id=py_assessment.id,
                    skill_id=py_skill.id,
                    question_text="What is the output of len(set([1, 2, 2, 3, 4, 4])) in Python?",
                    question_type="mcq",
                    options=["6", "4", "5", "Error"],
                    correct_answer="4",
                    explanation="Sets automatically remove duplicate elements, reducing [1, 2, 2, 3, 4, 4] to {1, 2, 3, 4}.",
                    points=10
                ),
                AssessmentQuestion(
                    assessment_id=py_assessment.id,
                    skill_id=py_skill.id,
                    question_text="How are key-value pairs stored in Python dictionaries for fast lookup?",
                    question_type="mcq",
                    options=["Array", "Hash Table", "Linked List", "Tree"],
                    correct_answer="Hash Table",
                    explanation="Python dictionaries are implemented using underlying hash tables.",
                    points=10
                )
            ])

    # 4. Seed Demo Student for immediate testing and verification
    from app.models import User, StudentProfile, Project, StudentSkill
    from app.core.security import get_password_hash

    demo_email = "demo@placementmentor.com"
    existing_user = db.query(User).filter(User.email == demo_email).first()
    if not existing_user:
        demo_user = User(
            email=demo_email,
            hashed_password=get_password_hash("password123"),
            full_name="Alex Sharma"
        )
        db.add(demo_user)
        db.flush()

        sde_role = db.query(RoleArchetype).filter(RoleArchetype.title == "SDE-1 Backend").first()
        demo_profile = StudentProfile(
            user_id=demo_user.id,
            branch="Computer Science & Engineering",
            graduation_year=2026,
            target_role_id=sde_role.id if sde_role else None
        )
        db.add(demo_profile)

        # Sample structured project
        p1 = Project(
            user_id=demo_user.id,
            name="Distributed Task Scheduler",
            one_line_summary="High-throughput distributed task queue system using Redis and FastAPI",
            role="Backend Engineer",
            tech_stack=["Python", "FastAPI", "Docker", "Database Management Systems"],
            architectural_decisions="Used async FastAPI workers with Redis queue for decoupled job execution.",
            challenges_faced="Handling worker crash recovery without job loss.",
            tradeoffs_made="Prioritized at-least-once message delivery over strict FIFO ordering."
        )
        db.add(p1)

        # Sample student skills
        skill_tuples = [
            ("Data Structures & Algorithms", 75.0),
            ("Python", 80.0),
            ("Database Management Systems", 70.0),
            ("Git & GitHub", 75.0)
        ]
        for sk_name, prof in skill_tuples:
            sk_obj = skill_map.get(sk_name)
            if sk_obj:
                db.add(StudentSkill(
                    user_id=demo_user.id,
                    skill_id=sk_obj.id,
                    proficiency=prof,
                    confidence=0.85,
                    source="assessment_verified"
                ))

    db.commit()
    print("Database seeding completed successfully.")

