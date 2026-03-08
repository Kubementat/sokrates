# How to publish

## Build first

Before publishing, build the distributable packages:

```bash
# Basic version (without voice features)
uv build

# Or with all optional dependencies for voice support
uv pip install -e ".[voice]"
uv build
```

This creates wheel and source distributions in the `dist/` directory. Verify with:

```bash
ls -la dist/
# Should show sokrates-$VERSION-py3-none-any.whl and similar files
```

## Publish to pypi test instance
```
PYPI_API_TOKEN="REPLACEME"

# publish to pypi test instance
uv publish --index testpypi --token "$PYPI_API_TOKEN"

# Test the test package
TEMP_DIR="/tmp/test_sokrates"
mkdir -p $TEMP_DIR

cd $TEMP_DIR
uv venv
source .venv/bin/activate
uv pip install --index-url https://test.pypi.org/simple/ sokrates

# test cli tool
uv run sokrates list-models
uv run sokrates chat
```

## publish to pypi prod instance

```bash
PYPI_API_TOKEN="REPLACEME"
uv publish --token "$PYPI_API_TOKEN"

# Test the published package
TEMP_DIR="/tmp/test_sokrates_prd"
rm -r $TEMP_DIR
mkdir -p $TEMP_DIR

cd $TEMP_DIR
uv venv
source .venv/bin/activate
# install
uv pip install sokrates

# test cli tool
uv run sokrates list-models
uv run sokrates chat
```
