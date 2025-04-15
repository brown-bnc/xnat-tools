FROM python:3.13


RUN mkdir -p xnat-tools
WORKDIR xnat-tools

ENV DCM2NIIX_VERSION=v1.0.20241211

RUN curl -fLO "https://github.com/rordenlab/dcm2niix/releases/download/${DCM2NIIX_VERSION}/dcm2niix_lnx.zip" \
    && unzip dcm2niix_lnx.zip \
    && mv dcm2niix /usr/bin/

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv pip install .

COPY uv.lock pyproject.toml tests xnat_tools ./
COPY xnat_tools/ ./xnat_tools 
COPY tests/ ./tests

RUN uv pip install pytest python-dotenv responses
