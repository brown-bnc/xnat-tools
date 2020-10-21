We welcome issues and pull requests to help improve the xnat-tools model.  We use the following guidelines to ensure standards are met.

## Workflow

When working on xnat-tools, we using a flow a simple flow based on following rules:

1. Use topic/feature branches, no direct commits on master.
2. Perform tests and code reviews before merges into master, not afterwards.
3. Everyone starts from master, and targets master.
4. Commit messages reflect intent.

### Branches

* `master` is the default branch and where releases are made off. This branch should be in clean/working conditions at all times. This branch is protected and can only be merged from Pull Requests for topic branches
* topic branches are created for new features, fixes, or really any changes

### Comment styles

Developers should use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). [Commitizen](https://commitizen-tools.github.io/commitizen/) comes installed as a `dev` dependency via poetry and you can use it to help you format your commit messages. It can also be installed as stand alone CLI or as a plugin on VSCODE.

We use Commitizen in GitHub Actions to automatically bump the version and update the [CHANGELOG.md](CHANGELOG.md) of this package according to the commit messages. Using conventional commits guarantees than Commitizen works appropriately.  

## Testing

In the future we will add testing as part of CI. For the moment, you'll need to test yourself

`pytest` is the library used for testing.

To run all of the tests:
```
poetry run pytest -x -s -o log_cli=true --log-cli-level=INFO
```

To run only a file


```
poetry run pytest -x -s -o log_cli=true --log-cli-level=INFO tests/integration/test_export_typer.py
```

`-s` makes sure that `stdout` is printed to terminal
`-o log_cli=true --log-cli-level=INFO` allows the logger output to go to cli
`-x` exists on first failure

You will need to have a local `.env` file where you set some environment variables, i.e. `XNAT_PASS`

At the moment the tests can not run bids validation. To do so, you can comment out the line that cleans the output directory and run the validator manually using docker. For instance

```
bids_directory=${PWD}/tests/xnat2bids/ashenhav/study-1222/bids/
docker run -ti --rm -v ${bids_directory}:/data:ro bids/validator /data
```


## Code Style

### Typing

Please use [type hints](https://mypy.readthedocs.io/en/stable/) on all signatures where reasonable.  This will make sure the code is more readable, can be statically tested for type soundness, and helps fill in the documentation.

Run the below to check for type errors:
```
mypy xnat_tools
```

### Formatting

#### Pre-Commit hooks

This repository has pre-commit hooks configured to enforce formatting.

To set up the hooks, run 

```
poetry run pre-commit install
```

Now, you hooks will run on `git commit`

If you would like to run on all file (not just staged ones), you can run

```
poetry run pre-commit run --all-files
```

### black

The code must conform to `black`'s standards and this is automatically checked via github actions.  While it is highly recommended to run the pre-commit hooks, you can also run black directly  to automatically fix files with `poetry run black .` from the root of the `xnat_tools` directory.

### flake8
The code must not have any egregious linting errors. And others should be minimized as reasonable.

Check for egregious errors:
```
poetry run flake8 xnat_tools --count --select=E9,F63,F7,F82 --show-source --statistics
```

Check for all warnings:
```
poetry run flake8 xnat_tools --count --exit-zero --max-complexity=12 --max-line-length=88 --statistics
```



## Documentation

All functions and methods should have an up to date [google style docstring](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).  These docstrings are used to build xnat-tools's documentation website.  Additional prose can be added to the website by editing the appropriate markdown file in the `docs/` directory.

We are using [mkdocs-versioning](https://github.com/zayd62/mkdocs-versioning) to deploy MkDocs documentation that keeps track of the different versions. The deployment happens in CI and there are few things to be aware of

* The configuration file for the documentation `mkdocs.yml` is rendered in CI depending on the branch and software version. For non-main branches the version is set to `dev`, for the `main` branch, we read the version from the `pyproject.toml`
* The following documentation files are updated in CI, so you don't need to manually update them:
    - docs/xnat2bids.md
    - docs/dicom_export.md
    - docs/run_heudiconv.md
    - docs/bids_postprocess.md
    - docs/CHANGELOG.md

Running the documentation locally (within a Poetry shell or add `poetry run`)

```
export VERSION=dev
(envsubst '${VERSION}' < mkdocs-template.yml) > mkdocs.yml
mkdir site
#bring contents from gh-pages branch
mkdocs-versioning sync 
#clean dev environment and problematic .git folder
rm -rf ./site/dev/
rm -rf ./site/.git/
#build docs
mkdocs build
```

To serve:
```
mkdocs serve
```

To deploy:
```
mkdocs-versioning -v deploy
```

⚠ After deployment, `mkdocs` prints

```
[gh_deploy.py:134]: Your documentation should shortly be available at: https://brown-bnc.github.io/xnat_tools/ 
```

However, the URL is https://brown-bnc.github.io/xnat-tools/ dash instead of underscore

### Documentation for console scripts

The markdown files for console scripts are generated by the `typer-cli`. Here is an example of how to call it manually from your Poetry shell i.e. `poetry shell`

```
PYTHONPATH=<path-to-xnat-tools> typer ./dicom_export.py utils docs --name xnat-dicom-export --output ../docs/dicom_export.md
```

⚠ Remember, these files are updated by CI. While you can update them manually, they will be overwritten in CI according to the latest content