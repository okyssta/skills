#!/usr/bin/env python3
"""
Replace 'catalog:' version references in monorepo packages with explicit versions.
Reads catalog from the original root package.json, then walks workspace packages.
Usage: python3 fix-catalog.py <root-dir>
"""
import json, os, sys

def main(root_dir):
    pkg_path = os.path.join(root_dir, "package.json")
    if not os.path.exists(pkg_path):
        print(f"ERROR: {pkg_path} not found")
        sys.exit(1)
    with open(pkg_path) as f:
        root = json.load(f)
    catalog = root.get("workspaces", {}).get("catalog", {})
    if not catalog:
        print("No catalog found")
        sys.exit(1)
    packages = []
    for pattern in root.get("workspaces", {}).get("packages", []):
        base = pattern.replace("/*", "")
        path = os.path.join(root_dir, base)
        if "*" not in pattern:
            if os.path.exists(os.path.join(path, "package.json")):
                packages.append(path)
        else:
            parent = os.path.join(root_dir, os.path.dirname(base))
            if os.path.isdir(parent):
                for child in os.listdir(parent):
                    p = os.path.join(parent, child, "package.json")
                    if os.path.exists(p):
                        packages.append(os.path.join(parent, child))
    total = 0
    for pkg_dir in sorted(packages):
        pkg_json = os.path.join(pkg_dir, "package.json")
        try:
            with open(pkg_json) as f:
                data = json.load(f)
        except:
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
                        print(f"  WARN: {dep} not in catalog, removing")
                        del data[section][dep]
                        changed = True
        if changed:
            with open(pkg_json, 'w') as f:
                json.dump(data, f, indent=2)
            total += 1
    print(f"\nDone. Updated {total} packages.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix-catalog.py <root-dir>")
        sys.exit(1)
    main(sys.argv[1])
