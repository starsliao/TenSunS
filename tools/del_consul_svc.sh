# Assuming localhost, substitute with actual Consul server address.
export CONSUL_HTTP_TOKEN=234dbcac-25df-42d3-965a-af4193474a56
CONSUL_HOST="http://172.26.32.83:8500"

# Get all instances of the service
SERVICE_INSTANCES=$(curl -s -H "X-Consul-Token: $CONSUL_HTTP_TOKEN" "${CONSUL_HOST}/v1/catalog/service/alicloud_dreame_app_mongodb")

# Extract the service IDs and deregister each
echo "${SERVICE_INSTANCES}" | jq -r '.[].ServiceID' | while read SERVICE_ID; do
    echo "Deregistering service instance: $SERVICE_ID"
    curl -s -X PUT -H "X-Consul-Token: $CONSUL_HTTP_TOKEN" "${CONSUL_HOST}/v1/agent/service/deregister/${SERVICE_ID}"
done