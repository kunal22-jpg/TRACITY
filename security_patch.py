"""
Security patch for TRACITY API authentication and file upload system.

This patch fixes the following security issues:
1. Captcha verification is not properly enforced in the login endpoint
2. Authentication is not properly enforced on the upload endpoint
3. Authentication is not properly enforced on the user/files endpoint
4. Authentication is not properly enforced on the user/data endpoint

The patch modifies the following functions:
- login_user: Add proper captcha verification
- upload_file: Ensure authentication is properly enforced
- get_user_files: Ensure authentication is properly enforced
- get_user_file_data: Ensure authentication is properly enforced
"""

import sys
import os
import re

def apply_patch(server_file_path):
    """Apply security patches to the server.py file"""
    try:
        # Read the server.py file
        with open(server_file_path, 'r') as file:
            content = file.read()
        
        # 1. Fix captcha verification in login_user function
        # Find the login_user function
        login_pattern = r'@api_router\.post\("/login", response_model=LoginResponse\)\nasync def login_user\(user_login: UserLogin\):.*?try:.*?# Verify captcha first.*?captcha_key = f"captcha_{user_login\.email}".*?# For simplicity.*?# In production'
        login_match = re.search(login_pattern, content, re.DOTALL)
        
        if login_match:
            # Replace the captcha verification code
            old_captcha_code = login_match.group(0)
            new_captcha_code = old_captcha_code.replace(
                '# Verify captcha first\n        captcha_key = f"captcha_{user_login.email}"  # Using email as captcha session\n        # For simplicity, we\'ll skip strict captcha verification in this demo\n        # In production',
                '# Verify captcha first\n        captcha_key = f"captcha_{user_login.email}"  # Using email as captcha session\n        \n        # Check if captcha session exists and answer is correct\n        if captcha_key not in active_sessions or active_sessions[captcha_key]["answer"] != user_login.captcha_answer:\n            raise HTTPException(status_code=401, detail="Invalid captcha")\n        \n        # In production'
            )
            content = content.replace(old_captcha_code, new_captcha_code)
            print("✅ Fixed captcha verification in login_user function")
        else:
            print("❌ Could not find login_user function to patch")
        
        # 2. Fix authentication in upload_file function
        # The upload_file function already has Depends(verify_token), but it might not be working correctly
        # Let's make sure it's properly implemented
        upload_pattern = r'@api_router\.post\("/upload", response_model=UploadFileResponse\)\nasync def upload_file\(.*?\):'
        upload_match = re.search(upload_pattern, content, re.DOTALL)
        
        if upload_match:
            old_upload_def = upload_match.group(0)
            # Make sure it uses verify_token
            if "Depends(verify_token)" not in old_upload_def:
                new_upload_def = old_upload_def.replace(
                    "async def upload_file(",
                    "async def upload_file(\n    user_data: dict = Depends(verify_token),"
                )
                content = content.replace(old_upload_def, new_upload_def)
                print("✅ Fixed authentication in upload_file function")
            else:
                print("✓ Upload file function already has authentication dependency")
        else:
            print("❌ Could not find upload_file function to patch")
        
        # 3. Fix authentication in get_user_files function
        user_files_pattern = r'@api_router\.get\("/user/files"\)\nasync def get_user_files\(.*?\):'
        user_files_match = re.search(user_files_pattern, content, re.DOTALL)
        
        if user_files_match:
            old_user_files_def = user_files_match.group(0)
            # Make sure it uses verify_token
            if "Depends(verify_token)" not in old_user_files_def:
                new_user_files_def = old_user_files_def.replace(
                    "async def get_user_files(",
                    "async def get_user_files(user_data: dict = Depends(verify_token),"
                )
                content = content.replace(old_user_files_def, new_user_files_def)
                print("✅ Fixed authentication in get_user_files function")
            else:
                print("✓ User files function already has authentication dependency")
        else:
            print("❌ Could not find get_user_files function to patch")
        
        # 4. Fix authentication in get_user_file_data function
        user_file_data_pattern = r'@api_router\.get\("/user/data/{file_id}"\)\nasync def get_user_file_data\(.*?\):'
        user_file_data_match = re.search(user_file_data_pattern, content, re.DOTALL)
        
        if user_file_data_match:
            old_user_file_data_def = user_file_data_match.group(0)
            # Make sure it uses verify_token
            if "Depends(verify_token)" not in old_user_file_data_def:
                new_user_file_data_def = old_user_file_data_def.replace(
                    "async def get_user_file_data(",
                    "async def get_user_file_data(file_id: str, user_data: dict = Depends(verify_token),"
                )
                content = content.replace(old_user_file_data_def, new_user_file_data_def)
                print("✅ Fixed authentication in get_user_file_data function")
            else:
                print("✓ User file data function already has authentication dependency")
        else:
            print("❌ Could not find get_user_file_data function to patch")
        
        # Write the patched content back to the file
        with open(server_file_path, 'w') as file:
            file.write(content)
        
        print("\n✅ Security patch applied successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Error applying security patch: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        server_file_path = sys.argv[1]
    else:
        server_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "server.py")
    
    apply_patch(server_file_path)