# PreCICE Structure Generator

## Project Overview

The PreCICE Structure Generator is a Python-based utility designed to automate the generation of preCICE configuration files from YAML topology descriptions. This tool simplifies the process of setting up multi-physics simulations by transforming user-defined YAML configurations into preCICE-compatible XML configuration files.

## Key Features

- Automated preCICE configuration generation
- YAML-based input parsing
- Flexible topology description support
- Comprehensive error logging and handling
- Simple command-line interface

## Prerequisites

- Python 3.7+
- preCICE library
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-organization/precice-structure-generator.git
cd precice-structure-generator
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Interface

Generate a preCICE configuration file from a YAML topology:

```bash
python FileGenerator.py -f path/to/your/topology.yaml
```

### Configuration

1. Prepare a YAML topology file describing your multi-physics simulation setup.
2. Use the command-line interface to generate the preCICE configuration.
3. The tool will create the necessary configuration files in the `_generated/` directory.

## Dependencies

- myutils==0.0.21
- pyaml==24.9.0
- PyYAML==6.0.2
- termcolor==2.5.0

## Project Structure

```
precice-structure-generator/
│
├── FileGenerator.py         # Main script for configuration generation
├── requirements.txt         # Project dependencies
├── _generated/              # Output directory for generated files
├── controller/              # Controller modules
│   ├── ui_struct/           # User interface handling
│   ├── myutils/             # Utility modules
│   └── precice_struct/      # preCICE configuration modules
├── generation_utils/        # Utility modules for file generation
└── README.md                # Project documentation
```

## Logging and Error Handling

The tool provides detailed logging to help you understand the configuration generation process:
- Tracks input YAML file details
- Validates user input
- Generates comprehensive error messages
- Supports troubleshooting configuration issues

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## Troubleshooting

- Ensure all dependencies are correctly installed
- Verify the format of your input YAML file
- Check the generated logs for detailed error information

## License

[Specify your project's license]

## Contact

[Add contact information or project maintainer details]

## Acknowledgements

[Optional: Mention any contributors, funding sources, or related projects]
