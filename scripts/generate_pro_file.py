
import glob
import pathlib
from jinja2 import Template


PROJECT_DIR = pathlib.Path(__file__).parent.parent

# Use glob to dynamically collect source and translation files
source_pattern = '**/*.py'  # Pattern for source files
translation_pattern = 'resource/i18n/*.ts'  # Pattern for translation files

# Collect source files (matching .py files under app/view/)
sources = [pathlib.Path(p).as_posix() for p in glob.glob(source_pattern, root_dir=PROJECT_DIR, recursive=True)]

# Collect translation files (matching .ts files under app/resource/i18n/)
translations = [pathlib.Path(p).as_posix() for p in glob.glob(translation_pattern, root_dir=PROJECT_DIR)]

# Define the Jinja2 template for the .pro file
pro_template = """SOURCES += \\
{%- for source in sources %}
    {{ source }}{% if not loop.last %} \\{% endif %}
{%- endfor %}

TRANSLATIONS += \\
{%- for translation in translations %}
    {{ translation }}{% if not loop.last %} \\{% endif %}
{%- endfor %}
"""

# Create a Jinja2 Template object
template = Template(pro_template)

# Render the template with the sources and translations data
output = template.render(sources=sources, translations=translations)

# Save the rendered output to a .pro file
with open(PROJECT_DIR / 'py661.pro', 'w') as f:
    f.write(output)

print("Successfully generated the [dim].pro[/dim] file: /simpleacct.pro")
print("Next, you can run /scripts/make_i18n_files.bat to automatically "
              "generate the [dim].ts[/dim] and [dim].qm[/dim] files.")