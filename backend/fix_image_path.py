import os

# Read the current file
with open('app_simple.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The old buggy code
old_code = '''            # Convert image_path to image URL for frontend
            if 'image_path' in alert and alert['image_path']:
                image_path = alert['image_path']
                # Convert absolute path to relative path if needed
                if 'storage' in image_path:
                    # Extract path after 'storage/'
                    relative_path = image_path.split('storage/')[-1].replace('\\\\', '/')
                    alert['image'] = f'http://localhost:{PORT}/api/storage/image/{relative_path}'
                else:
                    alert['image'] = image_path'''

# The new fixed code
new_code = '''            # Convert image_path to image URL for frontend
            if 'image_path' in alert and alert['image_path']:
                image_path = alert['image_path']
                
                # If already a full URL, keep it
                if image_path.startswith('http'):
                    alert['image'] = image_path
                elif 'storage' in image_path.lower():
                    # FIRST normalize path (backslashes to forward slashes)
                    normalized = image_path.replace('\\\\', '/')
                    # THEN split and get part after 'storage/'
                    parts = normalized.split('storage/')
                    relative_path = parts[-1] if len(parts) > 1 and parts[-1] else normalized
                    alert['image'] = f'http://localhost:{PORT}/api/storage/image/{relative_path}'
                else:
                    alert['image'] = f'http://localhost:{PORT}/api/storage/image/{image_path}' '''

# Replace
if old_code in content:
    content = content.replace(old_code, new_code)
    with open('app_simple.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print(' File patched successfully!')
else:
    print(' Could not find the code to replace')
    print('File might already be patched or has different formatting')
