## Setting Up your Development Environment

This instructions are for MacOS, while they should roughly be the same for Windows and Linux, they are untested in those environments:

## 1. Package Manager 

[Homebrew](https://brew.sh) is a popular package manager for MacOS. It can be installed as follows:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

[Chocolatey](https://chocolatey.org) is a popular package manager for Windows. To install, run the following from a priviledged powershell prompt:


```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```



## 2. PYENV

### Installation

[`pyenv`](https://github.com/pyenv/pyenv) allows you to run and manage multiple versions of Python, all in isolations from your system's Python.
If this is your first time using `pyenv` you can learn more about isuing it in [this blog post](https://realpython.com/intro-to-pyenv/#exploring-pyenv-commands)

`brew install pyenv`

Append `pyenv init` to bash's profile

```
$ echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bash_profile
```

And restart your SHELL

`exec "$SHELL"`

### List versions of Python available to install

`pyenv install --list`

### Install most recent stable version

A stable version means there is no `-dev` of `-rc` after the name. For instance run

`pyenv install 3.7.4`

### Activate global environment

`pyenv global 3.7.4`

### Listing available versions to the system

`pyenv versions`

### Configuring a local environment

When you are in a folder, you can configure the version of the Python that is activated when you are calling Python within that folder by calling for instance `pyenv local 3.8.0` within your directory.

This will create a hidden file `.python-version` in the current directory.

## 3. PIPX

[PIPX](https://github.com/pipxproject/pipx) allows you to install Python (and Ruby) CLI utilities in their own environment, without contaminating your global environment

### Installation

`python -m pip install pipx`

## 5. uv

[`uv`](https://docs.astral.sh/uv/) is a fast and user-friendly Python package manager and dependency resolver. It also simplifies creating and managing virtual environments.

### Installation

We recommend installing `uv` using `pipx` to keep it isolated:

```bash
pipx install uv
```

Unlike Poetry, uv does not automatically manage virtual environments. You must create and activate one manually:

```bash
uv venv 
source .venv/bin/activate 
```

You should see your shell prompt change to reflect that the virtual environment is active.

### Installing Dependencies 

With your environment active, install your project’s dependencies:

```
uv pip install -e '.[dev, docs]'
```
