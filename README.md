# XNAT Tools

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/brown-bnc/xnat-tools)](https://github.com/brown-bnc/xnat-tools/releases/latest/)
[![Stable](https://img.shields.io/badge/docs-stable-blue.svg)](https://brown-bnc.github.io/xnat-tools/)
![tests](https://github.com/brown-bnc/xnat-tools/workflows/tests/badge.svg)

XNAT tools is a Python package developed and maintained by members of the [Behavior and NeuroData Core](https://brown-bnc.github.io) at Brown University. This package facilitates the export and conversion of data stored in Brown's XNAT platform to the [Brain Imaging Data Structure (BIDS)](https://bids.neuroimaging.io). To learn about installation, usage, and deployment please visit our [documentation](https://brown-bnc.github.io/xnat-tools/).

<!-- TODO #178: The development documentation is found here: https://brown-bnc.github.io/xnat-tools/dev/ -->
<!-- TODO #178: We should probably move some of the basic getting started documentation into this README? -->
<!-- TODO #178: We need to better split the documentation for "users" and "developers" -->

## Local Development

### Set up Your environment

```bash
uv venv
source .venv/bin/activate
uv sync --all-extras
```

### Environment Variables

To run integration tests, you'll need to provide authentication credentials for XNAT using environment variables. These should be defined in a local `.env` file at the root of the repository.

1. Copy the [.env.example](.env.example) file and rename it `.env`

   ```shell
   cp .env.example .env
   ```

2. Add your credentials

   ```shell
   XNAT_USER=your_xnat_username
   XNAT_PASS=your_xnat_password
   ```
