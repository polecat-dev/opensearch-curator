# Contributing to Curator

All contributions are welcome: ideas, patches, documentation, bug reports,
complaints, etc!

Programming is not a required skill, and there are many ways to help out!
It is more important to us that you are able to contribute.

That said, some basic guidelines, which you are free to ignore :)

## Want to learn?

Want to write your own code to do something Curator doesn't do out of the box?

* [Curator API Documentation](https://github.com/polecat-dev/opensearch-curator/tree/main/docs) Since version 2.0,
Curator ships with both an API and wrapper scripts (which are actually defined
as entry points).  This allows you to write your own scripts to accomplish
similar goals, or even new and different things with the
[Curator API](https://github.com/polecat-dev/opensearch-curator/tree/main/docs), [opensearch_client](https://github.com/polecat-dev/opensearch-curator/tree/main/opensearch_client), and the
[OpenSearch Python Client Library](https://opensearch.org/docs/latest/clients/python/).

Want to know how to use the command-line interface (CLI)?

* [Curator CLI Documentation](https://github.com/polecat-dev/opensearch-curator/tree/main/docs/reference)
  The CLI documentation is part of this repository and can be built locally with `sphinx-build -b html docs docs/_build/html`.


## Have a Question? Or an Idea or Feature Request?

* File a ticket on [GitHub](https://github.com/polecat-dev/opensearch-curator/issues)

## Something Not Working? Found a Bug?

If you think you found a bug, it probably is a bug.

* File it on [GitHub](https://github.com/polecat-dev/opensearch-curator/issues)

# Contributing Documentation and Code Changes

If you have a bugfix or new feature that you would like to contribute to
Curator, and you think it will take more than a few minutes to produce the fix
(ie; write code), it is worth discussing the change with the Curator users and
developers first! You can reach us via
[GitHub](https://github.com/polecat-dev/opensearch-curator/issues).

Documentation is in two parts: API and CLI documentation.

API documentation is generated from comments inside the classes and methods
within the code.  This documentation is rendered and hosted at
http://github.com/opensearch-project/opensearch-curator/tree/main/docs

CLI documentation lives under `docs/reference/` (Markdown and reStructuredText) in this repository.
You can update it with a standard pull request, and the HTML output can be verified locally using `sphinx-build`.

## Contribution Steps

1. Test your changes! Run the test suite (`python -m pytest --cov=curator`). This
   requires an OpenSearch instance. The tests connect to `TEST_ES_SERVER`
   (defaults to `https://localhost:19200`) and run integration tests against it.
   **This will delete all data on that cluster.** Point the env var at a disposable
   instance if you cannot run locally.
2. Ensure new files retain the Apache 2.0 license header where applicable and that
   dependencies remain compatible with Python 3.8+.
3. Send a pull request! Push your changes to your fork of the repository and
   [submit a pull
   request](https://help.github.com/articles/using-pull-requests). In the pull
   request, describe what your changes do and mention any bugs/issues related
   to the pull request.
