from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import os
import re
from io import BytesIO
import warnings
import tempfile
import uuid
from datetime import datetime
warnings.filterwarnings('ignore')
from faker import Faker

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

fake = Faker()
Faker.seed(0)
generated_files = {}

class SimpleNLP:
    def __init__(self):
        self.stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                          'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                          'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
                          'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between',
                          'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                          'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
                          'own', 'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because',
                          'until', 'while', 'although', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'you', 'your',
                          'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them', 'what', 'which', 'who', 'whom',
                          'this', 'that', 'these', 'those', 'am', 'about', 'against', 'also', 'any', 'both', 'down', 'up',
                          'data', 'dataset', 'generate', 'create', 'need', 'want', 'like', 'using', 'use', 'model', 'build', 'make', 'include', 'required'}
    
    def extract_keywords(self, text):
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return [w for w in words if w not in self.stop_words]
    
    def detect_column_type(self, col_name):
        col_lower = col_name.lower().replace('_', ' ').replace('-', ' ')
        patterns = {
            'first_name': ['first name', 'firstname', 'fname', 'first_name'],
            'last_name': ['last name', 'lastname', 'lname', 'last_name', 'surname'],
            'full_name': ['full name', 'fullname', 'name', 'patient name', 'customer name', 'employee name'],
            'email': ['email', 'mail', 'e-mail'], 'phone': ['phone', 'mobile', 'cell', 'telephone', 'contact'],
            'street_address': ['street', 'address', 'addr'], 'city': ['city'], 'state': ['state'],
            'zipcode': ['zip', 'postal', 'pincode'], 'country': ['country'],
            'ssn': ['ssn', 'social security'], 'patient_id': ['patient id', 'patientid', 'patient_id', 'mrn', 'medical record'],
            'employee_id': ['employee id', 'employeeid', 'emp id', 'emp_id'],
            'customer_id': ['customer id', 'customerid', 'cust id', 'cust_id'],
            'order_id': ['order id', 'orderid', 'order_id', 'order number'],
            'transaction_id': ['transaction id', 'transactionid', 'trans id', 'txn id'],
            'product_id': ['product id', 'productid', 'prod id', 'sku'],
            'invoice_id': ['invoice', 'bill id'], 'generic_id': ['id', 'code'],
            'date_of_birth': ['dob', 'birth', 'birthday', 'date of birth'],
            'admission_date': ['admission', 'admit'], 'discharge_date': ['discharge'],
            'hire_date': ['hire', 'joining', 'join date'], 'transaction_date': ['order date', 'purchase date', 'transaction date'],
            'date': ['date', 'created', 'updated', 'timestamp'],
            'age': ['age'], 'salary': ['salary', 'income', 'wage', 'pay'],
            'price': ['price', 'cost', 'amount', 'total', 'revenue', 'fee'],
            'quantity': ['quantity', 'qty', 'count', 'number of'], 'rating': ['rating', 'score', 'grade'],
            'percentage': ['percentage', 'percent', 'rate'], 'measurement': ['weight', 'height', 'bmi'],
            'balance': ['balance', 'credit', 'debit'], 'years': ['year', 'experience'],
            'diagnosis': ['diagnosis', 'disease', 'condition', 'illness'],
            'medication': ['medication', 'medicine', 'drug', 'prescription'],
            'treatment': ['treatment', 'procedure', 'therapy'], 'blood_pressure': ['blood', 'bp', 'pressure'],
            'department': ['department', 'dept', 'ward', 'unit'], 'doctor_name': ['doctor', 'physician', 'specialist'],
            'insurance': ['insurance', 'policy', 'coverage'], 'length_of_stay': ['length of stay', 'los', 'stay duration'],
            'status': ['status', 'state'], 'category': ['type', 'category', 'class', 'segment'],
            'gender': ['gender', 'sex'], 'marital_status': ['marital', 'married'],
            'education': ['education', 'degree', 'qualification'], 'job_title': ['occupation', 'job', 'position', 'title', 'role'],
            'payment_method': ['payment', 'method'], 'shipping_method': ['shipping', 'delivery'],
            'product_name': ['product', 'item', 'goods'], 'brand': ['brand', 'manufacturer'],
            'description': ['description', 'desc', 'details', 'notes', 'comment'],
            'region': ['region', 'area', 'zone', 'territory'], 'company': ['company', 'organization', 'org', 'employer', 'business']
        }
        for col_type, pattern_list in patterns.items():
            if any(p in col_lower for p in pattern_list):
                return col_type
        return 'text'
    
    def extract_requirements(self, text):
        """Extract data requirements from free-form text"""
        keywords = self.extract_keywords(text)
        text_lower = text.lower()
        
        # Extract column mentions
        columns = []
        column_patterns = re.findall(r'(?:column|field|attribute|include|need|want|require|should have|must have)\s+([a-z_]+(?:\s+[a-z_]+)?)', text_lower)
        for match in column_patterns:
            col = match.strip().replace(' ', '_')
            if col and col not in columns:
                columns.append(col)
        
        # Extract numbers (record counts, ranges, etc.)
        numbers = re.findall(r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\b', text)
        num_records = 1000
        for num in numbers:
            n = int(num.replace(',', ''))
            if n > 100 and n < 100000000:
                num_records = n
                break
        
        # Extract ranges
        ranges = re.findall(r'(\d+)\s*(?:to|-|and)\s*(\d+)', text_lower)
        ranges_dict = {}
        for r in ranges:
            ranges_dict['min'] = int(r[0])
            ranges_dict['max'] = int(r[1])
        
        # Detect domain
        domain_keywords = {
            'healthcare': ['patient', 'medical', 'health', 'hospital', 'doctor', 'diagnosis', 'treatment', 'medicine', 'clinical', 'disease', 'symptom', 'pharmacy', 'readmission', 'admission', 'discharge', 'prescription', 'nurse'],
            'finance': ['bank', 'transaction', 'payment', 'loan', 'credit', 'money', 'financial', 'investment', 'account', 'fraud', 'risk', 'insurance', 'budget', 'revenue'],
            'retail': ['customer', 'product', 'sale', 'order', 'purchase', 'shop', 'store', 'inventory', 'price', 'discount', 'ecommerce', 'retail', 'cart', 'shipping'],
            'hr': ['employee', 'staff', 'hire', 'salary', 'job', 'performance', 'human', 'resource', 'workforce', 'recruitment', 'training', 'payroll', 'department'],
            'education': ['student', 'course', 'grade', 'school', 'university', 'education', 'learning', 'academic', 'teacher', 'exam', 'class', 'semester', 'degree']
        }
        
        domain_scores = {d: sum(1 for kw in keywords if any(dk in kw for dk in dk_list)) for d, dk_list in domain_keywords.items()}
        domain = max(domain_scores, key=domain_scores.get) if max(domain_scores.values()) > 0 else 'general'
        
        # If no columns found, use domain defaults
        if not columns:
            domain_columns = {
                'healthcare': ['patient_id', 'first_name', 'last_name', 'age', 'gender', 'diagnosis', 'admission_date', 'discharge_date', 'treatment', 'medication', 'department', 'doctor_name', 'insurance_type', 'length_of_stay'],
                'finance': ['transaction_id', 'customer_id', 'transaction_date', 'amount', 'transaction_type', 'merchant_category', 'account_type', 'balance', 'payment_status'],
                'retail': ['order_id', 'customer_id', 'product_name', 'category', 'quantity', 'unit_price', 'total_amount', 'order_date', 'payment_method', 'shipping_method', 'region'],
                'hr': ['employee_id', 'first_name', 'last_name', 'department', 'job_title', 'hire_date', 'salary', 'years_experience', 'education', 'performance_rating'],
                'education': ['student_id', 'first_name', 'last_name', 'course_name', 'grade', 'enrollment_date', 'credits', 'gpa', 'major', 'semester'],
                'general': ['id', 'name', 'category', 'value', 'date', 'status', 'description']
            }
            columns = domain_columns.get(domain, domain_columns['general'])
        
        return {'columns': columns[:20], 'num_records': num_records, 'domain': domain, 'keywords': list(set(keywords))[:15], 'ranges': ranges_dict}
    
    def parse_column_description(self, description):
        """Parse column description to extract requirements"""
        if not description:
            return {'dtype': None, 'min_val': None, 'max_val': None, 'categories': None}
        
        desc_lower = description.lower()
        result = {'dtype': None, 'min_val': None, 'max_val': None, 'categories': None}
        
        # Extract ranges (e.g., "between 25 and 75", "from 1000 to 5000", "18-65")
        range_patterns = [
            r'between\s+(\d+)\s+and\s+(\d+)',
            r'from\s+(\d+)\s+to\s+(\d+)',
            r'(\d+)\s*-\s*(\d+)',
            r'(\d+)\s+to\s+(\d+)',
            r'(\d+)\s+and\s+(\d+)'
        ]
        for pattern in range_patterns:
            matches = re.findall(pattern, desc_lower)
            if matches:
                result['min_val'] = matches[0][0]
                result['max_val'] = matches[0][1]
                break
        
        # Extract date ranges
        date_patterns = [
            r'from\s+(\d{4}-\d{2}-\d{2}|\d{4})\s+to\s+(\d{4}-\d{2}-\d{2}|\d{4})',
            r'between\s+(\d{4}-\d{2}-\d{2}|\d{4})\s+and\s+(\d{4}-\d{2}-\d{2}|\d{4})'
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, desc_lower)
            if matches:
                result['min_val'] = matches[0][0] if len(matches[0][0]) == 10 else matches[0][0] + '-01-01'
                result['max_val'] = matches[0][1] if len(matches[0][1]) == 10 else matches[0][1] + '-12-31'
                result['dtype'] = 'date'
                break
        
        # Extract categories (e.g., "Low, Medium, High", "Active, Inactive")
        if 'category' in desc_lower or 'option' in desc_lower or 'value' in desc_lower:
            category_match = re.search(r'(?:category|option|value|type)[s]?\s*(?:are|is|:)?\s*([a-z\s,]+)', desc_lower)
            if category_match:
                cats = [c.strip() for c in category_match.group(1).split(',') if c.strip()]
                if cats:
                    result['categories'] = ', '.join(cats)
                    result['dtype'] = 'categorical'
        
        # Detect data type from description
        if not result['dtype']:
            if any(x in desc_lower for x in ['email', 'mail']):
                result['dtype'] = 'email'
            elif any(x in desc_lower for x in ['phone', 'mobile', 'telephone']):
                result['dtype'] = 'phone'
            elif any(x in desc_lower for x in ['date', 'time', 'timestamp']):
                result['dtype'] = 'date'
            elif any(x in desc_lower for x in ['number', 'numeric', 'integer', 'decimal', 'float']):
                result['dtype'] = 'numeric'
            elif any(x in desc_lower for x in ['boolean', 'true/false', 'yes/no']):
                result['dtype'] = 'boolean'
            elif any(x in desc_lower for x in ['text', 'string', 'description']):
                result['dtype'] = 'string'
        
        return result

nlp = SimpleNLP()

HIPAA_PHI_IDENTIFIERS = ['name', 'firstname', 'first_name', 'lastname', 'last_name', 'fullname', 'full_name', 'address', 'street', 'city', 'state', 'zip', 'zipcode', 'zip_code', 'country', 'phone', 'telephone', 'mobile', 'cell', 'phone_number', 'fax', 'email', 'email_address', 'mail', 'ssn', 'social_security', 'social_security_number', 'mrn', 'medical_record', 'medical_record_number', 'patient_id', 'patientid', 'dob', 'date_of_birth', 'birthdate', 'birth_date', 'birthday', 'ip', 'ip_address', 'mac_address', 'license', 'license_number', 'drivers_license', 'account', 'account_number', 'bank_account', 'credit_card', 'creditcard', 'card_number', 'vin', 'vehicle_identification', 'device_id', 'serial_number', 'biometric', 'fingerprint', 'face_id', 'photo', 'image', 'photograph', 'certificate', 'certificate_number', 'beneficiary', 'insurance_id', 'policy_number', 'member_id']

DATA_POOLS = {
    'first_names': [fake.first_name() for _ in range(1000)],
    'last_names': [fake.last_name() for _ in range(1000)],
    'cities': [fake.city() for _ in range(500)],
    'states': ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'],
    'countries': ['USA', 'Canada', 'UK', 'Germany', 'France', 'Australia', 'Japan', 'India', 'Brazil', 'Mexico', 'Italy', 'Spain', 'Netherlands'],
    'companies': [fake.company() for _ in range(500)],
    'job_titles': ['Software Engineer', 'Data Analyst', 'Project Manager', 'Sales Representative', 'Marketing Manager', 'HR Specialist', 'Financial Analyst', 'Product Manager', 'Operations Manager', 'Customer Service Rep', 'Account Executive', 'Designer', 'Developer', 'Consultant', 'Director', 'VP', 'Manager', 'Coordinator', 'Specialist'],
    'departments': ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations', 'Customer Service', 'IT', 'Legal', 'R&D', 'Admin', 'Cardiology', 'Neurology', 'Oncology', 'Pediatrics', 'Emergency', 'Surgery', 'Radiology'],
    'products': ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Monitor', 'Keyboard', 'Mouse', 'Camera', 'Speaker', 'Printer', 'TV', 'Watch', 'Shoes', 'Shirt', 'Pants', 'Jacket', 'Bag', 'Book', 'Toy', 'Game'],
    'diagnoses': ['Hypertension', 'Diabetes Type 2', 'Asthma', 'COPD', 'Heart Failure', 'Pneumonia', 'UTI', 'Fracture', 'Migraine', 'Arthritis', 'Anemia', 'Depression', 'Anxiety', 'Back Pain', 'Bronchitis', 'Influenza'],
    'medications': ['Lisinopril', 'Metformin', 'Amlodipine', 'Omeprazole', 'Simvastatin', 'Losartan', 'Albuterol', 'Gabapentin', 'Hydrochlorothiazide', 'Atorvastatin', 'Levothyroxine', 'Metoprolol', 'Prednisone', 'Amoxicillin', 'Ibuprofen'],
    'treatments': ['Physical Therapy', 'Surgery', 'Chemotherapy', 'Radiation', 'Dialysis', 'Medication Management', 'Counseling', 'Rehabilitation', 'Observation', 'IV Fluids', 'Blood Transfusion', 'Wound Care', 'Oxygen Therapy'],
    'insurance': ['Medicare', 'Medicaid', 'Blue Cross', 'Aetna', 'Cigna', 'UnitedHealth', 'Humana', 'Kaiser', 'Self-Pay', 'Private Insurance'],
    'education': ['High School', 'Associate', 'Bachelor', 'Master', 'PhD', 'MD', 'JD'],
    'payment_methods': ['Credit Card', 'Debit Card', 'Cash', 'PayPal', 'Bank Transfer', 'Check'],
    'shipping_methods': ['Standard', 'Express', 'Overnight', 'Economy', 'Priority', 'Same Day'],
    'regions': ['North', 'South', 'East', 'West', 'Northeast', 'Southeast', 'Midwest', 'Southwest'],
    'categories': ['Electronics', 'Clothing', 'Home', 'Sports', 'Books', 'Toys', 'Food', 'Health'],
    'statuses': ['Active', 'Inactive', 'Pending', 'Completed', 'Cancelled', 'Processing'],
    'genders': ['Male', 'Female', 'Other'],
    'marital': ['Single', 'Married', 'Divorced', 'Widowed'],
    'brands': ['Apple', 'Samsung', 'Sony', 'LG', 'Dell', 'HP', 'Nike', 'Adidas', 'Gucci', 'Prada']
}

def is_hipaa_sensitive(col_name):
    return any(phi in col_name.lower().replace(' ', '_').replace('-', '_') for phi in HIPAA_PHI_IDENTIFIERS)

def generate_batch_data(col_type, size, min_val=None, max_val=None, categories=None):
    if col_type == 'first_name': return np.random.choice(DATA_POOLS['first_names'], size).tolist()
    elif col_type == 'last_name': return np.random.choice(DATA_POOLS['last_names'], size).tolist()
    elif col_type == 'full_name':
        first, last = np.random.choice(DATA_POOLS['first_names'], size), np.random.choice(DATA_POOLS['last_names'], size)
        return [f"{f} {l}" for f, l in zip(first, last)]
    elif col_type == 'email':
        first, last, dom = np.random.choice(DATA_POOLS['first_names'], size), np.random.choice(DATA_POOLS['last_names'], size), np.random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'email.com', 'company.com'], size)
        nums = np.random.randint(1, 999, size)
        return [f"{f.lower()}.{l.lower()}{n}@{d}" for f, l, n, d in zip(first, last, nums, dom)]
    elif col_type == 'phone':
        area, mid, end = np.random.randint(200, 999, size), np.random.randint(200, 999, size), np.random.randint(1000, 9999, size)
        return [f"({a}) {m}-{e}" for a, m, e in zip(area, mid, end)]
    elif col_type == 'street_address':
        nums, streets = np.random.randint(100, 9999, size), np.random.choice(['Main St', 'Oak Ave', 'Park Blvd', 'Cedar Ln', 'Elm St', 'Pine Rd', 'Maple Dr', 'Washington Ave'], size)
        return [f"{n} {s}" for n, s in zip(nums, streets)]
    elif col_type == 'city': return np.random.choice(DATA_POOLS['cities'], size).tolist()
    elif col_type == 'state': return np.random.choice(DATA_POOLS['states'], size).tolist()
    elif col_type == 'zipcode': return [f"{z}**"[:5] for z in np.random.randint(10000, 99999, size)]
    elif col_type == 'country': return np.random.choice(DATA_POOLS['countries'], size).tolist()
    elif col_type == 'ssn': return [f"***-**-{np.random.randint(1000, 9999)}" for _ in range(size)]
    elif col_type == 'patient_id': return [f"PAT-{str(i+1).zfill(8)}" for i in range(size)]
    elif col_type == 'employee_id': return [f"EMP-{str(i+1).zfill(6)}" for i in range(size)]
    elif col_type == 'customer_id': return [f"CUST-{str(i+1).zfill(7)}" for i in range(size)]
    elif col_type == 'order_id': return [f"ORD-{str(i+1).zfill(8)}" for i in range(size)]
    elif col_type == 'transaction_id': return [f"TXN-{str(i+1).zfill(10)}" for i in range(size)]
    elif col_type == 'product_id': return [f"PROD-{str(i+1).zfill(6)}" for i in range(size)]
    elif col_type == 'invoice_id': return [f"INV-{str(i+1).zfill(7)}" for i in range(size)]
    elif col_type == 'generic_id': return [f"ID-{str(i+1).zfill(6)}" for i in range(size)]
    elif col_type == 'date_of_birth':
        ages = np.random.randint(18, 89, size)
        base = pd.Timestamp('2024-01-01')
        return [(base - pd.Timedelta(days=int(a*365 + np.random.randint(0, 365)))).strftime('%Y-%m-%d') for a in ages]
    elif col_type in ['admission_date', 'hire_date', 'transaction_date', 'date']:
        start = pd.Timestamp(min_val) if min_val else pd.Timestamp('2020-01-01')
        end = pd.Timestamp(max_val) if max_val else pd.Timestamp('2024-12-31')
        days_range = max((end - start).days, 365)
        return [(start + pd.Timedelta(days=int(d))).strftime('%Y-%m-%d') for d in np.random.randint(0, days_range, size)]
    elif col_type == 'discharge_date':
        start, end = pd.Timestamp('2020-01-01'), pd.Timestamp('2024-12-31')
        return [(start + pd.Timedelta(days=int(d))).strftime('%Y-%m-%d') for d in np.random.randint(0, (end - start).days, size)]
    elif col_type == 'age':
        min_v, max_v = int(min_val) if min_val else 18, min(int(max_val) if max_val else 89, 89)
        return np.random.randint(min_v, max_v + 1, size).tolist()
    elif col_type == 'salary':
        min_v, max_v = float(min_val) if min_val else 30000, float(max_val) if max_val else 200000
        return np.round(np.random.uniform(min_v, max_v, size), 2).tolist()
    elif col_type == 'price':
        min_v, max_v = float(min_val) if min_val else 1, float(max_val) if max_val else 1000
        return np.round(np.random.uniform(min_v, max_v, size), 2).tolist()
    elif col_type == 'quantity':
        min_v, max_v = int(min_val) if min_val else 1, int(max_val) if max_val else 100
        return np.random.randint(min_v, max_v + 1, size).tolist()
    elif col_type == 'rating':
        min_v, max_v = int(min_val) if min_val else 1, int(max_val) if max_val else 5
        return np.random.randint(min_v, max_v + 1, size).tolist()
    elif col_type == 'percentage':
        min_v, max_v = float(min_val) if min_val else 0, float(max_val) if max_val else 100
        return np.round(np.random.uniform(min_v, max_v, size), 1).tolist()
    elif col_type == 'measurement':
        min_v, max_v = float(min_val) if min_val else 50, float(max_val) if max_val else 200
        return np.round(np.random.uniform(min_v, max_v, size), 1).tolist()
    elif col_type == 'balance':
        min_v, max_v = float(min_val) if min_val else -10000, float(max_val) if max_val else 100000
        return np.round(np.random.uniform(min_v, max_v, size), 2).tolist()
    elif col_type == 'years':
        min_v, max_v = int(min_val) if min_val else 0, int(max_val) if max_val else 40
        return np.random.randint(min_v, max_v + 1, size).tolist()
    elif col_type == 'length_of_stay': return np.random.randint(1, 30, size).tolist()
    elif col_type == 'diagnosis': return np.random.choice(DATA_POOLS['diagnoses'], size).tolist()
    elif col_type == 'medication': return np.random.choice(DATA_POOLS['medications'], size).tolist()
    elif col_type == 'treatment': return np.random.choice(DATA_POOLS['treatments'], size).tolist()
    elif col_type == 'blood_pressure':
        sys, dia = np.random.randint(90, 180, size), np.random.randint(60, 110, size)
        return [f"{s}/{d}" for s, d in zip(sys, dia)]
    elif col_type == 'department': return np.random.choice(DATA_POOLS['departments'], size).tolist()
    elif col_type == 'doctor_name':
        first, last = np.random.choice(DATA_POOLS['first_names'], size), np.random.choice(DATA_POOLS['last_names'], size)
        return [f"Dr. {f} {l}" for f, l in zip(first, last)]
    elif col_type == 'insurance': return np.random.choice(DATA_POOLS['insurance'], size).tolist()
    elif col_type == 'status': return np.random.choice(DATA_POOLS['statuses'], size).tolist()
    elif col_type == 'category':
        return np.random.choice([c.strip() for c in categories.split(',')], size).tolist() if categories else np.random.choice(DATA_POOLS['categories'], size).tolist()
    elif col_type == 'gender': return np.random.choice(DATA_POOLS['genders'], size).tolist()
    elif col_type == 'marital_status': return np.random.choice(DATA_POOLS['marital'], size).tolist()
    elif col_type == 'education': return np.random.choice(DATA_POOLS['education'], size).tolist()
    elif col_type == 'job_title': return np.random.choice(DATA_POOLS['job_titles'], size).tolist()
    elif col_type == 'payment_method': return np.random.choice(DATA_POOLS['payment_methods'], size).tolist()
    elif col_type == 'shipping_method': return np.random.choice(DATA_POOLS['shipping_methods'], size).tolist()
    elif col_type == 'product_name': return np.random.choice(DATA_POOLS['products'], size).tolist()
    elif col_type == 'brand': return np.random.choice(DATA_POOLS['brands'], size).tolist()
    elif col_type == 'description': return np.random.choice(['Standard item', 'Premium quality', 'Best seller', 'New arrival', 'Limited edition', 'Customer favorite', 'Top rated', 'Value pack', 'Special offer', 'Recommended'], size).tolist()
    elif col_type == 'region': return np.random.choice(DATA_POOLS['regions'], size).tolist()
    elif col_type == 'company': return np.random.choice(DATA_POOLS['companies'], size).tolist()
    elif col_type == 'numeric':
        min_v, max_v = float(min_val) if min_val else 0, float(max_val) if max_val else 100
        return np.random.randint(int(min_v), int(max_v) + 1, size).tolist() if min_v == int(min_v) and max_v == int(max_v) else np.round(np.random.uniform(min_v, max_v, size), 2).tolist()
    elif col_type == 'boolean': return np.random.choice([True, False], size).tolist()
    else:
        words, nums = np.random.choice(['Item', 'Data', 'Value', 'Entry', 'Record', 'Unit', 'Element', 'Object'], size), np.random.randint(1, 10000, size)
        return [f"{word}_{n}" for word, n in zip(words, nums)]

