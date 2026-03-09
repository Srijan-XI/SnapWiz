# Contributing to Linux Package Installer

Thank you for considering contributing to Linux Package Installer! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and professional in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear descriptive title**
- **Detailed steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Screenshots** (if applicable)
- **System information**:
  - Linux distribution and version
  - Python version
  - PyQt5 version
  - Package manager being used

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear descriptive title**
- **Detailed description** of the proposed functionality
- **Use cases** explaining why this enhancement would be useful
- **Possible implementation** (if you have ideas)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - Follow the coding style guidelines below
   - Add tests if applicable
   - Update documentation as needed
3. **Test your changes**:
   - Test on multiple Linux distributions if possible
   - Ensure existing functionality still works
4. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Reference issues and pull requests when relevant
5. **Push to your fork** and submit a pull request

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/linux-package-installer.git
cd linux-package-installer
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Coding Style Guidelines

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all functions and classes

### Example:

```python
def install_package(self, package_path):
    """
    Install the package using appropriate package manager
    
    Args:
        package_path (str): Path to the package file
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Implementation here
    pass
```

### PyQt5 Guidelines

- Keep UI code in the main.py file
- Separate business logic into appropriate modules
- Use Qt signals and slots properly
- Don't block the UI thread - use QThread for long operations

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests after the first line

Examples:
```
Add support for Snap packages

Fixes #123
```

## Testing

Currently, the project doesn't have automated tests, but manual testing is essential:

### Manual Testing Checklist

- [ ] Test with .deb packages on Debian/Ubuntu
- [ ] Test with .rpm packages on Fedora/RHEL
- [ ] Test package info extraction
- [ ] Test installation progress tracking
- [ ] Test error handling for invalid packages
- [ ] Test history logging
- [ ] Test on multiple Linux distributions
- [ ] Test with different Qt themes

## Project Structure

```
linux-package-installer/
├── main.py              # Main application and GUI
├── package_handler.py   # Package operations
├── logger.py            # Logging functionality
├── requirements.txt     # Python dependencies
├── setup.py            # Package setup
├── install.sh          # Installation script
├── README.md           # Project documentation
├── CONTRIBUTING.md     # This file
└── LICENSE             # MIT License
```

## Adding New Features

When adding new features:

1. **Discuss first**: Open an issue to discuss major changes
2. **Plan the changes**: Think about how it fits with existing code
3. **Keep it simple**: Follow the KISS principle
4. **Document**: Update README.md and add docstrings
5. **Test thoroughly**: Test on multiple distributions

### Feature Priorities

High priority features:
- Multi-language support
- Package uninstallation
- Batch installation

Medium priority:
- Dark theme
- Export reports
- Package verification

Low priority:
- Additional package formats (Snap, Flatpak)
- Repository management

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add comments for complex logic
- Update CONTRIBUTING.md if development process changes

## Questions?

Feel free to:
- Open an issue with the "question" label
- Contact the maintainers
- Check existing issues and pull requests

## Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes
- GitHub contributors page

Thank you for contributing to make Linux more accessible to beginners! 🎉
