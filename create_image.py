from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import Image, SubResource
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import (
    NetworkInterface,
    IPConfiguration,
    Subnet,
    IPAllocationMethod,
)
import os


def create_image(subscription_id, resource_group, vm_name, image_name, location, libraries):
    # Authenticate
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    try:
        # Create vnet
        VNET_NAME = f"{vm_name}-vnet"

        network_client = NetworkManagementClient(credential, subscription_id)
        poller = network_client.virtual_networks.begin_create_or_update(
            resource_group,
            VNET_NAME,
            {
                "location": location,
                "address_space": {"address_prefixes": ["10.0.0.0/16"]},
            },
        )
        vnet_result = poller.result()

        print(
            f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}"
        )

        # Create subnet
        SUBNET_NAME = f"{vm_name}-subnet"

        network_client = NetworkManagementClient(credential, subscription_id)
        poller = network_client.subnets.begin_create_or_update(
            resource_group,
            VNET_NAME,
            SUBNET_NAME,
            {"address_prefix": "10.0.0.0/24"},
        )
        subnet_result = poller.result()

        print(
            f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}"
        )

        # Create nic
        nic_params = NetworkInterface(
            location=location,
            ip_configurations=[
                IPConfiguration(
                    name=f"{vm_name}-ip-config",
                    subnet=Subnet(id=subnet_result.id),
                    private_ip_allocation_method=IPAllocationMethod.static,
                    private_ip_address="10.0.0.9"
                )
            ]
        )

        poller = network_client.network_interfaces.begin_create_or_update(
            resource_group, f"{vm_name}-nic", nic_params
        )

        nic_result = poller.result()

        image_reference = {
            "publisher": "Canonical",
            "offer": "0001-com-ubuntu-server-jammy",
            "sku": "22_04-lts-gen2",
            "version": "latest",
        }
        poller = compute_client.virtual_machines.begin_create_or_update(
            resource_group,
            vm_name,
            {
                "location": location,
                "storage_profile": {
                    "image_reference": image_reference
                },
                "hardware_profile": {"vm_size": "Standard_DS3_v2"},
                "os_profile": {
                    "computer_name": vm_name,
                    "admin_username": os.environ.get("USERNAME", "luser"),
                    "admin_password": os.environ.get("PASSWORD", "changeThisPass##!1234"),
                },
                "network_profile": {
                    "network_interfaces": [
                        {
                            "id": nic_result.id,
                        }
                    ]
                },
            },
        )
        vm_result = poller.result()
        print(f"Provisioned virtual machine {vm_result.name}")

        run_command_parameters = {
            "command_id": "RunShellScript",
            "script": [
                f"(curl https://raw.githubusercontent.com/juliom6/datatool/refs/heads/main/scripts/install.sh -o /home/luser/install.sh && chmod +x /home/luser/install.sh && /home/luser/install.sh) >> {vm_name}-log.txt",
                f"(sudo apt install python3-pip -y && sudo python3 -m pip install {libraries} && export PYSPARK_DRIVER_PYTHON=/usr/bin/python3 && export PYSPARK_PYTHON=/usr/bin/python3) >> {vm_name}-log.txt",
            ],
        }

        poller = compute_client.virtual_machines.begin_run_command(
            resource_group, vm_name, run_command_parameters
        )
        result = poller.result()

        # Step 1: Deallocate the VM
        print("Deallocating the VM...")
        async_deallocate = compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
        async_deallocate.wait()

        # Step 2: Generalize the VM
        print("Generalizing the VM...")
        compute_client.virtual_machines.generalize(resource_group, vm_name)

        # Step 3: Create image from VM
        print("Creating image from VM...")
        image_params = Image(
            location=location,
            source_virtual_machine=SubResource(
                id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
            )
        )

        async_image_creation = compute_client.images.begin_create_or_update(
            resource_group,
            image_name,
            image_params
        )

        image = async_image_creation.result()
        print(f"Successfully created image: {image.id}")

        # Deleting resources
        vm = compute_client.virtual_machines.get(
            resource_group_name=resource_group,
            vm_name=vm_name,
            expand='instanceView'
        )

        async_delete = compute_client.virtual_machines.begin_delete(
            resource_group,
            vm_name
        )
        async_delete.wait()

        os_disk_name = vm.storage_profile.os_disk.name
        delete_os_disk_poller = compute_client.disks.begin_delete(
            resource_group_name=resource_group,
            disk_name=os_disk_name
        )
        delete_os_disk_poller.wait()

        # Delete nic
        poller = network_client.network_interfaces.begin_delete(resource_group, f"{vm_name}-nic")
        poller.wait()
    
        # Delete vnet
        poller = network_client.virtual_networks.begin_delete(
            resource_group,
            VNET_NAME
        )
        poller.wait()
    except Exception as ex:
        print(f"Error: {ex}")
        raise

# Usage

libraries = "numpy pandas msgpack scikit-learn plotly matplotlib delta-spark==3.2.0"
create_image(
    subscription_id=os.environ.get("SUBSCRIPTION_ID", ""), # place your subscription ID here
    resource_group="images-rg",
    vm_name="image-vm",
    image_name="test-image-name",
    location="canadacentral",
    libraries=libraries
)
