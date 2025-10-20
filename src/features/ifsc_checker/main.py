import requests
import re
from typing import Dict, Any

def validate_ifsc_format(ifsc_code: str) -> bool:
    """
    Validate IFSC code format using regex.
    Format: 4 letters + 0 + 6 alphanumeric characters
    """
    if ifsc_code is None:
        return False
        
    # Standard IFSC format regex
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    return bool(re.match(pattern, ifsc_code.upper()))

def check_ifsc_exists(ifsc_code: str) -> Dict[str, Any]:
    """
    Check if a valid IFSC code exists via the Razorpay API.
    
    Args:
        ifsc_code: 11-character IFSC code string (already validated for format).
        
    Returns:
        dict: {'status': 'success'/'error', 'message': str, 'data': dict or None}
    """
    ifsc_code = ifsc_code.upper().strip()
    
    url = f"https://ifsc.razorpay.com/{ifsc_code}"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Ensure the response structure is valid (sometimes 200 returns an error message)
            if 'IFSC' in data and data['IFSC'] == ifsc_code:
                 return {
                    'status': 'success',
                    'message': f"IFSC code found for {data.get('BANK', 'Unknown Bank')}.",
                    'data': data
                }
            else:
                # Handle cases where the API returns 200 but the data is empty/error
                 return {
                    'status': 'error',
                    'message': 'IFSC code found, but returned invalid/empty data.',
                    'data': response.json()
                }

        elif response.status_code == 404:
            return {
                'status': 'error',
                'message': 'IFSC code not found in the database.',
                'data': None
            }
        else:
            return {
                'status': 'error',
                'message': f'API connection error: Status {response.status_code}',
                'data': None
            }
            
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': 'Request timed out while contacting the API.',
            'data': None
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'Connection error: {str(e)}',
            'data': None
        }