# One-Time Setup — Azure OIDC for GitHub Actions

Run these once, locally, using the Azure CLI (`az login` first).
This avoids ever storing a long-lived Azure secret in GitHub.

## 1. Create a resource group (this persists; only the AKS cluster inside it is ephemeral)

az group create --name rg-infra-api-demo --location westus2

## 2. Create an App Registration for GitHub OIDC

az ad app create --display-name "github-infra-api-demo"
# Note the "appId" from the output — this is your AZURE_CLIENT_ID

APP_ID="<paste appId here>"

az ad sp create --id $APP_ID

## 3. Create a federated credential trusting this specific repo + workflow

az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-infra-api-demo-fic",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:shanecthomas/gitops-helm-argocd-demo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

## 4. Scope Contributor role to ONLY the resource group created in step 1 (least privilege)

SUBSCRIPTION_ID=$(az account show --query id -o tsv)

az role assignment create \
  --assignee $APP_ID \
  --role Contributor \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/rg-infra-api-demo

## 5. Get the values you need for GitHub repo secrets

echo "AZURE_CLIENT_ID:       $APP_ID"
echo "AZURE_TENANT_ID:       $(az account show --query tenantId -o tsv)"
echo "AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"

## 6. Add these as GitHub repo secrets

Settings -> Secrets and variables -> Actions -> New repository secret:
  AZURE_CLIENT_ID
  AZURE_TENANT_ID
  AZURE_SUBSCRIPTION_ID

No AZURE_CLIENT_SECRET is needed — OIDC replaces it entirely.
