# VVPay Project Instructions

## Project Structure Overview

### 1. App Layer (`app/`)
The presentation layer containing Streamlit UI components.

```
app/
├── components/         # UI Components
│   ├── upload.py      # File upload handling
│   ├── status.py      # Status display
│   └── validation.py  # Validation interface
├── utils/             # UI-specific utilities
│   └── formatters.py  # Display formatting
└── main.py           # Main Streamlit application
```

**Working with UI Components:**
- Each component should be self-contained
- Use formatters for consistent display
- Handle errors with proper user feedback
- Follow Streamlit best practices

### 2. Core Layer (`core/`)
Foundation of the application containing essential configurations and interfaces.

```
core/
├── config.py         # Application settings
├── exceptions.py     # Custom exceptions
├── interfaces/       # Abstract base classes
│   ├── base.py      # Base interfaces
│   ├── repository.py # Repository interfaces
│   └── service.py   # Service interfaces
└── logging.py       # Logging configuration
```

**Working with Core:**
- Add new settings to `config.py`
- Define new exceptions in `exceptions.py`
- Create interfaces before implementations
- Follow error handling patterns

### 3. Models Layer (`models/`)
Data models and schema definitions.

```
models/
├── db/              # Database models
│   ├── base.py     # Base model class
│   ├── extraction.py
│   ├── validation.py
│   └── meta.py
├── processing/      # Processing models
│   ├── states.py   # State definitions
│   └── llm.py      # LLM models
└── service/        # Service models
    └── enums.py    # Enumerations
```

**Working with Models:**
- Inherit from `DBModelBase` for database models
- Use Pydantic for validation
- Keep models focused and single-purpose
- Add proper field descriptions

### 4. Repositories Layer (`repositories/`)
Data access layer implementing repository pattern.

```
repositories/
├── base.py          # Base repository
├── extraction.py    # PDF extraction repo
├── validation.py    # Validation repo
├── meta.py         # Meta table repo
└── mixins.py       # Shared functionality
```

**Working with Repositories:**
- Inherit from `BaseRepository`
- Use `TransactionMixin` for transactions
- Implement CRUD operations
- Handle database errors properly

### 5. Services Layer (`services/`)
Business logic implementation.

```
services/
├── document_processor.py  # PDF processing
└── validation_service.py  # Validation logic
```

**Working with Services:**
- Implement service interfaces
- Use repositories for data access
- Handle business logic
- Proper error propagation

### 6. Utils Layer (`utils/`)
Shared utilities and helpers.

```
utils/
├── db_utils.py     # Database utilities
└── helpers.py      # General helpers
```

**Working with Utils:**
- Keep functions focused
- Add proper error handling
- Document usage examples
- Add type hints

## Development Workflows

### Adding a New Feature

1. **Plan the Changes**:
   - Identify affected components
   - Review existing interfaces
   - Plan data model changes

2. **Update Models**:
   ```python
   # 1. Add model in models/db/
   class NewModel(DBModelBase):
       field: str = Field(...)
   
   # 2. Update enums if needed
   class NewEnum(str, Enum):
       VALUE = "value"
   ```

3. **Create Repository**:
   ```python
   # repositories/new_repo.py
   class NewRepository(BaseRepository[NewModel]):
       def __init__(self):
           super().__init__("table_name", NewModel)
   ```

4. **Implement Service**:
   ```python
   # services/new_service.py
   class NewService(ServiceInterface):
       def process(self):
           # Implementation
   ```

5. **Add UI Component**:
   ```python
   # app/components/new_component.py
   def new_section():
       st.header("New Feature")
       # Implementation
   ```

### Modifying Existing Features

1. **Check Dependencies**:
   - Review service usage
   - Check repository calls
   - Verify UI components

2. **Update in Order**:
   ```
   Models → Repositories → Services → UI
   ```

3. **Test Changes**:
   - Unit tests
   - Integration tests
   - UI testing

### Error Handling

1. **Database Errors**:
   ```python
   try:
       result = repository.create(model)
   except DatabaseError as e:
       logger.error("Database operation failed", exc_info=e)
       raise
   ```

2. **Service Errors**:
   ```python
   try:
       result = service.process()
   except ValidationError as e:
       logger.error("Validation failed", exc_info=e)
       raise
   ```

3. **UI Error Display**:
   ```python
   try:
       result = service.process()
       st.success("Success!")
   except Exception as e:
       st.error(f"Error: {str(e)}")
   ```

### Best Practices

1. **Code Organization**:
   - One class per file
   - Clear file naming
   - Proper imports
   - Type hints

2. **Error Handling**:
   - Use custom exceptions
   - Proper error messages
   - Consistent patterns
   - Log errors

3. **Documentation**:
   - Docstrings
   - Type hints
   - Comments
   - Examples

4. **Testing**:
   - Unit tests
   - Integration tests
   - Mock external services
   - Test edge cases

## Common Tasks

### Adding a New Model
1. Create model in `models/db/`
2. Add repository in `repositories/`
3. Update service layer
4. Add UI component

### Modifying Database Operations
1. Check `db_utils.py`
2. Update repository methods
3. Test transactions
4. Update error handling

### Adding UI Features
1. Create component in `app/components/`
2. Update main.py
3. Add formatters if needed
4. Test user flow

### Implementing Validation
1. Update validation models
2. Modify validation service
3. Add UI feedback
4. Test validation flow

## Troubleshooting

### Common Issues
1. Database Connections
2. Transaction Rollbacks
3. UI State Management
4. Error Propagation

### Debug Tools
1. Logging
2. Streamlit Debug
3. Database Queries
4. Error Tracking

## Deployment

### Environment Setup
1. Configure `.env`
2. Set up database
3. Configure services
4. Test deployment

### Monitoring
1. Check logs
2. Monitor errors
3. Track performance
4. User feedback

---

This guide provides a comprehensive overview of the VVPay project structure and development workflows. For specific questions or issues, consult the team or review the codebase.