def generate_smart_column_data(col_name, num_records, dtype=None, min_val=None, max_val=None, categories=None):
    col_type = nlp.detect_column_type(col_name)
    if dtype:
        if dtype == 'numeric': col_type = 'numeric'
        elif dtype == 'categorical': col_type = 'category'
        elif dtype == 'date': col_type = 'date'
        elif dtype == 'boolean': col_type = 'boolean'
        elif dtype == 'email': col_type = 'email'
        elif dtype == 'phone': col_type = 'phone'
    return generate_batch_data(col_type, num_records, min_val, max_val, categories)

def generate_large_dataset_streaming(columns, num_records, generate_func, chunk_size=100000):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'synthetic_data_{file_id}.csv')
    df_header = pd.DataFrame(columns=columns)
    df_header.to_csv(file_path, index=False, mode='w')
    total_chunks = (num_records + chunk_size - 1) // chunk_size
    masked_columns = []
    for chunk_idx in range(total_chunks):
        start_idx, end_idx = chunk_idx * chunk_size, min(start_idx + chunk_size, num_records)
        chunk_data = {col: generate_func(col, end_idx - start_idx) for col in columns}
        if chunk_idx == 0:
            masked_columns = [col for col in columns if is_hipaa_sensitive(col)]
        pd.DataFrame(chunk_data).to_csv(file_path, index=False, mode='a', header=False)
    generated_files[file_id] = {'path': file_path, 'created': datetime.now(), 'num_records': num_records, 'columns': columns, 'masked_columns': masked_columns}
    return file_id, masked_columns

