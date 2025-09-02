import pytest

from sokrates.coding.analyze_repository_workflow import AnalyzeRepositoryWorkflow

@pytest.fixture
def workflow():
    return AnalyzeRepositoryWorkflow(api_endpoint=pytest.TESTING_ENDPOINT, api_key='not-required')

@pytest.fixture
def file_paths():
    return [
        '/my/source/README.md',
        '/my/source/bla/test.txt',
        '/my/source/blu/guide.md',
        '/my/source/docs/MY_SUPER_README_FILE.md',
        '/my/source/docs/tutorial.md',
        '/my/source/docs/code/feature.md',
    ]


class TestAnalyzeRepositoryWorkflow:
    def test_filter_readme_filepaths(self, workflow, file_paths):
        paths = workflow._filter_readme_filepaths(file_paths)
        assert len(paths) == 2
        assert '/my/source/README.md' in paths
        assert '/my/source/docs/MY_SUPER_README_FILE.md' in paths

    def test_filter_non_readme_markdown_file_paths(self, workflow, file_paths):
        paths = workflow._filter_non_readme_markdown_file_paths(file_paths)
        assert len(paths) == 3
        assert '/my/source/blu/guide.md' in paths
        assert '/my/source/docs/tutorial.md' in paths
        assert '/my/source/docs/code/feature.md' in paths