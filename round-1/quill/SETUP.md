# Setup

This pack ships no tests, on purpose. Read the specification in `README.md`,
form a hypothesis about where the implementation deviates, and write your own
tests to confirm it before you change anything. The same service exists in
Python, C++, and Java; pick one. No external dependencies, services, API keys,
or network.

## Python 3.9+

Write test files named `test_*.py` in `python/` (a `conftest.py` is already there
so your imports resolve), then:

```bash
cd python && pytest -q
```

## C++ (g++ with -std=c++17)

The implementation is header-only. Write your own `test.cpp` that includes the
header, then:

```bash
cd cpp && g++ -std=c++17 test.cpp -o test && ./test
```

## Java (JDK 11+)

Write your own `Check.java` with a `main` that exercises the classes, then:

```bash
cd java && javac *.java && java Check
```