def generate_from_sample(sample_df, num_records, distribution='gaussian', allow_repeat=True):
    synthetic_data = {}
    for col in sample_df.columns:
        col_data = sample_df[col].dropna()
        if len(col_data) == 0:
            synthetic_data[col] = [None] * num_records
            continue
        if is_hipaa_sensitive(col):
            synthetic_data[col] = generate_batch_data(nlp.detect_column_type(col), num_records)
            continue
        if pd.api.types.is_numeric_dtype(col_data):
            mean, std, min_val, max_val = col_data.mean(), col_data.std() if col_data.std() > 0 else 1, col_data.min(), col_data.max()
            if distribution == 'ctgan':
                try:
                    hist, bin_edges = np.histogram(col_data.values, bins='auto', density=True)
                    if len(hist) > 0 and hist.sum() > 0:
                        bin_centers, probs = (bin_edges[:-1] + bin_edges[1:]) / 2, hist / hist.sum()
                        synthetic_values = np.random.choice(bin_centers, size=num_records, p=probs) + np.random.uniform(-0.5, 0.5, num_records) * (bin_edges[1] - bin_edges[0])
                    else:
                        synthetic_values = np.random.normal(mean, std, num_records)
                except:
                    synthetic_values = np.random.normal(mean, std, num_records)
            else:
                synthetic_values = np.random.normal(mean, std, num_records)
            synthetic_values = np.clip(synthetic_values, min_val, max_val)
            synthetic_data[col] = (np.round(synthetic_values).astype(int) if pd.api.types.is_integer_dtype(sample_df[col]) else np.round(synthetic_values, 2)).tolist()
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            min_date, max_date, date_range = col_data.min(), col_data.max(), max((max_date - min_date).days, 365)
            synthetic_data[col] = [(min_date + pd.Timedelta(days=int(d))).strftime('%Y-%m-%d') for d in np.random.randint(0, date_range, num_records)]
        else:
            unique_values, value_counts = col_data.unique(), col_data.value_counts(normalize=True)
            if allow_repeat or len(unique_values) < num_records:
                synthetic_data[col] = np.random.choice(value_counts.index, size=num_records, p=value_counts.values, replace=True).tolist()
            else:
                full_cycles, remainder = num_records // len(unique_values), num_records % len(unique_values)
                synthetic_values = list(unique_values) * full_cycles + list(np.random.choice(unique_values, remainder, replace=False))
                np.random.shuffle(synthetic_values)
                synthetic_data[col] = list(synthetic_values)
    return pd.DataFrame(synthetic_data), [col for col in sample_df.columns if is_hipaa_sensitive(col)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_nlp', methods=['POST'])
def process_nlp():
    data = request.json
    text = data.get('text', '')
    num_records = int(data.get('num_records', 1000))
    if not text:
        return jsonify({'error': 'Text input is required'}), 400
    req = nlp.extract_requirements(text)
    if data.get('num_records'):
        req['num_records'] = num_records
    columns = req['columns']
    if num_records > 100000:
        def generate_func(col, size):
            return generate_smart_column_data(col, size, None, req['ranges'].get('min'), req['ranges'].get('max'))
        file_id, masked_columns = generate_large_dataset_streaming(columns, num_records, generate_func)
        preview_data = {col: generate_smart_column_data(col, 10) for col in columns}
        return jsonify({'success': True, 'preview': pd.DataFrame(preview_data).to_dict(orient='records'), 'columns': columns, 'total_records': num_records, 'masked_columns': masked_columns, 'domain': req['domain'], 'file_id': file_id, 'large_file': True})
    df_data = {col: generate_smart_column_data(col, num_records) for col in columns}
    df = pd.DataFrame(df_data)
    masked_columns = [col for col in columns if is_hipaa_sensitive(col)]
    output = BytesIO()
    df.to_csv(output, index=False)
    return jsonify({'success': True, 'preview': df.head(10).to_dict(orient='records'), 'columns': columns, 'total_records': len(df), 'masked_columns': masked_columns, 'domain': req['domain'], 'csv_data': output.getvalue().decode('utf-8'), 'large_file': False})

@app.route('/analyze_problem', methods=['POST'])
def analyze_problem():
    data = request.json
    if not data.get('problem_statement'):
        return jsonify({'error': 'Problem statement is required'}), 400
    keywords = nlp.extract_keywords(data['problem_statement'])
    domain_keywords = {'healthcare': ['patient', 'medical', 'health', 'hospital', 'doctor', 'diagnosis', 'treatment', 'medicine', 'clinical', 'disease', 'symptom', 'pharmacy', 'readmission', 'admission', 'discharge', 'prescription', 'nurse'], 'finance': ['bank', 'transaction', 'payment', 'loan', 'credit', 'money', 'financial', 'investment', 'account', 'fraud', 'risk', 'insurance', 'budget', 'revenue'], 'retail': ['customer', 'product', 'sale', 'order', 'purchase', 'shop', 'store', 'inventory', 'price', 'discount', 'ecommerce', 'retail', 'cart', 'shipping'], 'hr': ['employee', 'staff', 'hire', 'salary', 'job', 'performance', 'human', 'resource', 'workforce', 'recruitment', 'training', 'payroll', 'department'], 'education': ['student', 'course', 'grade', 'school', 'university', 'education', 'learning', 'academic', 'teacher', 'exam', 'class', 'semester', 'degree']}
    domain_scores = {d: sum(1 for kw in keywords if any(dk in kw for dk in dk_list)) for d, dk_list in domain_keywords.items()}
    best_domain = max(domain_scores, key=domain_scores.get) if max(domain_scores.values()) > 0 else 'general'
    domain_columns = {'healthcare': ['patient_id', 'first_name', 'last_name', 'age', 'gender', 'diagnosis', 'admission_date', 'discharge_date', 'treatment', 'medication', 'department', 'doctor_name', 'insurance_type', 'length_of_stay'], 'finance': ['transaction_id', 'customer_id', 'transaction_date', 'amount', 'transaction_type', 'merchant_category', 'account_type', 'balance', 'payment_status'], 'retail': ['order_id', 'customer_id', 'product_name', 'category', 'quantity', 'unit_price', 'total_amount', 'order_date', 'payment_method', 'shipping_method', 'region'], 'hr': ['employee_id', 'first_name', 'last_name', 'department', 'job_title', 'hire_date', 'salary', 'years_experience', 'education', 'performance_rating'], 'education': ['student_id', 'first_name', 'last_name', 'course_name', 'grade', 'enrollment_date', 'credits', 'gpa', 'major', 'semester'], 'general': ['id', 'name', 'category', 'value', 'date', 'status', 'description']}
    columns = domain_columns.get(best_domain, domain_columns['general'])
    additional_cols = [kw for kw in keywords if len(kw) > 2 and kw not in [c.lower().replace('_', '') for c in columns]][:5]
    return jsonify({'domain': best_domain, 'columns': columns + additional_cols, 'keywords': list(set(keywords))[:10], 'entities': []})

@app.route('/generate_from_problem', methods=['POST'])
def generate_from_problem():
    data = request.json
    if not data.get('problem_statement'):
        return jsonify({'error': 'Problem statement is required'}), 400
    num_records = int(data.get('num_records', 100))
    keywords = nlp.extract_keywords(data['problem_statement'])
    domain_keywords = {'healthcare': ['patient', 'medical', 'health', 'hospital', 'doctor', 'diagnosis', 'treatment', 'medicine', 'clinical', 'disease', 'symptom', 'pharmacy', 'readmission', 'admission', 'discharge', 'prescription', 'nurse'], 'finance': ['bank', 'transaction', 'payment', 'loan', 'credit', 'money', 'financial', 'investment', 'account', 'fraud', 'risk', 'insurance', 'budget', 'revenue'], 'retail': ['customer', 'product', 'sale', 'order', 'purchase', 'shop', 'store', 'inventory', 'price', 'discount', 'ecommerce', 'retail', 'cart', 'shipping'], 'hr': ['employee', 'staff', 'hire', 'salary', 'job', 'performance', 'human', 'resource', 'workforce', 'recruitment', 'training', 'payroll', 'department'], 'education': ['student', 'course', 'grade', 'school', 'university', 'education', 'learning', 'academic', 'teacher', 'exam', 'class', 'semester', 'degree']}
    domain_scores = {d: sum(1 for kw in keywords if any(dk in kw for dk in dk_list)) for d, dk_list in domain_keywords.items()}
    best_domain = max(domain_scores, key=domain_scores.get) if max(domain_scores.values()) > 0 else 'general'
    domain_columns = {'healthcare': ['patient_id', 'first_name', 'last_name', 'age', 'gender', 'diagnosis', 'admission_date', 'discharge_date', 'treatment', 'medication', 'department', 'doctor_name', 'insurance_type', 'length_of_stay'], 'finance': ['transaction_id', 'customer_id', 'transaction_date', 'amount', 'transaction_type', 'merchant_category', 'account_type', 'balance', 'payment_status'], 'retail': ['order_id', 'customer_id', 'product_name', 'category', 'quantity', 'unit_price', 'total_amount', 'order_date', 'payment_method', 'shipping_method', 'region'], 'hr': ['employee_id', 'first_name', 'last_name', 'department', 'job_title', 'hire_date', 'salary', 'years_experience', 'education', 'performance_rating'], 'education': ['student_id', 'first_name', 'last_name', 'course_name', 'grade', 'enrollment_date', 'credits', 'gpa', 'major', 'semester'], 'general': ['id', 'name', 'category', 'value', 'date', 'status', 'description']}
    columns = domain_columns.get(best_domain, domain_columns['general'])
    additional_cols = [kw for kw in keywords if len(kw) > 2 and kw not in [c.lower().replace('_', '') for c in columns]][:5]
    columns = columns + additional_cols
    if num_records > 100000:
        def generate_func(col, size):
            return generate_smart_column_data(col, size)
        file_id, masked_columns = generate_large_dataset_streaming(columns, num_records, generate_func)
        preview_data = {col: generate_smart_column_data(col, 10) for col in columns}
        return jsonify({'success': True, 'preview': pd.DataFrame(preview_data).to_dict(orient='records'), 'columns': columns, 'total_records': num_records, 'masked_columns': masked_columns, 'domain': best_domain, 'file_id': file_id, 'large_file': True})
    df_data = {col: generate_smart_column_data(col, num_records) for col in columns}
    df = pd.DataFrame(df_data)
    masked_columns = [col for col in columns if is_hipaa_sensitive(col)]
    output = BytesIO()
    df.to_csv(output, index=False)
    return jsonify({'success': True, 'preview': df.head(10).to_dict(orient='records'), 'columns': list(df.columns), 'total_records': len(df), 'masked_columns': masked_columns, 'domain': best_domain, 'csv_data': output.getvalue().decode('utf-8'), 'large_file': False})

@app.route('/generate_from_attributes', methods=['POST'])
def generate_from_attributes():
    data = request.json
    attributes = data.get('attributes', [])
    num_records = int(data.get('num_records', 100))
    if not attributes:
        return jsonify({'error': 'At least one attribute is required'}), 400
    columns = [attr.get('name', 'column') for attr in attributes]
    
    # Process descriptions for each attribute
    processed_attrs = []
    for attr in attributes:
        col_name = attr.get('name', 'column')
        description = attr.get('description', '')
        dtype = attr.get('dtype', '')
        
        # Parse description using NLP
        desc_info = nlp.parse_column_description(description) if description else {}
        
        # Use description info, fallback to explicit dtype/min/max if provided
        final_dtype = dtype or desc_info.get('dtype')
        final_min = attr.get('min') or desc_info.get('min_val')
        final_max = attr.get('max') or desc_info.get('max_val')
        final_categories = attr.get('categories') or desc_info.get('categories')
        
        processed_attrs.append({
            'name': col_name,
            'dtype': final_dtype,
            'min': final_min,
            'max': final_max,
            'categories': final_categories
        })
    
    if num_records > 100000:
        def generate_func(col, size):
            attr = next((a for a in processed_attrs if a.get('name') == col), {})
            return generate_smart_column_data(col, size, attr.get('dtype'), attr.get('min'), attr.get('max'), attr.get('categories'))
        file_id, masked_columns = generate_large_dataset_streaming(columns, num_records, generate_func)
        preview_data = {attr.get('name', 'column'): generate_smart_column_data(attr.get('name', 'column'), 10, attr.get('dtype'), attr.get('min'), attr.get('max'), attr.get('categories')) for attr in processed_attrs}
        return jsonify({'success': True, 'preview': pd.DataFrame(preview_data).to_dict(orient='records'), 'columns': columns, 'total_records': num_records, 'masked_columns': masked_columns, 'file_id': file_id, 'large_file': True})
    df_data = {}
    masked_columns = []
    for attr in processed_attrs:
        col_name = attr.get('name', 'column')
        if is_hipaa_sensitive(col_name):
            masked_columns.append(col_name)
        df_data[col_name] = generate_smart_column_data(col_name, num_records, attr.get('dtype'), attr.get('min'), attr.get('max'), attr.get('categories'))
    df = pd.DataFrame(df_data)
    output = BytesIO()
    df.to_csv(output, index=False)
    return jsonify({'success': True, 'preview': df.head(10).to_dict(orient='records'), 'columns': list(df.columns), 'total_records': len(df), 'masked_columns': masked_columns, 'csv_data': output.getvalue().decode('utf-8'), 'large_file': False})

@app.route('/generate_from_sample', methods=['POST'])
def generate_from_sample_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    num_records = int(request.form.get('num_records', 100))
    distribution = request.form.get('distribution', 'gaussian')
    allow_repeat = request.form.get('allow_repeat', 'true') == 'true'
    try:
        sample_df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file) if file.filename.endswith(('.xls', '.xlsx')) else None
        if sample_df is None:
            return jsonify({'error': 'Unsupported file format. Use CSV or Excel.'}), 400
        if len(sample_df) < 5:
            return jsonify({'error': 'Sample dataset should have at least 5 records'}), 400
        if num_records > 100000:
            file_id, columns = str(uuid.uuid4()), list(sample_df.columns)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'synthetic_data_{file_id}.csv')
            sample_df.head(0).to_csv(file_path, index=False, mode='w')
            chunk_size, total_chunks, masked_columns = 100000, (num_records + 100000 - 1) // 100000, []
            for chunk_idx in range(total_chunks):
                chunk_size_actual = min(chunk_size, num_records - chunk_idx * chunk_size)
                synthetic_df, _ = generate_from_sample(sample_df, chunk_size_actual, distribution, allow_repeat)
                synthetic_df.to_csv(file_path, index=False, mode='a', header=False)
                if chunk_idx == 0:
                    masked_columns = [col for col in columns if is_hipaa_sensitive(col)]
            generated_files[file_id] = {'path': file_path, 'created': datetime.now(), 'num_records': num_records, 'columns': columns, 'masked_columns': masked_columns}
            preview_df, _ = generate_from_sample(sample_df, 10, distribution, allow_repeat)
            return jsonify({'success': True, 'preview': preview_df.to_dict(orient='records'), 'columns': columns, 'total_records': num_records, 'masked_columns': masked_columns, 'original_records': len(sample_df), 'file_id': file_id, 'large_file': True})
        synthetic_df, masked_columns = generate_from_sample(sample_df, num_records, distribution, allow_repeat)
        output = BytesIO()
        synthetic_df.to_csv(output, index=False)
        return jsonify({'success': True, 'preview': synthetic_df.head(10).to_dict(orient='records'), 'columns': list(synthetic_df.columns), 'total_records': len(synthetic_df), 'masked_columns': masked_columns, 'original_records': len(sample_df), 'csv_data': output.getvalue().decode('utf-8'), 'large_file': False})
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    if file_id not in generated_files:
        return jsonify({'error': 'File not found'}), 404
    file_info = generated_files[file_id]
    if not os.path.exists(file_info['path']):
        return jsonify({'error': 'File expired or not found'}), 404
    return send_file(file_info['path'], mimetype='text/csv', as_attachment=True, download_name=f'synthetic_data_{file_id[:8]}.csv')

@app.route('/detect_column_type', methods=['POST'])
def detect_column_type():
    data = request.json
    if not data.get('column_name'):
        return jsonify({'error': 'Column name is required'}), 400
    col_name = data['column_name']
    return jsonify({'column_name': col_name, 'detected_type': nlp.detect_column_type(col_name), 'is_hipaa_sensitive': is_hipaa_sensitive(col_name)})

@app.route('/check_hipaa', methods=['POST'])
def check_hipaa():
    data = request.json
    columns = data.get('columns', [])
    sensitive = [col for col in columns if is_hipaa_sensitive(col)]
    return jsonify({'sensitive_columns': sensitive, 'safe_columns': [col for col in columns if col not in sensitive]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
