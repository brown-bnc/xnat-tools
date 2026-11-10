###################################################################################################
### BASE
### Enables python and installs relevant packages
###################################################################################################
# !NOTE: This must match the version in the .python-version file
FROM python:3.10.6 AS base

ENV DCM2NIIX_VERSION=v1.0.20241211

WORKDIR /xnat-tools

# Install dcm2niix (DICOM to NIfTI conversion)
RUN curl -fLO "https://github.com/rordenlab/dcm2niix/releases/download/${DCM2NIIX_VERSION}/dcm2niix_lnx.zip" \
    && unzip dcm2niix_lnx.zip \
    && mv dcm2niix /usr/bin/ \
    && rm dcm2niix_lnx.zip

# Add the project
ADD pyproject.toml ./
ADD xnat_tools ./xnat_tools

# Install python dependencies
RUN pip install .


###################################################################################################
### TEST PHASE:
### Adds xnat-tools tests and relevant dependencies
###################################################################################################
FROM base AS test

ENV DENO_VERSION=2.3.7

# Install deno (bids-validator testing)
# TODO #188: If we can run bids-validator in Python this won't be needed at all
RUN curl -fsSL https://github.com/denoland/deno/releases/download/v${DENO_VERSION}/deno-x86_64-unknown-linux-gnu.zip -o deno.zip \
    && unzip deno.zip \
    && mv deno /usr/bin/deno \
    && chmod +x /usr/bin/deno \
    && rm deno.zip


# Install python dependencies needed to run the tests
RUN pip install pytest python-dotenv responses

ADD tests ./tests


###################################################################################################
### RUNTIME
### Final runtime image of the xnat-tools application
###################################################################################################
# NOTE: This must be the final phase to be consumed properly
FROM base AS runtime