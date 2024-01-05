# mySidewalk Fullstack Engineer Interview

## Running this Project

Make sure you have the latest version of docker installed.

Run ```docker-compose up``` at the root of the project.

## Configuration

```configuration.yml``` - here you can set the input and output file paths as well as the batch size and database path.

## Problem

See prompt.md

## Solution

This script reads the input of a file in batches set within config.yml. It then inserts those lines into a SQLite database. Once all the lines have been added, it queries the database using a custom order by clause and paging with the page size set to the configured batch size. Those queried results are written to the output file.

## Testing

```python3 -m unittest test/test_main.py```

## Considerations

1. How big of a file are we expecting to read? 1MB? 1GB? 1TB? 1PB??? I'll need to create a solution that doesn't load the entire file into memory.
2. Should we clean the data before we sort it? Based on the given example-list.txt, I'll assume in this case it's a light cleaning task.
3. Is it more important to create a simple, fast solution or one that is fast and allows for long-term storage and queries in the future? I'll assume the latter.

## Disclosure

To reflect current real-world conditions, GitHub Copilot was utilized for assistance in developing this project. However, its usage was limited. I refrained from using it to solve the problem entirely. It served as a reference for Python conventions, syntax, troubleshooting, and test generation.
