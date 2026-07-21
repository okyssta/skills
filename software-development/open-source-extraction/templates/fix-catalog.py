#!/usr/bin/env python3
"""
Replace 'catalog:' version references in monorepo packages with explicit versions.
Reads catalog from the original root package.json, then walks workspace packages.

Usage:
  python3 fix-catalog.py <root-dir>

Where <root-dir> contains package.json with workspaces.catalog entries.
"""
import json, os, sys

def main(root_dir):
    # Load root package.json for catalog
    pkg_path = os.path.join(root_dir, "package.json")
    if not os.path.exists(pkg_path):
        print(f"ERROR: {pkg_path} not found")
        sys.exit(1)
    
    with open(pkg_path) as f:
        root = json.load(f)
    
    catalog = root.get("workspaces", {}).get("catalog", {})
    if not catalog:
        print("No catalog found in workspaces section")
        sys.exit(1)
    
    # Discover all workspace packages
    packages = []
    for pattern in root.get("workspaces", {}).get("packages", []):
        base = pattern.replace("/*", "")
        path = os.path.join(root_dir, base)
        if "*" not in pattern:
            if os.path.exists(os.path.join(path, "package.json")):
                packages.append(path)
        else:
            # Glob pattern like "packages/*" or "packages/console/*"
            parent = os.path.join(root_dir, os.path.dirname(base))
            if os.path.isdir(parent):
                for child in os.listdir(parent):
                    child_path = os.path.join(parent, child)
                    pkg_json = os.path.join(child_path, "package.json")
                    if os.path.exists(pkg_json):
                        packages.append(child_path)
    
    total_fixed = 0
    for pkg_dir in sorted(packages):
        pkg_json = os.path.join(pkg_dir, "package.json")
        try:
            with open(pkg_json) as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            continue
        
        changed = False
        for section in ["dependencies", "devDependencies", "peerDependencies"]:
            if section not in data:
                continue
            for dep, ver in list(data[section].items()):
                if ver == "catalog:":
                    if dep in catalog:
                        data[section][dep] = catalog[dep]
                        changed = True
                        rel = os.path.relpath(pkg_json, root_dir)
                        print(f"  {rel}: {dep} -> {catalog[dep]}")
                    else:
                        # Remove unresolvable deps
                        print(f"  WARN: {dep} in {rel} not in catalog, removing")
                        del data[section][dep]
                        changed = True
                        total_fixed += 1
        
        if changed:
            with open(pkg_json, 'w') as f:
                json.dump(data, f, indent=2)
    
    print(f"\nDone. Fixed {total_fixed} catalog references across {len(packages)} packages.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix-catalog.py <root-dir>")
        sys.exit(1)
    main(sys.argv[1])
