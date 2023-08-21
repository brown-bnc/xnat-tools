FROM python:3.10.6

ENV POETRY_VERSION=1.0.3
ENV DCM2NIIX_VERSION=v1.0.20230411

RUN mkdir -p xnat-tools
WORKDIR xnat-tools

RUN curl -fLO "https://github.com/rordenlab/dcm2niix/releases/download/${DCM2NIIX_VERSION}/dcm2niix_lnx.zip" \
    && unzip dcm2niix_lnx.zip \
    && mv dcm2niix /usr/bin/ 

COPY poetry.lock pyproject.toml tests xnat_tools ./
COPY xnat_tools/ ./xnat_tools 
COPY tests/ ./tests

RUN pip install .
RUN pip install pytest python-dotenv responses