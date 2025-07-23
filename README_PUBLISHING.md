# How to publish

```
PYPI_API_TOKEN="REPLACEME"

# publish to pypi test instance
uv publish --index testpypi --token "$PYPI_API_TOKEN"

# publish to prod instance
uv publish --token "$PYPI_API_TOKEN"
```