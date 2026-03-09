import argparse
import importlib
import pkgutil
import sys

def main():
    parser = argparse.ArgumentParser(description="Computational Geometry CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    import compgeom.cli
    
    # Map from user-facing command name to module name
    command_to_module = {}
    
    for _, module_name, _ in pkgutil.iter_modules(compgeom.cli.__path__):
        if module_name == "main" or module_name == "__init__":
            continue
            
        # If module ends in _cli, strip it for the user-facing command
        if module_name.endswith("_cli"):
            cmd_name = module_name[:-4]
        else:
            cmd_name = module_name
            
        command_to_module[cmd_name] = module_name
        subparsers.add_parser(cmd_name, help=f"Run {cmd_name} utility")
        
    args, unknown = parser.parse_known_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
        
    real_module_name = command_to_module.get(args.command, args.command)
    module = importlib.import_module(f"compgeom.cli.{real_module_name}")
    
    # Pass along unknown arguments so that scripts that parse argv still work
    sys.argv = [sys.argv[0] + " " + args.command] + unknown
    
    if hasattr(module, "main"):
        module.main()
    else:
        print(f"Error: {args.command} does not have a main() function in module {real_module_name}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
