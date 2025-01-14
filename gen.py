import os
import sys
import inspect
import ruamel.yaml

# Define current and parent directory paths
current_dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_dir_path, 'scripts'))

# Import the main module
from scripts import main

# Initialize the pages dictionary
pages = {
    'sources_dir': 'docs/',
    'templates_dir': None,
    'repo': 'https://github.com/mandeepnh5/autogenerate-docs',
    'version': 'main',
    'pages': []
}

# Ensure the output directory exists
output_dir = os.path.join(current_dir_path, 'docs/')
os.makedirs(output_dir, exist_ok=True)

# Process classes and functions in the main module
for module in [main]:
    last_file = None
    save_old = False
    for name, item in inspect.getmembers(module):
        if inspect.isclass(item):
            file = os.path.relpath(inspect.getfile(item), current_dir_path).replace('scripts/', '')
            page = {
                'page': file.replace('.py', '.md'),
                'source': 'scripts/' + file,
                'classes': [item.__name__]
            }
            pages['pages'].append(page)

            # Generate markdown file for class
            md_file_path = os.path.join(output_dir, page['page'])
            with open(md_file_path, 'w') as md_file:
                md_file.write(f"# Class: {item.__name__}\n\n")
                md_file.write(f"Source: `{page['source']}`\n\n")
                md_file.write(inspect.getdoc(item) or "No class documentation available.\n")

        if inspect.isfunction(item):
            file = os.path.relpath(inspect.getfile(item), current_dir_path).replace('scripts/', '')
            if file == last_file:
                page['functions'].append(item.__name__)
                save_old = False
            else:
                save_old = True
                page = {
                    'page': file.replace('.py', '.md'),
                    'source': 'scripts/' + file,
                    'functions': [item.__name__]
                }

            if save_old:
                pages['pages'].append(page)

            # Generate markdown file for functions
            md_file_path = os.path.join(output_dir, page['page'])
            with open(md_file_path, 'w') as md_file:
                md_file.write(f"# Function: {item.__name__}\n\n")
                md_file.write(f"Source: `{page['source']}`\n\n")
                md_file.write("## Documentation\n\n")
                doc = inspect.getdoc(item)
                if doc:
                    md_file.write(doc + "\n\n")
                else:
                    md_file.write("No documentation available.\n\n")

                # Extract and write arguments
                sig = inspect.signature(item)
                md_file.write("### Arguments\n")
                for param_name, param in sig.parameters.items():
                    md_file.write(f"- **{param_name}**: {param.annotation if param.annotation != inspect.Parameter.empty else 'Unknown'}\n")

                # Write return type
                md_file.write("\n### Returns\n")
                if sig.return_annotation != inspect.Signature.empty:
                    md_file.write(f"- **{sig.return_annotation}**\n")
                else:
                    md_file.write("- **Unknown**\n")

            last_file = file

# Save the generated YAML file
yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)

with open('mkgendocs.yml', 'w') as f:
    yaml.dump(pages, f)
