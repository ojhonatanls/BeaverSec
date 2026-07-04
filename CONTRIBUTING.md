Contributing to BeaverSec
==========================

Thank you for your interest in contributing to BeaverSec.

Code Style
----------

- Follow PEP8 guidelines strictly
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names

Docstrings
----------

All functions, classes, and modules must have docstrings.

Example:

    def validate_port(port: int) -> bool:
        """Validate if port number is within valid range.
        
        Args:
            port: Port number to validate
            
        Returns:
            bool: True if valid (1-65535), False otherwise
        """
        return 1 <= port <= 65535

Commits
-------

Use conventional commit format:

    fix: description of bug fix
    feat: description of new feature
    docs: documentation changes
    test: test changes
    chore: maintenance tasks

Example:

    fix: add port validation to CLI
    docs: rewrite README
    test: add unit tests for security module

Testing
-------

All code changes must include tests. Run tests before submitting:

    $ pytest -q

Writing Tests:

- Place test files in tests/ directory
- Use descriptive test function names
- Test both success and failure cases
- Use mocks for external dependencies

Pull Requests
-------------

1. Fork the repository
2. Create a feature branch: git checkout -b feature/description
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: pytest
6. Commit with conventional format
7. Push to your fork
8. Open a pull request with clear description

Code Review
-----------

All pull requests will be reviewed for:
- Code style and PEP8 compliance
- Test coverage
- Documentation
- Security implications
- Compatibility with Python 3.8+

Issues
------

Before starting work:
- Check existing issues to avoid duplicates
- Look for "good first issue" labels for beginners
- Comment on the issue to indicate you'll work on it
- Ask questions in the issue if needed

Licensing
---------

By contributing, you agree that your code will be licensed under the MIT License.

Questions?
----------

Open an issue or ask in pull request comments. We're here to help!
