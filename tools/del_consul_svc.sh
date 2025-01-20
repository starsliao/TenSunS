# Assuming localhost, substitute with actual Consul server address.
export CONSUL_HTTP_TOKEN=xxxxxx
CONSUL_HOST="http://172.26.32.83:8500"

# Get all instances of the service
SERVICE_INSTANCES=$(curl -s -H "X-Consul-Token: $CONSUL_HTTP_TOKEN" "${CONSUL_HOST}/v1/catalog/service/alicloud_dreame_devops_rds")

# Extract the service IDs and deregister each
echo "${SERVICE_INSTANCES}" | jq -r '.[].ServiceID' | while read SERVICE_ID; do
    echo "Deregistering service instance: $SERVICE_ID"
    curl -s -X PUT -H "X-Consul-Token: $CONSUL_HTTP_TOKEN" "${CONSUL_HOST}/v1/agent/service/deregister/${SERVICE_ID}"
done