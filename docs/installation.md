## Using Docker

```
docker pull docker pull brownbnc/xnat_tools:<version>
```

_Version:_

- `latest`: Is the build of main
- `vX.X.X`: Latest tagged stable release

You can confirm the tags [here](https://hub.docker.com/repository/docker/brownbnc/xnat_tools/tags?page=1)

## Using Python

### Prerequisites:

We first need to install the dcm2niix . This is a dependency of Heudiconv that doesn't get installed by Heudiconv itself

```
brew install dcm2niix
```

### PIPX

Most users only need to interact with the command-line utilities provided by `xnat-tools`. In this case, we recommend using `pipx`. Please check their [installation instructions](https://github.com/pipxproject/pipx).

Once `pipx` is installed you will need to install Heudiconv and xnat-tools as stand-alone applications as follows:

```
pipx install heudiconv
pipx install git+https://github.com/brown-bnc/xnat-tools.git@v{{ mdvars.version }}
```

The command above installs the latest tagged release of `xnat-tools`. If you want to install the development version (main branch) you can run:

```
pipx install git+https://github.com/brown-bnc/xnat-tools.git
```

### PIP

- A Tagged Release

```
pip install git+https://github.com/brown-bnc/xnat-tools.git@v{{ mdvars.version }}
```

- Development (Main branch)

```
pip install git+https://github.com/brown-bnc/xnat-tools.git
```

### Poetry

This package is developed using [Poetry](https://python-poetry.org). If you are familiar with Poetry, you can add it to your project via

```
poetry add git+https://github.com/brown-bnc/xnat-tools.git
```

or for a tagged release

```
poetry add git+https://github.com/brown-bnc/xnat-tools.git@v{{ mdvars.version }}
```

