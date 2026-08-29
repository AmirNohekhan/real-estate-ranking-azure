resource "random_string" "suffix" { length = 6; special = false; upper = false }
locals { name = "${var.project}-${var.environment}-${random_string.suffix.result}" }
resource "azurerm_resource_group" "this" { name = "rg-${local.name}"; location = var.location; tags = var.tags }
resource "azurerm_storage_account" "lake" {
  name = replace("st${local.name}", "-", ""); resource_group_name = azurerm_resource_group.this.name
  location = var.location; account_tier = "Standard"; account_replication_type = "LRS"
  is_hns_enabled = true; min_tls_version = "TLS1_2"; shared_access_key_enabled = false; tags = var.tags
}
resource "azurerm_eventhub_namespace" "events" {
  name = "eh-${local.name}"; resource_group_name = azurerm_resource_group.this.name; location = var.location
  sku = "Basic"; capacity = 1; tags = var.tags
}
resource "azurerm_eventhub" "interactions" {
  name = "interactions"; namespace_id = azurerm_eventhub_namespace.events.id
  partition_count = 2; message_retention = 1
}
resource "azurerm_servicebus_namespace" "workflows" {
  name = "sb-${local.name}"; resource_group_name = azurerm_resource_group.this.name; location = var.location
  sku = "Standard"; tags = var.tags
}
resource "azurerm_servicebus_queue" "tour" { name = "tour-contact-workflows"; namespace_id = azurerm_servicebus_namespace.workflows.id; dead_lettering_on_message_expiration = true }
resource "azurerm_key_vault" "this" {
  name = "kv-${local.name}"; location = var.location; resource_group_name = azurerm_resource_group.this.name
  tenant_id = data.azurerm_client_config.current.tenant_id; sku_name = "standard"; enable_rbac_authorization = true
  purge_protection_enabled = true; soft_delete_retention_days = 7; tags = var.tags
}
data "azurerm_client_config" "current" {}
resource "azurerm_application_insights" "this" { name = "ai-${local.name}"; location = var.location; resource_group_name = azurerm_resource_group.this.name; application_type = "web"; tags = var.tags }
resource "azurerm_container_registry" "this" { name = replace("acr${local.name}", "-", ""); resource_group_name = azurerm_resource_group.this.name; location = var.location; sku = "Basic"; admin_enabled = false; tags = var.tags }

