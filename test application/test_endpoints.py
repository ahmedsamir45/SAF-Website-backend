import os
import sys
import json
import requests
import time
from typing import Dict, List, Tuple, Any, Optional
from urllib.parse import urljoin

class Colors:
    """ANSI color codes for console output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ==========================================
# Configuration
# ==========================================
BASE_URL = 'http://127.0.0.1:8000/api/'
TEST_EMAIL = f'test_{int(time.time())}@example.com'
TEST_PASSWORD = 'Test@1234'

def check_server_health() -> bool:
    """Check if the server is running and accessible"""
    try:
        # Try to access the public categories endpoint
        response = requests.get(BASE_URL + 'public/programs/categories/', timeout=5)
        if response.status_code != 200:
            print(f"{Colors.FAIL}Error: Unexpected status code {response.status_code} from server")
            print(f"Response: {response.text[:500]}...{Colors.ENDC}")
            return False
        return True
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}Error: Could not connect to the server at {BASE_URL}")
        print(f"Error details: {str(e)}{Colors.ENDC}")
        return False

# Check if server is running
if not check_server_health():
    print(f"{Colors.WARNING}\nPlease make sure the Django development server is running:")
    print(f"1. Open a new terminal")
    print(f"2. cd D:\\Projects\\SAF_backend")
    print(f"3. env\\Scripts\\activate")
    print(f"4. python manage.py runserver{Colors.ENDC}")
    print(f"\n{Colors.WARNING}Waiting for server to start...{Colors.ENDC}")
    
    # Wait for server to start
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(1)
        if check_server_health():
            print(f"{Colors.OKGREEN}✓ Server is now running!{Colors.ENDC}")
            break
    else:
        print(f"{Colors.FAIL}\nError: Could not connect to the server after {max_attempts} seconds{Colors.ENDC}")
        sys.exit(1)

test_user = {
    'email': TEST_EMAIL,
    'password': TEST_PASSWORD,
    're_password': TEST_PASSWORD,
    'first_name': 'Test',
    'last_name': 'User',
    'type': 'S',  # Student
    'gender': 'M',
    'phone': '+1234567890',
    'date_of_birth': '2000-01-01'
}

# Test data for programs
TEST_PROGRAM = {
    'title': 'Test Program',
    'description': 'This is a test program',
    'duration': '6 months',
    'location': 'Online',
    'start_date': '2024-01-01',
    'end_date': '2024-06-30',
    'deadline': '2023-12-31',
    'eligibility': 'Open to all',
    'benefits': 'Certificate, Mentorship',
    'requirements': 'Basic programming knowledge',
    'application_process': 'Online application',
    'is_active': True,
    'max_participants': 50,
    'cost': 0.00,
    'program_type': 'workshop',
    'contact_email': 'programs@example.com',
    'website': 'https://example.com/program'
}

# Global variables to track created resources
created_resources = {
    'programs': []
}

# ==========================================
# Helper Functions
# ==========================================
class Colors:
    """ANSI color codes for console output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_success(message: str) -> None:
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message: str, response=None) -> None:
    """Print error message with optional response details"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
    if response is not None:
        try:
            print(f"Status Code: {response.status_code}")
            print("Response:", json.dumps(response.json(), indent=2))
        except:
            print("Response:", response.text)

def print_info(message: str) -> None:
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def get_auth_headers(token: Optional[str] = None) -> Dict[str, str]:
    """Get authentication headers with JWT token if provided"""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    if token:
        headers['Authorization'] = f'JWT {token}'
    return headers

def make_request(method: str, endpoint: str, token: str = None, data: Any = None) -> Tuple[bool, Any]:
    """Make an HTTP request and handle errors"""
    # Ensure endpoint doesn't start with a slash
    if endpoint.startswith('/'):
        endpoint = endpoint[1:]
    
    # Remove any trailing slashes from BASE_URL
    base_url = BASE_URL.rstrip('/') + '/'
    url = urljoin(base_url, endpoint)
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if token:
        headers['Authorization'] = f'JWT {token}'
    
    try:
        # First, get CSRF token if this is a POST request
        if method.upper() in ['POST', 'PUT', 'DELETE']:
            csrf_response = requests.get(urljoin(BASE_URL, 'csrf/'))
            if csrf_response.status_code == 200:
                csrf_token = csrf_response.cookies.get('csrftoken')
                if csrf_token:
                    headers['X-CSRFToken'] = csrf_token
    
        # Make the actual request
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            print_error(f"Unsupported HTTP method: {method}")
            return False, None
        
        # Log the response for debugging
        print_info(f"{method} {url} - Status: {response.status_code}")
        if response.status_code >= 400:
            print_error(f"Request failed with status {response.status_code}", response)
            
        return (True, response) if response.status_code < 400 else (False, response)
        
    except Exception as e:
        print_error(f"Request failed: {method} {url} - {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request exception: {str(e)}")
        return False, None

# ==========================================
# Authentication Functions
# ==========================================
def register_test_user() -> bool:
    """Register a test user"""
    print_info("Registering test user...")
    success, response = make_request(
        'POST',
        'auth/users/',
        data=test_user
    )
    
    if success:
        print_success("Test user registered successfully")
        # Wait a bit for user to be created
        time.sleep(2)
        return True
    else:
        # Check if user already exists
        if response and 'email' in response.json() and 'already exists' in str(response.json()['email']):
            print_info("Test user already exists, continuing...")
            return True
        return False

def test_user_registration_and_authentication():
    """Test user registration and authentication
    
    Returns:
        Tuple[bool, Optional[str]]: (success, token)
    """
    print_info("\n=== Starting Authentication Test ===")
    
    # Register a new test user
    print_info("Attempting to register test user...")
    success, response = make_request('POST', 'auth/users/', data=test_user)
    
    if not success:
        print_error("Failed to register test user")
        if response and hasattr(response, 'status_code'):
            print_error(f"Status code: {response.status_code}")
            try:
                error_data = response.json()
                print_error("Error details:", json.dumps(error_data, indent=2))
            except:
                print_error("Response content:", response.text[:500])
        return False, None
    
    print_success("✓ Test user registered successfully")
    
    # Get authentication token
    print_info("Attempting to get authentication token...")
    auth_data = {
        'email': test_user['email'],
        'password': test_user['password']
    }
    print_info(f"Auth data: {auth_data}")
    
    success, response = make_request('POST', 'auth/jwt/create/', data=auth_data)
    
    if not success:
        print_error("Failed to get authentication token")
        if response and hasattr(response, 'status_code'):
            print_error(f"Status code: {response.status_code}")
            try:
                error_data = response.json()
                print_error("Error details:", json.dumps(error_data, indent=2))
            except:
                print_error("Response content:", response.text[:500])
        return False, None
    
    # Debug: Print the response to see what we're getting
    print_info(f"Auth response: {response}")
    
    # Handle different response formats
    if isinstance(response, dict):
        token_data = response
    elif hasattr(response, 'json') and callable(response.json):
        try:
            token_data = response.json()
        except:
            token_data = {}
    else:
        token_data = {}
    
    if 'access' not in token_data:
        print_error("No 'access' token in response")
        print_error("Response content:", response)
        return False, None
    
    token = token_data['access']
    print_success("✓ Authentication successful")
    print_info(f"Token: {token[:50]}...")
    return True, token

def test_programs_api(token: str) -> bool:
    """Test programs endpoints (read-only operations)"""
    print("\n=== Testing Programs API (Read-Only) ===")
    
    # 1. Test getting all programs
    print_info("Fetching all programs...")
    success, response = make_request('GET', 'programs/', token)
    if not success:
        return False
    
    programs_data = response.json()
    
    # Check if the response is paginated (has 'results' key) or a direct list
    if isinstance(programs_data, dict) and 'results' in programs_data:
        programs = programs_data['results']
        count = programs_data.get('count', len(programs))
    else:
        programs = programs_data if isinstance(programs_data, list) else []
        count = len(programs)
    
    print_success(f"Successfully fetched {count} programs")
    
    if programs:
        # Get the first program's ID from the results
        first_program = programs[0] if isinstance(programs, list) and len(programs) > 0 else None
        
        if first_program and 'id' in first_program:
            program_id = first_program['id']
            print_info(f"Fetching program with ID: {program_id}")
            success, response = make_request('GET', f'programs/{program_id}/', token)
            if not success:
                return False
            
            program = response.json()
            program_title = program.get('title', 'Untitled Program')
            print_success(f"Successfully fetched program: {program_title}")
            
            # Test program search if we have a title
            if program_title != 'Untitled Program':
                search_term = program_title.split()[0]
                print_info(f"Searching for programs with term: {search_term}")
                success, response = make_request(
                    'GET', 
                    f'programs/?search={search_term}', 
                    token
                )
                if success:
                    search_data = response.json()
                    if isinstance(search_data, dict) and 'results' in search_data:
                        search_count = len(search_data['results'])
                    else:
                        search_count = len(search_data) if isinstance(search_data, list) else 0
                    print_success(f"Found {search_count} matching programs")
                else:
                    print_info("Search test skipped due to error")
        else:
            print_info("No valid program ID found in the response")
    else:
        print_info("No programs found in the system")
    
    return True

def test_newsletter_api() -> bool:
    """Test newsletter subscription endpoints"""
    print("\n=== Testing Newsletter API ===")
    
    try:
        # Generate a unique email for testing
        test_email = f"test_newsletter_{int(time.time())}@example.com"
        
        # 1. Test subscribing to the newsletter
        print_info(f"Subscribing to newsletter with email: {test_email}")
        subscribe_data = {
            'email': test_email,
            'name': 'Test User',
            'is_active': True  # Add if your model requires this field
        }
        
        # Test successful subscription
        success, response = make_request('POST', 'newsletter-subscriptions/', None, subscribe_data)
        if not success:
            print_error(f"Failed to subscribe to newsletter. Status code: {response.status_code if response else 'N/A'}")
            if response:
                try:
                    error_data = response.json()
                    print_error(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print_error(f"Response: {response.text}")
            return False
        
        # Check response format
        try:
            response_data = response.json()
            if response_data.get('status') != 'success':
                print_error(f"Unexpected status in response: {response_data.get('status')}")
                return False
                
            print_success(f"Successfully subscribed with email: {test_email}")
            print_info(f"Response: {json.dumps(response_data, indent=2)}")
            
        except Exception as e:
            print_error(f"Error processing response: {str(e)}")
            return False
        
        # Test duplicate subscription
        print_info("Testing duplicate subscription...")
        success, response = make_request('POST', 'newsletter-subscriptions/', None, subscribe_data)
        if not success or (response and response.status_code != 201):
            print_error(f"Duplicate subscription test failed: Expected status code 201, got {response.status_code if response else 'N/A'}")
            if response:
                print_info(f"Response: {response.text}")
            return False

        print_success("Duplicate subscription test passed")
        
        # Test invalid email
        print_info("Testing invalid email...")
        invalid_email_data = {'email': 'not-an-email'}
        success, response = make_request('POST', 'newsletter-subscriptions/', None, invalid_email_data)
        
        if success or (response and response.status_code != 400):
            print_error("Invalid email test failed: Expected 400 error for invalid email")
            return False
            
        print_success("Invalid email test passed")
        
        # Test missing email
        print_info("Testing missing email...")
        missing_email_data = {}
        success, response = make_request('POST', 'newsletter-subscriptions/', None, missing_email_data)
        
        if success or (response and response.status_code != 400):
            print_error("Missing email test failed: Expected 400 error for missing email")
            return False
            
        print_success("Missing email test passed")
        
        # Note: The confirmation endpoint would be tested separately with a real email
        # as it requires a valid confirmation code that's sent via email
        
        return True
        
    except Exception as e:
        print_error(f"Unexpected error in newsletter test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_contact_api() -> bool:
    """Test contact us/message endpoints"""
    print("\n=== Testing Contact API ===")
    
    try:
        # 1. Test sending a contact message
        test_email = f"test_contact_{int(time.time())}@example.com"
        print_info(f"Sending a contact message from {test_email}...")
        
        # Simplified message data with only required fields
        message_data = {
            'name': 'Test User',
            'email': test_email,
            'subject': f'Test Message {int(time.time())}',
            'message': 'This is a test message from the API test suite.',
            # 'phone': '+1234567890'
        }
        
        # Test with the contact/ endpoint
        success, response = make_request('POST', 'contact/', None, message_data)
        
        if not success or (response and response.status_code != 201):
            status_code = response.status_code if response else 'N/A'
            print_error(f"Failed to send contact message. Status code: {status_code}")
            if response:
                try:
                    error_data = response.json()
                    print_error(f"Error details: {json.dumps(error_data, indent=2)}")
                    
                    # Print more detailed error if available
                    if 'detail' in error_data:
                        print_error(f"Server error detail: {error_data['detail']}")
                    
                except Exception as e:
                    print_error(f"Could not parse error response: {str(e)}")
                    print_error(f"Raw response: {response.text}")
            
            # Print request details for debugging
            print_info("\nRequest details:")
            print_info(f"URL: {response.url if response else 'N/A'}")
            print_info(f"Method: POST")
            print_info(f"Headers: {json.dumps(response.request.headers, indent=2) if response and hasattr(response, 'request') else 'N/A'}")
            print_info(f"Body: {json.dumps(message_data, indent=2)}")
            
            return False
        
        # Check response format
        try:
            response_data = response.json()
            print_success("Successfully sent contact message")
            
            # Validate response structure
            if response_data.get('status') != 'success':
                print_error(f"Unexpected response status: {response_data.get('status')}")
                return False
                
            if 'data' not in response_data or 'id' not in response_data.get('data', {}):
                print_error("Missing expected fields in response")
                return False
                
            print_info(f"Message created with ID: {response_data['data']['id']}")
            
        except Exception as e:
            print_error(f"Error processing response: {str(e)}")
            return False
        
        # Test validation - missing required fields
        print_info("Testing validation - missing required fields...")
        invalid_data = {'name': 'Test User'}  # Missing email and message
        success, response = make_request('POST', 'contact/', None, invalid_data)
        
        if success or (response and response.status_code != 400):
            print_error("Validation failed: Expected 400 error for missing required fields")
            return False
            
        print_success("Validation test passed")
        
        return True
        
    except Exception as e:
        print_error(f"Unexpected error in contact test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_resources(token: str) -> None:
    """Clean up test resources"""
    print("\n=== Test Cleanup ===")
    print_info("No test resources to clean up (read-only mode)")

def main():
    """Main test function"""
    print(f"=== Starting API Tests ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    
    # Run authentication tests
    print("\n=== Testing Authentication ===")
    auth_success, token = test_user_registration_and_authentication()
    if not auth_success:
        print_error("Authentication tests failed. Exiting...")
        sys.exit(1)
    
    # Run API tests
    test_results = {
        'Programs API': test_programs_api(token),
        'Newsletter API': test_newsletter_api(),
        'Contact API': test_contact_api()
    }
    
    # Clean up resources
    cleanup_resources(token)
    
    # Print test summary
    print("\n=== Test Summary ===")
    all_passed = True
    
    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        color = Colors.OKGREEN if result else Colors.FAIL
        print(f"{test_name}: {color}{status}{Colors.ENDC}")
        if not result:
            all_passed = False
    
    # Exit with appropriate status code
    if all_passed:
        print(f"\n{Colors.OKGREEN}All tests passed successfully!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}Some tests failed!{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
