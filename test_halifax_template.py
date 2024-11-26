#!/usr/bin/env python3

import json
import pdfplumber
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

def clean_amount(text):
    """Clean amount strings and convert to float, then format as string with 2 decimal places"""
    if not text or not isinstance(text, str):
        return None
    # Remove currency symbols and text
    amount = re.sub(r'[£,]|Money In \(£\)|Money Out \(£\)|Balance \(£\)|Money Obulat n\(£k\)', '', text)
    # Extract first number found
    match = re.search(r'(\d+\.?\d*)', amount)
    if match:
        try:
            return f"{float(match.group(1)):.2f}"
        except (ValueError, TypeError):
            return None
    return None

def clean_date(text):
    """Clean and standardize date format to YYYY-MM-DD"""
    if not text or not isinstance(text, str):
        return None
    # Extract date pattern DD MMM YY
    match = re.search(r'(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*(\d{2})', text)
    if match:
        day, month, year = match.groups()
        month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
            'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        return f"20{year}-{month_map[month]}-{day.zfill(2)}"
    return None

def clean_description(text):
    """Clean transaction description"""
    if not text or not isinstance(text, str):
        return None
    # Remove common noise patterns
    text = re.sub(r'Description|Type|CDolumn|\.\s*\.|^\s*\.|^D\s*$|DHescription|DGescription|DFescription|TDype|TFype|TType', '', text)
    text = ' '.join(text.split())
    return text.strip() if text.strip() else None

def clean_customer_details(text):
    """Clean customer name and other details"""
    if not text or not isinstance(text, str):
        return None
    # Remove common patterns and clean up
    text = re.sub(r'Document requested by:|Account Number \d+|Page \d+ of \d+|\d{1,2} \w+ \d{4}', '', text)
    text = re.sub(r'BICESTER|OXFORDSHIRE|OX\d+ \d\w+', '', text)
    text = ' '.join(text.split())
    return text.strip()

def extract_transaction_type(text):
    """Extract transaction type from text"""
    if not text or not isinstance(text, str):
        return None
    
    type_patterns = {
        r'DD\b': 'DD',
        r'FPI\b': 'FPI',
        r'DEB\b': 'DEB',
        r'TFR\b': 'TFR',
        r'BGC\b': 'BGC',
        r'CPT\b': 'CPT',
        r'CHG\b': 'CHG',
        r'SO\b': 'SO'
    }
    
    text = text.upper()
    for pattern, ttype in type_patterns.items():
        if re.search(pattern, text):
            return ttype
    return None

def extract_text_from_area(page, coordinates):
    """Extract text from a specific area of a PDF page"""
    x1 = coordinates['top_left']['x'] * float(page.width)
    y1 = coordinates['top_left']['y'] * float(page.height)
    x2 = coordinates['bottom_right']['x'] * float(page.width)
    y2 = coordinates['bottom_right']['y'] * float(page.height)
    
    crop_area = page.crop((x1, y1, x2, y2))
    return crop_area.extract_text()

def process_transactions(raw_data):
    """Process raw transaction data into clean records"""
    transactions = []
    
    # Get the maximum length of any column
    max_length = max(len(values) for values in raw_data.values())
    
    for i in range(max_length):
        # Get values for each field
        date = raw_data.get('date', [])[i] if i < len(raw_data.get('date', [])) else None
        type_text = raw_data.get('type', [])[i] if i < len(raw_data.get('type', [])) else None
        desc = raw_data.get('description', [])[i] if i < len(raw_data.get('description', [])) else None
        money_out = raw_data.get('money_out', [])[i] if i < len(raw_data.get('money_out', [])) else None
        money_in = raw_data.get('money_in', [])[i] if i < len(raw_data.get('money_in', [])) else None
        balance = raw_data.get('balance', [])[i] if i < len(raw_data.get('balance', [])) else None
        
        # Clean and validate each field
        date = clean_date(date)
        desc = clean_description(desc)
        ttype = extract_transaction_type(type_text or desc)
        money_out = clean_amount(money_out)
        money_in = clean_amount(money_in)
        balance = clean_amount(balance)
        
        if date and desc:
            transaction = {
                "date": date,
                "description": desc,
                "type": ttype,
                "money_in": money_in,
                "money_out": money_out,
                "balance": balance
            }
            transactions.append(transaction)
    
    return transactions

def extract_transactions(page, table_rule):
    """Extract transaction data from a page"""
    column_data = {}
    
    # Extract text from each column
    for column in table_rule['config']['columns']:
        text = extract_text_from_area(page, column['coordinates'])
        column_data[column['field_name']] = text.split('\n') if text else []
    
    return process_transactions(column_data)

