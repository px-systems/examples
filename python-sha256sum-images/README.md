# python-sha256sum-images

Hash NASA Artemis II images in parallel: locally across CPU cores, then on a cluster.
Zero deps, stdlib Python.

New to PX?
The [Quick Start](https://px.app/docs/quick-start) walks through installing the CLI, authenticating with your cloud, and running your first parallel job.
This example assumes you have PX installed and gcloud SDK configured with an active project.

## What this does

`sha256sum.py` reads file paths (from argv or stdin), computes the SHA-256 of each file, and prints `<hex>  <path>` lines in `sha256sum`-compatible format.
We run it across 50 high-resolution Artemis II images that NASA released to the public domain.
Locally, you'll see parallelism across your CPU cores.
On a cluster, the same command spreads the work across worker nodes.

## Get the data locally

Download the sample from the public bucket into `./images/`:

```bash
gsutil -m cp 'gs://px-public-examples-dev/artemis-2-sample/*' images/
```

The glob (`*`) drops every object into `images/` without nesting an `artemis-2-sample/` subdir locally.

If you prefer `rclone` (cross-cloud workflows):

```bash
rclone copy :gcs,anonymous=true:px-public-examples-dev/artemis-2-sample/ images/
```

## Run locally

Hash everything in `./images/` across four parallel tasks:

```bash
find images/ -type f | px run -p 4 'python3 sha256sum.py'
```

The output is in `sha256sum`-compatible format, so you can pipe it through `sha256sum -c` to verify later.

## Submit to the cluster

This example ships its own `px.yaml` because it needs `file_mounts` to access the image bucket.
Spin up a cluster with it (run from this directory so `px` picks up `./px.yaml`):

```bash
px cluster up my-cluster
```

Then submit the job:

```bash
find images/ -type f | sed 's|^images/|/px-public-examples-dev/artemis-2-sample/|' | px job submit -c my-cluster -p 8 'python3 sha256sum.py'
```

The cluster mounts the public bucket at `/px-public-examples-dev/` (defined in `px.yaml`'s `file_mounts` block).
The `sed` rewrite swaps the local `images/` prefix for the cluster mount path, so the job reads from the bucket instead of the laptop.
The `-p 8` distributes work across both workers (`num_nodes: 3` = 1 head + 2 workers, so 4 parallel tasks per worker).

## How `px.yaml` works

Two important blocks in this example's `px.yaml`:

- `file_mounts` mounts the public Artemis II bucket at `/px-public-examples-dev/` on every node, read-only.
  Since `sha256sum.py` only reads, no write access is needed.
- `setup:` runs once per node at cluster bring-up.
  GCP's default image already ships with `python3`, but we install it explicitly so the pattern is visible.
  For any real workload, this is where your system deps go.

## Tearing down

When you're done, terminate the cluster to stop billing:

```bash
px cluster down my-cluster
```
