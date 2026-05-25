# python-jpg-to-jxl

Convert NASA Artemis II images in parallel: locally across CPU cores, then on a cluster.

New to PX?
The [Quick Start](https://px.app/docs/quick-start) walks through installing the CLI, authenticating with your cloud, and running your first parallel job.
This example assumes you have PX installed and gcloud SDK configured with an active project.

## What this does

`jpg-to-jxl.py` reads file paths (from argv or stdin), converts it to jxl, and prints the new file's path.
We run it across 50 high-resolution Artemis II images that NASA released to the public domain.
Locally, you'll see parallelism across your CPU cores.
On a cluster, the same command spreads the work across worker nodes.

## Get the data locally

You can run with local data using PX's public bucket with NASA Artemis II images.
Download the samples into `./images/` with:

```bash
mkdir -p images && gsutil -m cp 'gs://px-public-examples-dev/artemis-2-sample/*' images/
```

If you prefer `rclone` (cross-cloud workflows):

```bash
rclone copy :gcs,anonymous=true:px-public-examples-dev/artemis-2-sample/ images/
```

## Run locally

Convert everything in `./images/` across four parallel tasks:

```bash
# Install System Dependencies
apt-get install libmagickwand-dev
# Install python Dependencies
uv sync
# Find and convert images
find images/ -type f | px run -p 4 './.venv/bin/python3 jpg-to-jxl.py'
```

## Run in cluster with your images

This example ships its own `px.yaml` example, but you will need to fill in `<REPLACE-WITH-YOUR-BUCKET-NAME>`

```bash
px cluster up jpg-to-jxl
```

Then submit the job:

```bash
# Generate an argument list of the files you want to convert. The cluster
# mounts the bucket as defined inside your `file_mounts` section in px.yaml
ssh jpg-to-jxl 'find /<REPLACE-WITH-YOUR-BUCKET-NAME> -name *.jpg' > jpg-to-jxl-args
# Submit the job
px job submit -c jpg-to-jxl -a jpg-to-jxl-args -p 4 '.venv/bin/python3 jpg-to-jxl.py'
```

## Tearing down

When you're done, terminate the cluster to stop billing:

```bash
px cluster down jpg-to-jxl
```
