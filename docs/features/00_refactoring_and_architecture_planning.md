# Logging
WHEN USING THE LIBRARY IT SHOULD NEVER PRINT TO THE CONSOLE.
WHEN USING THE COMMANDS IT SHOULD USE THE ACCORDING CONSOLE OUTPUT SYSTEM.
## Logfile
- use logging standard library -> log to log files
- TODO: think about splitting up into multiple loggers

## Console Output
- use a consistent console output
  - colored (only if active (default))

# Task queue and task management
- First step: 
  - refactor to use a ORM wrapper instead of the direct SQL approach in `src/sokrates/task_queue/database.py`
  - add orm: [alchemy](https://docs.peewee-orm.com/en/latest/peewee/quickstart.html#quickstart)
  - add models:
    - api
    - task
    - task_history
- Exception handling
  - handle execution error state setting after retries

# Database architecture

## Api
- id [int] - database id
- provider [str] - the provider name (e.g. lm-studio, openai, openrouter, ...)
- api_type [str] - openai, grok, .... (changes request behavior for calling APIs according to the used standard (later, later))
- api_endpoint [str] - the endpoint, e.g. 
- api_key [str] - should be read via env variable


## Model
- id [int] - database id
- model_identifier [str] - the model name for using the API
- api_id [int] - foreign id linking to Api - the id of the api that the model belongs to
- alias [str] - a short identifier that can be used for switching between models and in task descriptions, ....

## Task
- architecture - use a composite pattern for the task json documents
  - it should also be possible to link further task jsons within sub-tasks in a json task document

- id [int] - database id
- priority [int] - priority from 1 (low) to 10 (high) - Default: 1
- status [str or int???] - Enum TaskStatus - Default: 'created'
- planned_for [timestamp] - when should this run? - Default: None
- execution_model_id [int] - required - foreign id linking to Model - the id of the model to use for executing the task
- parent_task - [int] - foreign key to Task table - reference to a parent task, so tasks can be connected in a tree - Default: None

- a root parent task without any sub-tasks is considered done, when all of it's sub-tasks are executed successfully
- when a task does not have parent tasks and does not have sub-tasks it is considered done once it was executed successfully
- TODO: add support for assigning other required prerequisite tasks via their database id
- TODO: allow specifying sokrates workflows to execute with according input parameters instead of prompt-text

## TaskResult

- id [int] - database id
- executed_at [timestamp] - when was this task executed?
- error_log [string] - a log string with the error description - Default: None
- succesful [boolean] - was the task executed successfully - Default: False
  - TODO: rethink this

## ResultDocument
- id [int] - database id
- created_at [timestamp]
- task_result_id - foreign key to TaskResult table
- location [str]
  - this can be file://, or https:// based locations (initially we will use file://)

- TODO: later - add possibility to reference other resultdocuments and tasks via a join table
  - this could help in making the documents more interconnected and reusable for further tasks


# Extended LM Studio support
  - model execution control (via lm stutdio api (like the lms command does))
    - this will help coordinating the task executions
    - listing loaded models
    - load model
    - unload model
    - list RAM, VRAM and CPU loads


# Unsorted TODOs
- feature - generate CHANGELOG from git history and README.md (see analyze-git-history.md workflow in kilocode)