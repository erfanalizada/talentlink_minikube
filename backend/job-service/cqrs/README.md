# CQRS Implementation for Job Service

## Overview

This directory contains the CQRS (Command Query Responsibility Segregation) implementation for the job-service. CQRS separates read operations (queries) from write operations (commands), providing better scalability and maintainability.

## Why CQRS?

### Job Listings Use Case
- **Writes**: Employers creating/editing/deleting jobs - requires validation and business rules
- **Reads**: "Show me 20 jobs with filters" - requires fast, optimized queries
- These operations have very different performance needs and can be scaled independently

### Applications Use Case
- **Writes**: Employees applying to jobs, employers updating application status
- **Reads**: Employers viewing applicants, employees viewing their applications
- Read-heavy operations can be optimized separately from write operations

## Structure

```
cqrs/
├── commands/           # Write operations (state changes)
│   ├── job_commands.py
│   └── application_commands.py
├── queries/            # Read operations (no state changes)
│   ├── job_queries.py
│   └── application_queries.py
└── handlers/           # Execute commands and queries
    ├── command_handlers.py
    └── query_handlers.py
```

## Commands (Write Operations)

Commands represent intentions to change state. They contain all necessary data for the operation.

### Job Commands
- **CreateJobCommand**: Create a new job posting
- **UpdateJobCommand**: Update an existing job
- **DeleteJobCommand**: Delete a job

### Application Commands
- **ApplyToJobCommand**: Submit a job application
- **UpdateApplicationStatusCommand**: Update application status (accept/reject)

### Usage Example
```python
from cqrs.commands import CreateJobCommand
from cqrs.handlers import JobCommandHandler

# Create command with data
command = CreateJobCommand(
    employer_id="emp123",
    title="Senior Developer",
    description="We are hiring...",
    salary=80000,
    skills=["Python", "Flask"]
)

# Execute command via handler
handler = JobCommandHandler(service)
job = handler.handle_create_job(command)
```

## Queries (Read Operations)

Queries represent requests for data without modifying state. They are optimized for read performance.

### Job Queries
- **GetAllJobsQuery**: Fetch all job postings
- **GetJobByIdQuery**: Fetch a specific job
- **GetJobsByEmployerQuery**: Fetch jobs by employer
- **GetAllJobsWithApplicationStatusQuery**: Fetch jobs with application status for an employee

### Application Queries
- **GetApplicationsByJobQuery**: Fetch applications for a job (employer view)
- **GetApplicationsByEmployeeQuery**: Fetch applications by employee

### Usage Example
```python
from cqrs.queries import GetAllJobsQuery
from cqrs.handlers import JobQueryHandler

# Create query
query = GetAllJobsQuery()

# Execute query via handler
handler = JobQueryHandler(service)
jobs = handler.handle_get_all_jobs(query)
```

## Handlers

Handlers execute commands and queries using the existing service layer. This keeps the business logic centralized while providing a clean CQRS interface.

- **JobCommandHandler**: Executes job-related commands
- **ApplicationCommandHandler**: Executes application-related commands
- **JobQueryHandler**: Executes job-related queries
- **ApplicationQueryHandler**: Executes application-related queries

## Benefits

1. **Clear Separation**: Write and read operations are clearly separated
2. **Scalability**: Queries can be optimized independently (e.g., add read replicas, caching, ElasticSearch)
3. **Maintainability**: Easy to understand what each operation does
4. **Performance**: Can optimize read and write paths separately
5. **Testing**: Commands and queries can be tested independently

## Future Enhancements

As your application grows, you can:

1. **Add a separate read database**: Use ElasticSearch for fast job searches
2. **Implement caching**: Cache frequently accessed queries
3. **Add event sourcing**: Store events for audit trails
4. **Scale reads independently**: Add read replicas for query operations
5. **Optimize query models**: Create denormalized views for complex queries

## Integration with Routes

The routes layer has been updated to use CQRS handlers. Each endpoint now clearly indicates whether it's a COMMAND or QUERY operation:

```python
@jobs_bp.route("/api/jobs", methods=["POST"])
def create_job():
    """Create a new job posting (Employer only) - COMMAND."""
    command = CreateJobCommand(...)
    command_handler, _, db = get_job_handlers()
    job = command_handler.handle_create_job(command)
    return jsonify(job.to_dict()), 201

@jobs_bp.route("/api/jobs", methods=["GET"])
def get_all_jobs():
    """Get all job postings (Public) - QUERY."""
    query = GetAllJobsQuery()
    _, query_handler, db = get_job_handlers()
    jobs = query_handler.handle_get_all_jobs(query)
    return jsonify([job.to_dict() for job in jobs]), 200
```

## Notes

- The existing service layer and repositories remain unchanged
- CQRS is a pattern, not a framework - it's implemented simply and pragmatically
- Commands and queries use dataclasses for clear, type-safe contracts
- No over-engineering - only what's needed for the current use cases
