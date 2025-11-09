# Contributing to CDN Checker

First off, thanks for taking the time to contribute! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (URLs tested, browser used, etc.)
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any examples of similar features in other tools**

### Adding New CDN Providers

To add support for a new CDN provider:

1. Add the CDN signature to the `cdn_signatures` dictionary in `app.py`:

```python
'NewCDN': {
    'headers': ['x-newcdn-header'],
    'cname_patterns': [r'\.newcdn\.'],
    'server_headers': ['newcdn'],
    'domains': ['newcdn.com']
}
```

2. Add an icon for the CDN in `static/js/app.js` in the `getCDNIcon()` function
3. Test with known websites using that CDN
4. Update the README.md to list the new CDN

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

#### Pull Request Guidelines

- Follow the existing code style
- Write clear commit messages
- Update documentation as needed
- Add tests if applicable
- Keep pull requests focused on a single feature/fix

## Code Style

- Use 4 spaces for indentation (Python)
- Use 2 spaces for indentation (JavaScript, HTML, CSS)
- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic

## Testing

Before submitting a pull request:

1. Test the application locally
2. Test with various websites (with and without CDN)
3. Test input validation (invalid URLs, etc.)
4. Test on different browsers if making frontend changes
5. Ensure no errors appear in the console

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing! 🙏
