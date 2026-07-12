from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from academics.models import Department, Student, Teacher

User = get_user_model()

DEFAULT_PASSWORD = "password123"
DEFAULT_COUNT = 50
DEFAULT_DEPARTMENT_COUNT = 10

ENGINEERING_DEPARTMENTS = [
    "Computer Science and Engineering",
    "Information Technology",
    "Electronics and Communication Engineering",
    "Electrical and Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Aerospace Engineering",
    "Biotechnology",
    "Agricultural Engineering",
    "Automobile Engineering",
    "Biomedical Engineering",
    "Industrial Engineering",
    "Instrumentation Engineering",
    "Marine Engineering",
    "Metallurgical Engineering",
    "Mining Engineering",
    "Petroleum Engineering",
    "Production Engineering",
    "Textile Engineering",
    "Environmental Engineering",
    "Food Technology",
    "Robotics Engineering",
    "Artificial Intelligence and Machine Learning",
    "Data Science",
    "Cyber Security",
    "Internet of Things",
    "Cloud Computing",
    "Software Engineering",
    "Structural Engineering",
    "Geotechnical Engineering",
    "Transportation Engineering",
    "Water Resources Engineering",
    "Power Systems Engineering",
    "Control Systems Engineering",
    "VLSI Design",
    "Embedded Systems",
    "Nanotechnology",
    "Renewable Energy Engineering",
    "Nuclear Engineering",
    "Materials Science and Engineering",
    "Polymer Engineering",
    "Ceramic Engineering",
    "Mechatronics Engineering",
    "Mining Machinery Engineering",
    "Naval Architecture",
    "Fire and Safety Engineering",
    "Construction Engineering",
    "Telecommunication Engineering",
    "Energy Engineering",
    "Agricultural and Food Engineering",
    "Mining and Mineral Engineering",
    "Computer Engineering",
    "Electronics Engineering",
    "Electrical Engineering",
    "Applied Electronics and Instrumentation",
    "Engineering Physics",
    "Engineering Chemistry",
    "Engineering Mathematics",
    "Geoinformatics Engineering",
    "Smart Manufacturing",
    "Additive Manufacturing",
    "Quantum Computing",
    "5G and Wireless Communication",
    "Automotive Electronics",
    "Thermal Engineering",
    "Fluid Mechanics and Machinery",
    "Design Engineering",
    "Manufacturing Engineering",
    "Hydraulics Engineering",
    "Surveying and Geomatics",
    "Urban Planning Engineering",
    "Railway Engineering",
    "Highway Engineering",
    "Bridge Engineering",
    "Earthquake Engineering",
    "Coastal Engineering",
    "Irrigation Engineering",
    "Sanitary Engineering",
    "Refrigeration and Air Conditioning",
    "Process Engineering",
    "Pharmaceutical Engineering",
    "Leather Technology",
    "Pulp and Paper Technology",
    "Sugar Technology",
    "Dairy Technology",
    "Ceramic and Cement Technology",
    "Surface Coating Technology",
    "Plastic and Polymer Technology",
    "Printing Technology",
    "Packaging Technology",
    "Optical Engineering",
    "Acoustical Engineering",
    "Biochemical Engineering",
    "Genetic Engineering",
    "Agricultural Biotechnology",
    "Marine Biotechnology",
    "Space Technology",
    "Defense Technology",
    "Railway Signaling Engineering",
    "Smart Grid Technology",
    "Electric Vehicle Technology",
    "Battery Technology",
    "Semiconductor Technology",
    "Photonics Engineering",
    "Microelectronics Engineering",
    "RF and Microwave Engineering",
    "Satellite Communication Engineering",
    "Avionics Engineering",
    "Aircraft Maintenance Engineering",
    "Helicopter Engineering",
    "Unmanned Aerial Systems Engineering",
    "Underwater Robotics",
    "Industrial IoT",
    "Digital Twin Engineering",
    "Sustainable Engineering",
    "Green Building Technology",
    "Waste Management Engineering",
    "Water Treatment Engineering",
    "Air Pollution Control Engineering",
    "Noise Control Engineering",
    "HVAC Engineering",
    "Building Services Engineering",
    "Facilities Engineering",
    "Maintenance Engineering",
    "Reliability Engineering",
    "Safety Engineering",
    "Quality Engineering",
    "Operations Research",
    "Supply Chain Engineering",
    "Logistics Engineering",
    "Warehouse Automation",
    "Factory Automation",
    "Process Automation",
    "Instrumentation and Control",
    "Biomedical Instrumentation",
    "Clinical Engineering",
    "Prosthetics Engineering",
    "Rehabilitation Engineering",
    "Sports Engineering",
    "Entertainment Engineering",
    "Game Development Engineering",
    "AR and VR Engineering",
    "Human-Computer Interaction",
    "Computational Linguistics",
    "Bioinformatics",
    "Computational Biology",
    "Computational Fluid Dynamics",
    "Finite Element Analysis",
    "Simulation Engineering",
    "Digital Signal Processing",
    "Image Processing",
    "Computer Vision",
    "Natural Language Processing",
    "Knowledge Engineering",
    "Expert Systems",
    "Fuzzy Logic Engineering",
    "Neural Networks Engineering",
    "Deep Learning Engineering",
    "Edge Computing",
    "Fog Computing",
    "Distributed Systems Engineering",
    "High Performance Computing",
    "Grid Computing",
    "Parallel Computing",
    "Quantum Information Engineering",
    "Cryptography Engineering",
    "Blockchain Engineering",
    "FinTech Engineering",
    "Health Informatics",
    "Medical Imaging Engineering",
    "Telemedicine Engineering",
    "Assistive Technology",
    "Wearable Technology",
    "Sensor Technology",
    "MEMS Engineering",
    "NEMS Engineering",
    "Thin Film Technology",
    "Surface Engineering",
    "Corrosion Engineering",
    "Welding Engineering",
    "Foundry Technology",
    "Heat Treatment Technology",
    "Powder Metallurgy",
    "Composite Materials Engineering",
    "Smart Materials Engineering",
    "Shape Memory Alloys",
    "Piezoelectric Engineering",
    "Magnetics Engineering",
    "Superconductivity Engineering",
    "Plasma Engineering",
    "Laser Technology",
    "Optoelectronics",
    "Fiber Optics Engineering",
    "Antenna Engineering",
    "Radar Engineering",
    "Sonar Engineering",
    "Navigation Engineering",
    "Guidance and Control",
    "Flight Dynamics",
    "Orbital Mechanics",
    "Rocket Propulsion",
    "Combustion Engineering",
    "Turbomachinery",
    "Gas Dynamics",
    "Aerodynamics",
    "Hydrodynamics",
    "Ocean Engineering",
    "Offshore Engineering",
    "Pipeline Engineering",
    "Reservoir Engineering",
    "Drilling Engineering",
    "Production Technology",
    "Enhanced Oil Recovery",
    "Coal Technology",
    "Solar Energy Engineering",
    "Wind Energy Engineering",
    "Hydroelectric Engineering",
    "Geothermal Engineering",
    "Biomass Energy Engineering",
    "Hydrogen Energy Engineering",
    "Fuel Cell Technology",
    "Energy Storage Systems",
    "Power Electronics",
    "Electric Drives",
    "High Voltage Engineering",
    "Protection and Switchgear",
    "Substation Engineering",
    "Transmission Engineering",
    "Distribution Engineering",
    "Microgrid Engineering",
    "Energy Management Systems",
    "Building Energy Systems",
    "Industrial Energy Systems",
    "Carbon Capture Engineering",
    "Climate Engineering",
    "Disaster Management Engineering",
    "Forensic Engineering",
    "Reverse Engineering",
    "Value Engineering",
    "Systems Engineering",
    "Software Defined Networking",
    "Network Security Engineering",
    "Information Security",
    "Digital Forensics",
    "Ethical Hacking",
    "Penetration Testing",
    "Malware Analysis",
    "Incident Response Engineering",
    "DevOps Engineering",
    "Site Reliability Engineering",
    "Platform Engineering",
    "API Engineering",
    "Microservices Engineering",
    "Container Technology",
    "Kubernetes Engineering",
    "Serverless Computing",
    "Data Engineering",
    "Big Data Analytics",
    "Business Intelligence",
    "Data Warehousing",
    "ETL Engineering",
    "Database Engineering",
    "Search Engine Technology",
    "Recommendation Systems",
    "Information Retrieval",
    "Web Engineering",
    "Mobile Application Engineering",
    "Cross-Platform Development",
    "UI/UX Engineering",
    "Accessibility Engineering",
    "Localization Engineering",
    "Technical Writing Engineering",
    "Documentation Engineering",
    "Test Automation Engineering",
    "Performance Engineering",
    "Load Testing Engineering",
    "Chaos Engineering",
    "Observability Engineering",
    "Monitoring Engineering",
    "Logging Engineering",
    "Tracing Engineering",
    "Alerting Engineering",
    "Incident Management",
    "Change Management Engineering",
    "Configuration Management",
    "Release Engineering",
    "Build Engineering",
    "Compiler Engineering",
    "Interpreter Engineering",
    "Virtual Machine Technology",
    "Operating Systems Engineering",
    "Kernel Development",
    "Device Driver Development",
    "Firmware Engineering",
    "BIOS Engineering",
    "Bootloader Engineering",
    "Real-Time Systems",
    "RTOS Engineering",
    "Bare Metal Programming",
    "Low-Level Programming",
    "Assembly Language Engineering",
    "Hardware Description Languages",
    "FPGA Engineering",
    "ASIC Design",
    "SoC Design",
    "Chip Design",
    "Wafer Fabrication",
    "Semiconductor Manufacturing",
    "Clean Room Technology",
    "Yield Engineering",
    "Test Engineering",
    "Failure Analysis",
    "Root Cause Analysis",
    "Six Sigma Engineering",
    "Lean Manufacturing",
    "Kaizen Engineering",
    "Total Quality Management",
    "Statistical Process Control",
    "Design of Experiments",
    "Taguchi Methods",
    "Robust Design",
    "Concurrent Engineering",
    "Collaborative Engineering",
    "Agile Engineering",
    "Scrum Engineering",
    "Kanban Engineering",
    "Project Management Engineering",
    "Program Management",
    "Portfolio Management",
    "Risk Management Engineering",
    "Cost Engineering",
    "Estimation Engineering",
    "Scheduling Engineering",
    "Resource Planning",
    "Capacity Planning",
    "Demand Forecasting",
    "Inventory Management",
    "Procurement Engineering",
    "Vendor Management",
    "Contract Management",
    "Legal Engineering",
    "Patent Engineering",
    "Intellectual Property",
    "Technology Transfer",
    "Innovation Management",
    "R&D Engineering",
    "Product Development",
    "Prototype Engineering",
    "Pilot Plant Engineering",
    "Scale-Up Engineering",
    "Technology Commercialization",
    "Startup Engineering",
    "Venture Engineering",
    "Entrepreneurship in Engineering",
    "Engineering Economics",
    "Engineering Management",
    "Engineering Leadership",
    "Engineering Ethics",
    "Professional Engineering Practice",
    "Continuing Education in Engineering",
    "Lifelong Learning in Engineering",
]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Shaurya", "Atharv", "Advik", "Pranav", "Advaith", "Dhruv",
    "Kabir", "Ritvik", "Aarush", "Kian", "Ananya", "Aadhya", "Diya", "Myra",
    "Sara", "Ira", "Pari", "Anika", "Navya", "Kiara", "Riya", "Aanya",
    "Prisha", "Avni", "Saanvi", "Ishita", "Kavya", "Tara", "Zara", "Meera",
    "Rohan", "Karan", "Nikhil", "Varun", "Rahul", "Amit", "Suresh", "Rajesh",
    "Priya", "Neha", "Pooja", "Sneha", "Divya", "Lakshmi", "Meena", "Kavita",
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Reddy", "Nair",
    "Iyer", "Menon", "Joshi", "Desai", "Shah", "Mehta", "Rao", "Pillai",
    "Chatterjee", "Banerjee", "Mukherjee", "Das", "Bose", "Ghosh", "Kapoor",
    "Malhotra", "Chopra", "Saxena", "Agarwal", "Bansal", "Khanna", "Sethi",
    "Pandey", "Mishra", "Tiwari", "Yadav", "Dubey", "Srivastava", "Jain",
    "Kulkarni", "Patil", "Naik", "Kamat", "Hegde", "Shetty", "Gowda", "Murthy",
    "Swamy", "Ranganathan", "Krishnan", "Subramanian", "Venkatesh", "Balaji",
]


