FROM ghcr.io/astral-sh/uv:python3.10-bookworm

WORKDIR /xnat-tools

ENV VIRTUAL_ENV=/xnat-tools/.venv

ENV DCM2NIIX_VERSION=v1.0.20241211

# Copy project files into container
ADD xnat_tools ./xnat_tools 
ADD uv.lock pyproject.toml tests ./
ADD tests/ ./tests

# dcm2niix must be fetched——cannot be built locally via uv
RUN curl -fLO "https://github.com/rordenlab/dcm2niix/releases/download/${DCM2NIIX_VERSION}/dcm2niix_lnx.zip" \
    && unzip dcm2niix_lnx.zip \
    && mv dcm2niix /usr/bin/

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project 

# Installing separately from its dependencies allows optimal layer caching
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen 
    
# Add dev/test tools like pytest, dotenv, responses
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install pytest python-dotenv responses

ENV PATH="$VIRTUAL_ENV/bin:$PATH"