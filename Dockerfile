FROM python:3.10.6

ENV POETRY_VERSION=1.0.3
ENV DCM2NIIX_VERSION=v1.0.20190902

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Install bids-validator using npm
RUN npm install -g bids-validator

RUN mkdir -p xnat-tools
WORKDIR xnat-tools

RUN curl -fLO "https://github.com/rordenlab/dcm2niix/releases/download/${DCM2NIIX_VERSION}/dcm2niix_lnx.zip" \
    && unzip dcm2niix_lnx.zip \
    && mv dcm2niix /usr/bin/ \
    && mv dcm2niibatch /usr/bin/

COPY poetry.lock pyproject.toml tests xnat_tools ./
COPY xnat_tools/ ./xnat_tools 
COPY tests/ ./tests

RUN pip install . 