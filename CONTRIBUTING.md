# Contributing to NetCreep

## Code of Conduct
By participating, you are expected to uphold our Code of Conduct.

## Development Setup
1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Set up pre-commit hooks

## Contribution Process
1. Check existing issues
2. Create a new branch
3. Make your changes
4. Write tests
5. Run linters and formatters
6. Submit a pull request

## Contribution Types
- Bug fixes
- Feature enhancements
- Documentation improvements
- Performance optimizations
- Security patches

## Code Quality Standards
- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Maintain 90%+ test coverage
- Use type hints
- Write meaningful commit messages

## Specific Areas of Contribution
### Network Monitoring
- Protocol support
- Packet analysis algorithms
- Anomaly detection improvements

### Security
- Vulnerability patches
- Authentication mechanisms
- Encryption enhancements

### Performance
- Optimize packet processing
- Improve database queries
- Reduce memory footprint

## Reporting Security Issues
- Do not open public issues for security vulnerabilities
- Email security@netcreep.com with details

## Pull Request Process
1. Update documentation
2. Increase version number
3. Obtain approval from maintainers

## Code Review Checklist
- [ ] Follows project coding standards
- [ ] Includes tests
- [ ] Updates documentation
- [ ] Passes all CI checks

## Development Environment
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Run linters
flake8 .
black --check .
isort --check .
```

## Commit Message Guidelines
- Use present tense
- Use imperative mood
- Limit first line to 72 characters
- Reference issues when applicable

Example:
```
Add support for IPv6 packet capture

- Implement IPv6 protocol detection
- Update packet model to handle IPv6
- Add tests for IPv6 packet processing

Fixes #123
```

## Code of Conduct
### Our Pledge
We are committed to providing a friendly, safe, and welcoming environment.

### Expected Behavior
- Be respectful
- Be collaborative
- Provide constructive feedback
- Focus on what is best for the community

### Unacceptable Behavior
- Harassment
- Discriminatory language
- Personal attacks
- Public or private harassment

## Questions?
Contact the maintainers at contribute@netcreep.com
