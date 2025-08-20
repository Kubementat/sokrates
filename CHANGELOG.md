## Changelog

**Week 2025-15-10**
- version 0.9.0
  - rename `sokrates-python-summarize` -> `sokrates-code-summarize`
  - introduce `sokrates-code-generate-tests`

**Week 2025-08-10**
- version 0.8.2 - introduce coding tools v1
  - features: 
    - sokrates-code-review
    - sokrates-python-summarize
- a lot of refactorings around configuration
- update readme and changelog
- simplify MANIFEST.in
- refine readme
- improve testsuite, 
- set qwen3-4b-instruct-2507-mlx as default model
- add temperature range check in configuration
- fix bug in parsing api_key
- adds kilocode rules for usage of the uv command instead of direct execution
- fix config singleton, refactor cli argument parsing
- remove cline project specific workflows

**Week 2025-08-03**
- fix testsuite imports, add conftest.py, remove click from dependencies and use argparse consistently for all cli commands, adjust readme
- bump to new version 0.6.2
- adds missing docstrings, refines test all commands to output failed commands at the end of the execution
- adds option to disable refinement for sequential task executor executions, adds the --no-refinement option for sokrates-execute-tasks, adds test tasks for llm testing in tests/tasks

**Week 2025-07-27**
- adds idea merging tools, bumps to the next version
- allow installing basic or voice version (pip install sokrates[voice]) , bump to 0.5.0
- bump to 0.4.2 - usage of default values from .env file if present + improvement of sequential task processing
- implements the task queuing system , bumps to the next version
- fix manifest inclusion for packaging, bump to 0.4.1
- changelog update

**Week 2025-07-20**
- remove obsolete context llm usage docs
- adds execute-tasks feature, small fixes and improvements, docs improvements, bumps version to 0.3.0
- updates pyproject.toml
- rename lib to : sokrates
- improve readme, add changelog update
- bump to new version, refactor idea generator to use random category picks via python

**Week 2025-07-13**
- remove unnecessary file
- refine changelog and readme
- fix test all commands smoke tests
- fix directory naming bug in idea generation workflow
- update changelog
- refactoring: - rename meta prompt generator -> idea_generator - refine idea generator - add better documentation
- remove obsolete kilocode files
- only load audio libraries when needed
- bump version, also remove <answer> tags when refining
- bump version, improve voice chat
- adds more documentation to the code, updates llm chat, adds a context document in docs/ for loading information about the library to a context

**Week 2025-07-06**
- version bump
- improvements + addition of llmchat functionality for chatting on the terminal
- bump up version , add DEFAULT_PROMPTS_DIRECTORY to Config
- add context parameters to all cli scripts and to the llmapi send
- adds mantra generator - refactors console output formatting into output_printer.py
- refactor meta prompt generation -> MetaPromptWorkflow, move prompts directory to library main path

**Week 2025-06-29**
- refactorings and fixes, bump version
- major improvements and refinements, bugfixes, now this becomes nice to use :D
- api_token -> api_key ; improvements; adds refinement_workflow
- initial commit
