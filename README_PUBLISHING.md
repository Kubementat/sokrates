# How to publish

```
PYPI_API_TOKEN="REPLACEME"

# publish to pypi test instance
uv publish --token "$PYPI_API_TOKEN" --publish-url https://test.pypi.org/legacy/

# publish to prod instance
uv publish --token "$PYPI_API_TOKEN"
```