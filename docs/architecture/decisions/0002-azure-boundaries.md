# ADR 0002: Azure service boundaries

Status: accepted.

Event Hubs carries high-throughput behavioral facts; Functions validates/deduplicates and updates near-real-time state. Service Bus carries durable tour/contact commands with retries and dead-letter handling. ADLS Gen2 stores offline Parquet zones; Cosmos DB serves online user/session state. Azure ML owns training jobs, quality gates, MLflow registry, and ranker endpoints. Container Apps hosts the API. Managed identities and Key Vault avoid embedded secrets. Local adapters preserve functionality without cloud credentials.

