$uri = "http://<ip>:8080/api/v1/token/"
$body = @{
    username = "jorge"
    password = "Abcd1234"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "Accept" = "application/json"
}

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -Headers $headers

$authAccess = $response.access
$authRefresh = $response.refresh

# $authAccess
# $authRefresh

##########################################################################
# Create cluster
$uri = "http://<ip>:8080/api/v1/clusters/create/"
$body = @{
    cluster_name = "test_cluster"
    worker_node_type = "Standard_DS3_v2"
    driver_node_type = "Standard_DS3_v2"
    num_workers = 2
    python_script_url = "https://raw.githubusercontent.com/juliom6/datatool/refs/heads/main/examples/read_write_dataframe.py"
    storage_name = "xyz123456789"
    container_name = "testcontainer"
    access_key = "<access key from Azure portal>"
    delete_after_execution = "true"
    create_from_image = "true"
    image_id = "/subscriptions/56f26a54-203e-406e-9b0f-0740228ad179/resourceGroups/images-rg/providers/Microsoft.Compute/images/test-image-name"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "Accept" = "application/json"
    "Authorization" = "Bearer $authAccess"
}

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -Headers $headers
$response