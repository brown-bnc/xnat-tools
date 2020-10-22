## Using Docker

```
docker pull docker pull brownbnc/xnat_tools:<version>
```

_Version:_

- `latest`: Is the build of master
- `vX.X.X`: Latest tagged stable release

You can confirm the tags [here](https://hub.docker.com/repository/docker/brownbnc/xnat_tools/tags?page=1)

## Using Python

### Prerequisites:

We first need to install the dcm2niix . This is a dependency of Heudiconv, that doesn't get installed by Heudiconv itself

```
brew install dcm2niix
```

### Poetry

This package is developed using [Poetry](https://python-poetry.org). If you are familiar with Poetry, you can add it to your project via

```
poetry add git+https://github.com/brown-bnc/xnat-tools.git
```

or for a tagged release

```
poetry add git+https://github.com/brown-bnc/xnat-tools.git@v0.1.0
```

You can also install xnat_tools using the python package manager of your choice, such as PIPX and PIP

### PIPX

If you are using this package in a stand-alone fashion, and you don't want to use Docker, we recommend using pipx. Please check their [installation instructions](https://github.com/pipxproject/pipx).

Once pipx is installed you install as follows:

A Tagged Release

```
pipx install git+https://github.com/brown-bnc/xnat-tools.git@v0.1.0
```

Development (Master branch)

```
pipx install git+https://github.com/brown-bnc/xnat-tools.git
```

### PIP

- A Tagged Release

```
pip install git+https://github.com/brown-bnc/xnat-tools.git@v0.1.0
```

- Development (Master branch)

```
pip install git+https://github.com/brown-bnc/xnat-tools.git
```

