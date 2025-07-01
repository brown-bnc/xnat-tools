FROM python:3.10.6

WORKDIR /xnat-tools

ENV DCM2NIIX_VERSION=v1.0.20241211
ENV DENO_VERSION=2.3.7

ADD xnat_tools ./xnat_tools 
ADD pyproject.toml tests ./
ADD tests/ ./tests

RUN curl -fLO "https://github.com/rordenlab/dcm2niix/releases/download/${DCM2NIIX_VERSION}/dcm2niix_lnx.zip" \
    && unzip dcm2niix_lnx.zip \
    && mv dcm2niix /usr/bin/

RUN curl -fsSL https://github.com/denoland/deno/releases/download/v${DENO_VERSION}/deno-x86_64-unknown-linux-gnu.zip -o deno.zip \
    && unzip deno.zip \
    && mv deno /usr/bin/deno \
    && chmod +x /usr/bin/deno \
    && rm deno.zip

RUN pip install .
RUN pip install pytest python-dotenv responses