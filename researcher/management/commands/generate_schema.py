import os
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate database schema diagram for the Company Research application'

    def add_arguments(self, parser):
        parser.add_argument('--output', '-o', default='schema', help='Output file name without extension')
        parser.add_argument('--format', '-f', default='png', choices=['png', 'pdf', 'svg', 'dot'],
                           help='Output file format')

    def handle(self, *args, **options):
        try:
            import sadisplay
            import pydot
        except ImportError:
            self.stdout.write(self.style.ERROR(
                'Error: sadisplay and pydot packages are required. Please install them with:\n'
                'pip install sadisplay pydot'
            ))
            return

        output_file = options['output']
        format_type = options['format']
        
        self.stdout.write(f"Generating database schema diagram...")
        
        # Get all models from the 'researcher' app
        models = []
        for model in apps.get_app_config('researcher').get_models():
            models.append(model)
        
        # Add User model
        from django.contrib.auth.models import User
        models.append(User)
        
        self.stdout.write(f"Found {len(models)} models")
        
        # Generate schema description
        desc = sadisplay.describe(models, show_methods=False, show_properties=False)
        
        # Create diagram
        if format_type == 'dot':
            with open(f"{output_file}.dot", 'w') as f:
                f.write(sadisplay.dot(desc))
            self.stdout.write(self.style.SUCCESS(f"Generated {output_file}.dot"))
        else:
            dot_file = f"{output_file}.dot"
            with open(dot_file, 'w') as f:
                f.write(sadisplay.dot(desc))
            
            try:
                graph, = pydot.graph_from_dot_file(dot_file)
                graph.write(f"{output_file}.{format_type}", format=format_type)
                self.stdout.write(self.style.SUCCESS(f"Generated {output_file}.{format_type}"))
                
                # Clean up the .dot file unless dot format was requested
                if os.path.exists(dot_file):
                    os.remove(dot_file)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error generating {format_type} file: {e}"))
                self.stdout.write(f"DOT file was generated at {dot_file}")
        
        self.stdout.write(self.style.SUCCESS("\nCompleted generating database schema diagram."))
        self.stdout.write("\nNote: If you're seeing errors with graphviz, make sure graphviz is installed:")
        self.stdout.write("  apt-get install graphviz  # on Debian/Ubuntu")
        self.stdout.write("  brew install graphviz     # on macOS with Homebrew") 