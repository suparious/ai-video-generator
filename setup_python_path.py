import os
import site
import sys

def setup_python_path():
    """Add the virtual environment site-packages to Python's path."""
    venv_path = '/app/venv'
    if os.path.exists(venv_path):
        # Get Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        site_packages = os.path.join(venv_path, 'lib', f'python{python_version}', 'site-packages')
        
        # Make sure the site-packages directory exists
        if os.path.exists(site_packages):
            # Only add if not already there
            if site_packages not in sys.path:
                sys.path.insert(0, site_packages)
                print(f"Added {site_packages} to Python path")
            else:
                print(f"{site_packages} already in Python path")
        else:
            print(f"Warning: Site packages directory {site_packages} not found")
            
            # Try different directory structures that might exist in Docker
            alternative_paths = [
                os.path.join(venv_path, 'lib', 'python3', 'site-packages'),
                os.path.join(venv_path, 'lib', 'site-packages'),
                os.path.join(venv_path, 'lib64', f'python{python_version}', 'site-packages'),
                os.path.join('/usr/local/lib', f'python{python_version}', 'site-packages'),
                os.path.join('/usr/local/lib', 'site-packages')
            ]
            
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    sys.path.insert(0, alt_path)
                    print(f"Added alternative path {alt_path} to Python path")
            
            # Try to locate site-packages through other means
            all_site_packages = site.getsitepackages()
            print(f"Available site-packages: {all_site_packages}")
            
            # Add all available site-packages to path for redundancy
            for path in all_site_packages:
                if path not in sys.path:
                    sys.path.insert(0, path)
                    print(f"Added {path} to Python path")
    
    # Add the app directory to the path
    app_dir = '/app'
    if os.path.exists(app_dir) and app_dir not in sys.path:
        sys.path.insert(0, app_dir)
        print(f"Added {app_dir} to Python path")
        
    # Print the current Python path for debugging
    print("\nFinal Python sys.path:")
    for path in sys.path:
        print(f"  - {path}")

# Run setup when the module is imported
setup_python_path()