def calculate_totals(transactions):
    """Calculate total money in and out"""
    money_in = sum(float(t['money_in']) for t in transactions if t['money_in'])
    money_out = sum(float(t['money_out']) for t in transactions if t['money_out'])
    return money_in, money_out

def extract_start_balance(text):
    """Extract start balance from text"""
    if not text or not isinstance(text, str):
        return None
    match = re.search(r'£?(\d+\.?\d*)', text)
    if match:
        try:
            return f"£{float(match.group(1)):.2f}"
        except (ValueError, TypeError):
            return None
    return None

def main():
    # Load the template
    with open('src/templates/halifax_template.json', 'r') as f:
        template = json.load(f)

    # Process all PDF files
    pdf_files = [
        ('March', 'data/bank_statements/halifax/pdf/March Halifax.pdf'),
        ('April', 'data/bank_statements/halifax/pdf/April Halifax.pdf'),
        ('May', 'data/bank_statements/halifax/pdf/May Halifax.pdf')
    ]
    
    # Create output directory if it doesn't exist
    Path("output").mkdir(exist_ok=True)
    
    for month, pdf_path in pdf_files:
        with pdfplumber.open(pdf_path) as pdf:
            # Create JSON structure
            output = {
                "metadata": {
                    "document_id": f"halifax_{month.lower()}",
                    "parsed_at": datetime.now().strftime("%Y-%m-%d"),
                    "number_of_pages": len(pdf.pages)
                },
                "pages": []
            }
            
            # Process first page
            first_page = pdf.pages[0]
            first_page_data = {
                "forms": [],
                "tables": []
            }
            
            # Extract customer details
            customer_rule = next(rule for rule in template['rules'] if rule['rule_id'] == 'customer_details')
            customer_name = extract_text_from_area(first_page, customer_rule['config']['coordinates'])
            if customer_name:
                customer_name = clean_customer_details(customer_name)
                if customer_name:
                    first_page_data["forms"].append({"customer_name": customer_name})
            
            # Extract sort code
            sort_code_rule = next(rule for rule in template['rules'] if rule['rule_id'] == 'sort_code')
            sort_code = extract_text_from_area(first_page, sort_code_rule['config']['coordinates'])
            if sort_code:
                sort_code = re.search(r'\d{2}-\d{2}-\d{2}', sort_code)
                if sort_code:
                    first_page_data["forms"].append({"sort_code": sort_code.group()})
            
            # Extract account number
            account_rule = next(rule for rule in template['rules'] if rule['rule_id'] == 'account_number')
            account_number = extract_text_from_area(first_page, account_rule['config']['coordinates'])
            if account_number:
                account_number = re.search(r'\d{8}', account_number)
                if account_number:
                    first_page_data["forms"].append({"account_number": account_number.group()})
            
            # Extract start balance
            start_balance_rule = next(rule for rule in template['rules'] if rule['rule_id'] == 'start_balance')
            start_balance = extract_text_from_area(first_page, start_balance_rule['config']['coordinates'])
            if start_balance:
                start_balance = extract_start_balance(start_balance)
                if start_balance:
                    first_page_data["forms"].append({"start_balance": start_balance})
            
            output["pages"].append(first_page_data)
            
            # Process transaction pages
            all_transactions = []
            for page_num in range(1, len(pdf.pages)):
                page = pdf.pages[page_num]
                page_data = {
                    "forms": [],
                    "tables": []
                }
                
                # Get transactions table rule
                table_rule = next(rule for rule in template['rules'] 
                                if rule['rule_id'] == 'transactions_page_2_onwards')
                
                # Extract transactions
                transactions = extract_transactions(page, table_rule)
                if transactions:
                    all_transactions.extend(transactions)
                    page_data["tables"].append({
                        "table_header": "Your Transactions",
                        "data": transactions
                    })
                
                output["pages"].append(page_data)
            
            # Calculate totals
            if all_transactions:
                money_in, money_out = calculate_totals(all_transactions)
                end_balance = float(all_transactions[-1]['balance'])
                
                # Add financial summary to first page forms
                output["pages"][0]["forms"].extend([
                    {"money_in": f"£{money_in:.2f}"},
                    {"money_out": f"£{money_out:.2f}"},
                    {"end_balance": f"£{end_balance:.2f}"}
                ])
            
            # Save to JSON file
            output_path = f'output/halifax_{month.lower()}.json'
            with open(output_path, 'w') as f:
                json.dump(output, f, indent=2)
            
            print(f"Processed {month} statement: {output_path}")

if __name__ == "__main__":
    main() 