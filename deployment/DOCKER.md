## Local container debugging

To make sure our environments are set up as expected and the service account we created has access to all the necessary assets in Google Cloud, we should test building and running the docker container locally.

```bash
# Build container using Dockerfile.test
docker build -f ./Dockerfile.test -t mev_boost_etl .

# Run the container in detach mode, mount the service account key as a volume and set it as an ENV var for Google Default Application login.
docker run -d -v /<absolute_path>/eden/keys/data-mev-boost-etl/<key_name>.json:/app/service-account.json -e GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json mev_boost_etl

# Tail the logs of the container using first n chars of id or the name.
docker logs -t <docker_id>|<docker_name>
```
