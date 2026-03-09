import argparse
import importlib
import pkgutil
import sys

def main():
    parser = argparse.ArgumentParser(description="Computational Geometry CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    import compgeom.cli
    
    for _, module_name, _ in pkgutil.iter_modules(compgeom.cli.__path__):
        if module_name == "main":
            continue
        subparsers.add_parser(module_name, help=f"Run {module_name} script")
        
    args, unknown = parser.parse_known_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
        
    module = importlib.import_module(f"compgeom.cli.{args.command}")
    
    # Pass along unknown arguments so that scripts that parse argv still work
    sys.argv = [sys.argv[0] + " " + args.command] + unknown
    
    if hasattr(module, "main"):
        module.main()
    else:
        print(f"Error: {args.command} does not have a main() function.")
        sys.exit(1)

if __name__ == "__main__":
    main()
