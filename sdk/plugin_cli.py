import argparse
import json
import os
import sys
import zipfile

def create_plugin(name: str, target_dir: str):
    """Generate boilerplate structure for a new AURA plugin."""
    plugin_dir = os.path.join(target_dir, name)
    os.makedirs(os.path.join(plugin_dir, "tools"), exist_ok=True)
    
    manifest = {
        "id": name.lower().replace(" ", "_"),
        "name": name,
        "version": "1.0.0",
        "description": f"{name} extension plugin for AURA AI OS",
        "author": "Developer",
        "entry_point": "plugin.py",
        "permissions": ["ALWAYS_ALLOWED"]
    }
    
    with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    with open(os.path.join(plugin_dir, "plugin.py"), "w") as f:
        f.write('def initialize_plugin(engine):\n    print(f"Plugin initialized")\n')

    print(f"✅ Plugin template created successfully at: '{plugin_dir}'")

def validate_plugin(plugin_dir: str) -> bool:
    """Validate a plugin manifest and structure."""
    manifest_path = os.path.join(plugin_dir, "plugin.json")
    if not os.path.exists(manifest_path):
        print(f"❌ Validation Error: Missing 'plugin.json' manifest in '{plugin_dir}'")
        return False
    
    try:
        with open(manifest_path, "r") as f:
            data = json.load(f)
        required = ["id", "name", "version", "entry_point"]
        for field in required:
            if field not in data:
                print(f"❌ Validation Error: Missing required field '{field}' in manifest.")
                return False
        print(f"✅ Plugin '{data['name']}' v{data['version']} validation passed cleanly!")
        return True
    except Exception as e:
        print(f"❌ Validation Error: Invalid JSON - {e}")
        return False

def package_plugin(plugin_dir: str, output_dir: str):
    """Package a plugin directory into a distributable archive."""
    if not validate_plugin(plugin_dir):
        sys.exit(1)
    
    manifest_path = os.path.join(plugin_dir, "plugin.json")
    with open(manifest_path, "r") as f:
        data = json.load(f)
        
    os.makedirs(output_dir, exist_ok=True)
    zip_name = f"{data['id']}_v{data['version']}.aura-plugin"
    zip_path = os.path.join(output_dir, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(plugin_dir):
            for file in files:
                rel_file = os.path.relpath(os.path.join(root, file), plugin_dir)
                zipf.write(os.path.join(root, file), rel_file)
                
    print(f"📦 Plugin packaged successfully into: '{zip_path}'")

def main():
    parser = argparse.ArgumentParser(description="AURA AI OS Plugin SDK CLI")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new plugin boilerplate")
    create_parser.add_argument("--name", required=True, help="Plugin Name")
    create_parser.add_argument("--out", default=".", help="Target Directory")

    val_parser = subparsers.add_parser("validate", help="Validate a plugin directory")
    val_parser.add_argument("--dir", required=True, help="Plugin Directory")

    pkg_parser = subparsers.add_parser("package", help="Package a plugin into .aura-plugin archive")
    pkg_parser.add_argument("--dir", required=True, help="Plugin Directory")
    pkg_parser.add_argument("--out", default="dist", help="Output Directory")

    args = parser.parse_args()

    if args.command == "create":
        create_plugin(args.name, args.out)
    elif args.command == "validate":
        validate_plugin(args.dir)
    elif args.command == "package":
        package_plugin(args.dir, args.out)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
