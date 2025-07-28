## Changelog

**Week 2025-07-28**
- implements the task queuing system , bumps to the next version
- remove obsolete context llm usage docs
- adds execute-tasks feature, small fixes and improvements, docs improvements, bumps version to 0.3.0
- improve readme, add changelog update
- rename lib to : sokrates
- updates pyproject.toml
- bump to new version, refactor idea generator to use random category picks via python

**Week 2025-07-14**
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