# Contributing

Thanks for helping improve MPP tooling.

## Development

```bash
cd conformance
make install
make test
make flow
```

Prerequisites are listed in [conformance/README.md](./conformance/README.md#prerequisites).

## Pull Requests

- Keep changes focused and follow existing patterns.
- Add or update conformance vectors for protocol behavior changes.
- Run `cd conformance && make all` before opening a PR.
- Do not commit secrets, credentials, local paths, or generated build artifacts.

## Test Vectors

Vectors in `conformance/vectors/` are the source of truth. When adding a vector:

1. Add the scenario to the relevant JSON file.
2. Run the affected adapter tests.
3. Run the full vector suite before submitting.
