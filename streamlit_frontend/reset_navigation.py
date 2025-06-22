"""
Script to reset navigation state and ensure consistent navigation across all pages.
Run this once after updating navigation functionality.
"""
import os
import json
import shutil
import sys

def add_navigation_to_page(file_path):
    """Update a page file to use the navigation module"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file already has navigation import
    if 'from lib.navigation import display_sidebar_navigation' in content:
        print(f"✅ {file_path} already has navigation import")
        return False
    
    # Add import for navigation
    import_line = 'from lib.navigation import display_sidebar_navigation'
    if 'import' in content and '# Import' in content:
        # Add after last import statement
        lines = content.split('\n')
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_idx = i
        
        lines.insert(last_import_idx + 1, import_line)
        
        # Find authentication check and add navigation display
        auth_check_idx = None
        for i, line in enumerate(lines):
            if 'authenticated' in line and 'session_state' in line and ('=' in line or 'if' in line):
                auth_check_idx = i
                break
        
        if auth_check_idx:
            # Find the end of the authentication block
            for i in range(auth_check_idx, len(lines)):
                if lines[i].strip().startswith('# ') or lines[i].strip() == '':
                    # Add navigation display before this line
                    indent = ' ' * 4  # Assuming 4 spaces indentation
                    lines.insert(i, f"{indent}# Display navigation sidebar")
                    lines.insert(i + 1, f"{indent}display_sidebar_navigation()")
                    lines.insert(i + 2, '')
                    break
        
        # Update file content
        updated_content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated {file_path} with navigation")
        return True
    else:
        print(f"❌ Could not update {file_path} - no import section found")
        return False

def main():
    """Main function to reset navigation"""
    print("Resetting navigation in all pages...")
    
    # Get the pages directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pages_dir = os.path.join(script_dir, 'pages')
    
    if not os.path.exists(pages_dir):
        print(f"❌ Pages directory not found at {pages_dir}")
        return
    
    # Update all Python files in pages directory
    updated_count = 0
    for filename in os.listdir(pages_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(pages_dir, filename)
            if add_navigation_to_page(file_path):
                updated_count += 1
    
    print(f"✅ Navigation reset complete. Updated {updated_count} page files.")
    
    # Create streamlit_config.toml to ensure consistent sidebar behavior
    config_dir = os.path.join(script_dir, '.streamlit')
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, 'config.toml')
    with open(config_path, 'w') as f:
        f.write("""
[theme]
primaryColor="#3b82f6"
backgroundColor="#111827"
secondaryBackgroundColor="#1e293b"
textColor="#f8fafc"
font="sans serif"

[server]
enableStaticServing = true
enableCORS = true
enableXsrfProtection = false

[browser]
serverAddress = "localhost"
gatherUsageStats = false
        """)
    
    print(f"✅ Created Streamlit config at {config_path}")
    
    print("♻️ Please restart Streamlit server for changes to take effect")

if __name__ == "__main__":
    main() 