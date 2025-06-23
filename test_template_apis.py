#!/usr/bin/env python3
"""
Test template APIs
"""

import requests
import json

# Note: Update with your actual token
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTU4Nzg0NTksInN1YiI6ImUwNGM4ODFmLTU3YjUtNDJkOC1iYzM4LTgzYzM4OTY4YTVhMiJ9.p2rD6qe30TbEdXmTA22aU7oW0ClvF43lEYM6awTPjjE"
BASE_URL = "http://localhost:8080/api/v1"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def test_list_all_templates():
    """Test listing all templates"""
    print("1. Testing: List all templates")
    print("-" * 40)
    
    response = requests.get(f"{BASE_URL}/templates/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SUCCESS: Found {data['total']} templates")
        
        for i, template in enumerate(data['templates'][:3]):
            print(f"  {i+1}. {template['industry']} - {template['name']}")
        
        if data['total'] > 3:
            print(f"  ... and {data['total'] - 3} more")
            
        return data['templates']
    else:
        print(f"✗ FAILED: {response.status_code} - {response.text}")
        return []

def test_templates_by_industry():
    """Test getting templates grouped by industry"""
    print("\n2. Testing: Templates by industry")
    print("-" * 40)
    
    response = requests.get(f"{BASE_URL}/templates/industries", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SUCCESS: Found {len(data)} industries")
        
        for industry_group in data:
            industry = industry_group['industry']
            template_count = len(industry_group['templates'])
            print(f"  {industry}: {template_count} templates")
            
        return data
    else:
        print(f"✗ FAILED: {response.status_code} - {response.text}")
        return []

def test_filter_by_industry():
    """Test filtering templates by industry"""
    print("\n3. Testing: Filter by industry (Healthcare)")
    print("-" * 40)
    
    response = requests.get(f"{BASE_URL}/templates/?industry=Healthcare", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SUCCESS: Found {data['total']} Healthcare templates")
        
        for template in data['templates']:
            print(f"  - {template['name']} ({template['use_case']})")
    else:
        print(f"✗ FAILED: {response.status_code} - {response.text}")

def test_get_single_template(template_id):
    """Test getting a single template"""
    print(f"\n4. Testing: Get single template ({template_id[:8]}...)")
    print("-" * 40)
    
    response = requests.get(f"{BASE_URL}/templates/{template_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SUCCESS: Retrieved template '{data['name']}'")
        print(f"  Industry: {data['industry']}")
        print(f"  Use Case: {data['use_case']}")
        print(f"  Variables: {', '.join(data['variables'])}")
        print(f"  Functions: {', '.join(data['functions'])}")
        
        if data.get('suggested_settings'):
            print(f"  Suggested Settings: {len(data['suggested_settings'])} options")
            
        return data
    else:
        print(f"✗ FAILED: {response.status_code} - {response.text}")
        return None

def main():
    """Run all template API tests"""
    print("TESTING TEMPLATE APIs")
    print("=" * 50)
    
    # Test 1: List all templates
    templates = test_list_all_templates()
    
    # Test 2: Templates by industry
    industries = test_templates_by_industry()
    
    # Test 3: Filter by industry
    test_filter_by_industry()
    
    # Test 4: Get single template (if we have templates)
    if templates:
        first_template_id = templates[0]['id']
        template_details = test_get_single_template(first_template_id)
        
        if template_details:
            print(f"\n5. Template Details Preview:")
            print("-" * 40)
            print(f"Prompt (first 100 chars): {template_details['prompt'][:100]}...")
            if template_details.get('welcome_message'):
                print(f"Welcome Message: {template_details['welcome_message'][:100]}...")
    
    print(f"\n{'='*50}")
    print("Template API tests completed!")

if __name__ == "__main__":
    main()