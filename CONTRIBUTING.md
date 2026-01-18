# Contributing to Concord Camera Documentation

Thank you for your interest in contributing to this reverse engineering documentation project!

## How to Contribute

### Reporting Issues

If you discover:
- New API endpoints
- Different firmware versions with varying behavior
- Solutions or workarounds for the RTSP issue
- Errors in the documentation
- Security vulnerabilities

Please open an issue with:
- Camera model and firmware version
- Detailed description of the finding
- Steps to reproduce (if applicable)
- Example code or API calls

### Adding Documentation

We welcome contributions to improve this documentation:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-endpoint`
3. **Make your changes**
4. **Test your changes** with actual camera hardware if possible
5. **Commit with clear messages**: `git commit -m "Add documentation for audio endpoint"`
6. **Push to your fork**: `git push origin feature/new-endpoint`
7. **Open a Pull Request**

### Documentation Standards

- Use clear, concise language
- Include code examples where helpful
- Test API calls before documenting
- Note firmware version compatibility if known
- Follow existing formatting conventions

### API Documentation Format

When documenting new endpoints, use this format:

```markdown
#### Endpoint Name

GET/POST /api/v1/path/to/endpoint

**Authentication**: Required/Optional

**Parameters:**
- `param1`: Description

**Request Body:** (for POST)
```json
{
  "key": "value"
}
```

**Response:**
```json
{
  "result": 0,
  "data": {}
}
```

**Example:**
```bash
curl -u admin: http://192.168.1.10/api/v1/path/to/endpoint
```
```

### Python Code Contributions

- Follow PEP 8 style guidelines
- Add docstrings for all functions
- Include type hints
- Test with Python 3.7+
- Update CLI help text if adding commands

### RTSP Issue Solutions

If you discover a workaround or solution for the RTSP issue:

1. Test thoroughly with multiple players/recorders
2. Document hardware/software versions
3. Provide step-by-step instructions
4. Include code examples
5. Note any limitations

## Testing

Before submitting:

- Test with actual camera hardware
- Verify API endpoints work as documented
- Check Python code runs without errors
- Validate JSON examples are valid
- Test CLI commands

## Firmware Versions

When documenting, please note the firmware version:
- Check via: `GET /api/v1/system/info`
- Include in documentation if behavior differs

## Security

**DO NOT** include:
- Actual passwords or credentials
- Real IP addresses (use examples like 192.168.1.10)
- Personal information
- Exploits without responsible disclosure

If you discover a security vulnerability:
1. Do NOT open a public issue
2. Contact maintainers privately
3. Allow time for coordinated disclosure

## Code of Conduct

- Be respectful and constructive
- Focus on technical merit
- Help newcomers
- Assume good faith
- Keep discussions on-topic

## Questions?

Open a discussion or issue for:
- Clarification on documentation
- Help with reverse engineering
- Feature requests
- General questions

## Legal

- Only document through legal reverse engineering methods
- Respect intellectual property
- Do not violate terms of service
- Contributions must be your own work
- By contributing, you agree to MIT license

## Recognition

Contributors will be acknowledged in:
- README.md
- Release notes
- Documentation

Thank you for helping improve camera interoperability!
