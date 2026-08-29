# Deployment and operations

Local: install, build data, train, test, then run Uvicorn as documented in the README. Cloud: authenticate with Azure CLI, create a remote Terraform state backend, copy an environment tfvars file, run `terraform init`, `terraform fmt -check`, `terraform validate`, `terraform plan -var-file=environments/dev.tfvars`, then `terraform apply` after review. Build/push the Docker image to ACR and deploy the Azure ML endpoint/API using managed identity. Registration/deployment must be conditional on offline quality gates.

Rollback by directing deployment traffic to the previous registered model version. Disable endpoints when idle. `terraform destroy -var-file=environments/dev.tfvars` removes the development stack (retention policies may preserve data). Event Hubs, Service Bus, Cosmos DB, Azure ML compute/endpoints, storage, ACR, and monitoring incur charges. Use budgets, low tiers, zero/min replicas where supported, short log retention, and scheduled shutdown.

Not independently validated without a subscription: Azure provisioning, RBAC propagation, private endpoints, real Event Hubs/Service Bus delivery, Azure ML registration/deployment, and cloud latency/cost.