class Command(BaseCommand):
    help = "Seed the database with engineering college sample data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=DEFAULT_COUNT,
            help=f"Number of teachers and students to create (default: {DEFAULT_COUNT}).",
        )
        parser.add_argument(
            "--departments",
            type=int,
            default=DEFAULT_DEPARTMENT_COUNT,
            help=f"Number of departments to create (default: {DEFAULT_DEPARTMENT_COUNT}).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing seed data before creating new records.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        department_count = options["departments"]
        if count < 1:
            self.stderr.write(self.style.ERROR("--count must be at least 1."))
            return
        if department_count < 1:
            self.stderr.write(self.style.ERROR("--departments must be at least 1."))
            return

        if department_count > len(ENGINEERING_DEPARTMENTS):
            self.stderr.write(
                self.style.ERROR(
                    f"Only {len(ENGINEERING_DEPARTMENTS)} engineering departments are available."
                )
            )
            return

        if options["clear"]:
            self._clear_data()

        if Department.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Data already exists. Use --clear to replace it."
                )
            )
            self._print_counts()
            return

        with transaction.atomic():
            departments = self._create_departments(department_count)
            teachers = self._create_teachers(count)
            self._assign_hods(departments, teachers)
            self._create_students(count, departments)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self._print_counts()

    def _clear_data(self):
        Student.objects.all().delete()
        Department.objects.all().delete()
        Teacher.objects.all().delete()
        User.objects.filter(
            username__startswith="student_"
        ).delete()
        User.objects.filter(
            username__startswith="teacher_"
        ).delete()
        self.stdout.write(self.style.WARNING("Existing seed data cleared."))

    def _create_departments(self, count):
        departments = [
            Department(name=ENGINEERING_DEPARTMENTS[index])
            for index in range(count)
        ]
        return Department.objects.bulk_create(departments)

    def _create_teachers(self, count):
        teacher_users = []
        for index in range(count):
            first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
            last_name = LAST_NAMES[index % len(LAST_NAMES)]
            user = User(
                username=f"teacher_{index + 1:03d}",
                email=f"teacher_{index + 1:03d}@engineeringcollege.edu",
                first_name=first_name,
                last_name=last_name,
            )
            user.set_password(DEFAULT_PASSWORD)
            teacher_users.append(user)

        User.objects.bulk_create(teacher_users)
        created_users = list(
            User.objects.filter(username__startswith="teacher_").order_by("username")
        )

        teachers = [
            Teacher(
                user=created_users[index],
                employee_id=f"EMP{index + 1:04d}",
            )
            for index in range(count)
        ]
        return Teacher.objects.bulk_create(teachers)

    def _assign_hods(self, departments, teachers):
        for department, teacher in zip(departments, teachers[: len(departments)]):
            department.hod = teacher
        Department.objects.bulk_update(departments, ["hod"])

    def _create_students(self, count, departments):
        student_users = []
        for index in range(count):
            first_name = FIRST_NAMES[(index + 10) % len(FIRST_NAMES)]
            last_name = LAST_NAMES[(index + 5) % len(LAST_NAMES)]
            user = User(
                username=f"student_{index + 1:03d}",
                email=f"student_{index + 1:03d}@engineeringcollege.edu",
                first_name=first_name,
                last_name=last_name,
            )
            user.set_password(DEFAULT_PASSWORD)
            student_users.append(user)

        User.objects.bulk_create(student_users)
        created_users = list(
            User.objects.filter(username__startswith="student_").order_by("username")
        )

        students = [
            Student(
                user=created_users[index],
                department=departments[index % len(departments)],
                roll_number=f"EN{index + 1:04d}",
            )
            for index in range(count)
        ]
        Student.objects.bulk_create(students)

    def _print_counts(self):
        self.stdout.write(f"Users: {User.objects.count()}")
        self.stdout.write(f"Departments: {Department.objects.count()}")
        self.stdout.write(f"Teachers: {Teacher.objects.count()}")
        self.stdout.write(f"Students: {Student.objects.count()}")
