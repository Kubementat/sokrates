# How to publish

```
PYPI_API_TOKEN="REPLACEME"

# publish to pypi test instance
uv publish --index testpypi --token "$PYPI_API_TOKEN"

# Test the test package
TEMP_DIR="~/tmp/test_sokrates"
mkdir -p $TEMP_DIR

cd $TEMP_DIR
uv venv
source .venv/bin/activate
pip install --index-url https://test.pypi.org/simple/ sokrates


# publish to prod instance
PYPI_API_TOKEN="REPLACEME"
uv publish --token "$PYPI_API_TOKEN"

# Test the published package
TEMP_DIR="~/tmp/test_sokrates_prd"
mkdir -p $TEMP_DIR

cd $TEMP_DIR
uv venv
source .venv/bin/activate
pip install sokrates

```