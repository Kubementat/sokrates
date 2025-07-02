**Implement a Python script that compares large language models based on benchmarking results stored in JSON files. The script should take a comma-separated list of file paths as input (via the `--result-files` command-line argument), read and parse these JSON files, extract specific performance and resource usage metrics for each model, and generate a comparative Markdown table.**

### Requirements:
1. The script must accept `--result-files` as a command-line argument containing comma-separated file paths.
2. Each JSON file contains benchmarking results for one or more models in a predefined structure (example provided below).
3. The script must extract the following metrics for each model:
- `avg_tokens_per_second`
- `avg_response_time_seconds`
- `total_completion_tokens`
- `prompts_tested`
- `avg_cpu_percent`
- `max_memory_used_gb`

4. The output should be a Markdown table comparing these metrics across all models from all input files.

### Example JSON Structure:
```json
{
"comparison_metadata": {
"timestamp": "2025-06-22T00:18:59.455267",
"total_models_tested": 2,
"benchmark_version": "1.0",
"temperature": 0.15
},
"model_comparisons": [
{
"model_name": "unsloth-phi-4",
"performance_metrics": {
"avg_tokens_per_second": 22.015008324270102,
"avg_response_time_seconds": 36.63447098731994,
"total_completion_tokens": 3675,
"prompts_tested": 5,
"relative_performance_percent": 100.0
},
"resource_usage": {
"avg_cpu_percent": 12.467914438502685,
"max_memory_used_gb": 19.942977905273438,
"avg_gpu_utilization_percent": null,
"max_gpu_memory_used_gb": null
},
...
}
],
...
}
```

### Expected Output Format (Markdown table example):
```markdown
| Model Name         | Avg Tokens/s | Avg Response Time (s) | Total Completion Tokens | Prompts Tested | Avg CPU (%) | Max Memory Used (GB) |
|-------------------|--------------|----------------------|------------------------|----------------|-------------|----------------------|
| unsloth-phi-4     | 22.015       | 36.634               | 3675                   | 5             | 12.468      | 19.943              |
| microsoft/phi-4   | 19.926       | 39.209               | 3629                   | 5             | 10.582      | 20.949              |
```

### Edge Cases and Error Handling:
1. If a file cannot be read (e.g., file not found), log an error and continue with the next file.
2. If a JSON field is missing or malformed, handle it gracefully (e.g., log a warning and skip that entry or use a default value).
3. If duplicate model names are found across files, ensure they are treated as the same model (average or sum metrics if necessary).
4. Handle cases where numeric values might be strings in the JSON (e.g., `"avg_tokens_per_second": "22.015"`).

### Logging and Console Output:
- Use colored console output for better readability (e.g., green for successes, red for errors).
- Log the following events:
- Start of script execution.
- Start and end of file processing (with filename).
- Any warnings or errors encountered during file reading or parsing.
- Completion of table generation and output.

### Recommended Libraries:
- Use `argparse` for command-line argument parsing.
- Use the built-in `json` module to parse JSON files.
- For generating Markdown tables, you can either construct the table manually with strings or use a library like `tabulate` for more complex cases.
- For colored console output, consider using `colorama`.

### Example Command to Run the Script:
```bash
python compare_models.py --result-files results1.json,results2.json
```

### Example Output Logs:
```
[INFO] Starting script execution...
[INFO] Processing file: results1.json
[WARNING] Missing field 'max_memory_used_gb' in model 'unsloth-phi-4'. Using default value: 0.0
[ERROR] Could not read file results3.json: No such file or directory
[INFO] Processing file: results2.json
[INFO] Generating Markdown table...
[SUCCESS] Comparison table generated successfully at: comparison_table.md