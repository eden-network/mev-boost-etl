# BIDS Backload

This is a simple application that will backload bids data into the bids_staging database.

## Infrastructure

### Terraform

```bash
cd {workspace}/../../terraform/bids_backload/environments/{environment}

# initialize terraform
terraform init

# plan the terraform
terraform plan

# apply the terraform
terraform apply

# destroy the terraform (if needed)

terraform destroy
```

## Connect to cluster:

```bash
gcloud container clusters get-credentials mev-boost-gke-cluster --zone us-central1-a

# check that you can connect to the cluster
kubectl get nodes
```

## Deployment

```bash
# build and push the docker image using gcloud
gcloud builds submit --config cloudbuild/backload.test.yaml .

# deploy the docker image to the kubernetes cluster
kubectl apply -f kubernetes/statefulset.test.yaml

```

## Monitor the deployment

```bash
# check the status of the pods
kubectl get pods -o wide

# check the logs of the pod
kubectl logs -f mev-boost-bids-statefulset-0

# check the status of the statefulset
kubectl get statefulset

# check the status of the service
kubectl get service
```

## Delete the deployment

```bash
# delete the statefulset
kubectl delete -f kubernetes/statefulset.test.yaml

# OR delete the statefulset using the name
kubectl delete statefulset mev-boost-bids-statefulset
```

# BIDS transfer (needs to move to bids app folder)

## Infrastructure

### Terraform

```bash
cd {workspace}/../../terraform/bids/environments/{environment}

# initialize terraform
terraform init

# plan the terraform
terraform plan

# apply the terraform
terraform apply

# destroy the terraform (if needed)

terraform destroy
```

## Deployment

```bash
# build and push the docker image using gcloud
gcloud builds submit --config cloudbuild/transfer.test.yaml .
```

# BIDS bau (needs to move to bids app folder)

## Infrastructure

### Terraform

```bash
cd {workspace}/../../terraform/bids/environments/{environment}

# initialize terraform
terraform init

# plan the terraform
terraform plan

# apply the terraform
terraform apply

# destroy the terraform (if needed)

terraform destroy
```

## Deployment

```bash
# build and push the docker image using gcloud
gcloud builds submit --config cloudbuild/transfer.bau.yaml .
```
