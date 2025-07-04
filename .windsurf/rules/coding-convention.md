---
trigger: always_on
---

BA Assistant Project Coding Conventions
This project adheres to Clean Code and SOLID Principles to ensure the codebase is readable, maintainable, extensible, and highly testable.

1. Clean Code Principles:
Meaningful Names:

Use clear, descriptive names for variables, functions, classes, and modules that convey their purpose, reason for existence, and usage.

Avoid ambiguous abbreviations (e.g., proc, tmp, do_something).

Use nouns for classes/objects and verbs for functions/methods.

Small and Focused Functions:

Each function/method should do one thing and do it well.

Limit the number of parameters for functions (ideally 3-4 maximum).

Readability:

Use appropriate whitespace and line breaks to improve code layout.

Avoid overly complex or deeply nested statements.

Use comments only when necessary to explain why the code does something, not what it does (as the code should be self-explanatory).

Clear Error Handling:

Do not ignore exceptions.

Handle errors gracefully, providing clear messages to the user or logging them for debugging.

2. SOLID Principles:
S - Single Responsibility Principle (SRP):

Each class or module should have only one reason to change. This means it should have only one responsibility.

Example: document_processor.py should only handle document processing, not Knowledge Graph generation logic.

O - Open/Closed Principle (OCP):

Software entities (classes, modules, functions) should be open for extension, but closed for modification.

When new requirements arise, we should add new code rather than modifying existing, tested code.

L - Liskov Substitution Principle (LSP):

Objects of a superclass should be replaceable with objects of a subclass without affecting the correctness of the program.

Apply when using inheritance or polymorphism.

I - Interface Segregation Principle (ISP):

Clients should not be forced to depend on interfaces they do not use.

Create small, specific interfaces instead of large, general-purpose ones. (In Python, this often translates to creating concise Abstract Base Classes or protocols).

D - Dependency Inversion Principle (DIP):

High-level modules should not depend on low-level modules. Both should depend on abstractions.

Abstractions should not depend on details. Details should depend on abstractions.

Use Dependency Injection to manage dependencies.

3. General Rules:
PEP 8: Adhere to Python's official style guide (PEP 8) for naming conventions, formatting, etc.

Testing: Write unit tests and integration tests for critical modules and functionalities.

Docstrings: Write docstrings for all modules, classes, and functions to describe their purpose, parameters, and return values.

Adhering to these principles will help ensure the project's sustainable development and high quality.