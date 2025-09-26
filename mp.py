import sqlite3, datetime, os, time, sys
from multiprocessing import Pool
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network.models import (
    NetworkInterface,
    IPConfiguration,
    Subnet,
    IPAllocationMethod,
    PublicIPAddress,
    NetworkSecurityGroup,
    SecurityRule,
    SecurityRuleProtocol
)
from utils.functions import dict_factory


def configure_driver(vm_name, node_type, node_rol, private_ip):
    if node_rol == "D":

        header_template = f"""from pyspark.sql import SparkSession
from delta import *

builder = (
SparkSession.builder.appName(\\"Datatool app\\")
.config(\\"spark.sql.extensions\\", \\"io.delta.sql.DeltaSparkSessionExtension\\")
.config(
    \\"spark.sql.catalog.spark_catalog\\",
    \\"org.apache.spark.sql.delta.catalog.DeltaCatalog\\",
)
.config(\\"spark.executor.memory\\", \\"9g\\")
.config(\\"spark.executor.cores\\", \\"4\\")
.config(\\"spark.default.parallelism\\", \\"100\\")
)
spark = configure_spark_with_delta_pip(builder).getOrCreate()

root_path = \\"abfss://{CONTAINER_NAME}@{STORAGE_NAME}.dfs.core.windows.net\\"

spark.sparkContext._jsc.hadoopConfiguration().set(
\\"fs.azure.account.key.{STORAGE_NAME}.dfs.core.windows.net\\", \\"{ACCESS_KEY}\\"
)

#######
"""

        run_command_parameters = {
            "command_id": "RunShellScript",
            "script": [
                f"echo \"{header_template}\" > /home/luser/script.py",
                f"curl {SCRIPT_URL} -o /home/luser/tmp",
                f"cat /home/luser/tmp >> /home/luser/script.py && rm /home/luser/tmp",
                f"echo \"{authorized_key}\" > /home/luser/.ssh/authorized_keys",
            ],
        }

        poller = compute_client.virtual_machines.begin_run_command(
            RESOURCE_GROUP_NAME, vm_name, run_command_parameters
        )
        result = poller.result()

        global CREATE_FROM_IMAGE
        if CREATE_FROM_IMAGE == 0:
            # Installing Spark
            os.system(f'ssh -o StrictHostKeyChecking=no luser@{ip_address_result.ip_address} "(curl https://raw.githubusercontent.com/juliom6/datatool/refs/heads/main/scripts/install.sh -o /home/luser/install.sh && chmod +x /home/luser/install.sh && /home/luser/install.sh) >> {vm_name}-log.txt"')
            # Installing libraries
            os.system(f'ssh -o StrictHostKeyChecking=no luser@{ip_address_result.ip_address} "(sudo apt install python3-pip -y;sudo python3 -m pip install numpy pandas msgpack scikit-learn plotly matplotlib delta-spark==3.2.0;export PYSPARK_DRIVER_PYTHON=/usr/bin/python3;export PYSPARK_PYTHON=/usr/bin/python3) >> {vm_name}-log.txt"')

        # Cluster initialization
        os.system(f'ssh -o StrictHostKeyChecking=no luser@{ip_address_result.ip_address} "/opt/spark/sbin/start-master.sh"')

        # Collect master URL
        MASTER_URL = ""
        while MASTER_URL == "":
            time.sleep(5)
            result = os.popen(f'ssh -o StrictHostKeyChecking=no luser@{ip_address_result.ip_address} "curl http://{private_ip}:8080/"').read()
            inicio = result.find("<li><strong>URL:</strong> ")
            fin = result.find(":7077</li>")
            MASTER_URL = result[inicio + len("<li><strong>URL:</strong> ") : fin + len(":7077")]

        print(f"Master node running in {MASTER_URL} ({ip_address_result.ip_address}:8080)")

    return MASTER_URL

def configure_workers(vm_name, node_type, node_rol, private_ip):
    if node_rol == "W":
        global MASTER_URL
        global CREATE_FROM_IMAGE
        if CREATE_FROM_IMAGE == 1:
            run_command_parameters = {
                "command_id": "RunShellScript",
                "script": [
                    f"/opt/spark/sbin/start-worker.sh {MASTER_URL}",
                ],
            }
        if CREATE_FROM_IMAGE == 0:
            run_command_parameters = {
                "command_id": "RunShellScript",
                "script": [
                    f"(curl https://raw.githubusercontent.com/juliom6/datatool/refs/heads/main/scripts/install.sh -o /home/luser/install.sh && chmod +x /home/luser/install.sh && /home/luser/install.sh) >> {vm_name}-log.txt",
                    f"(sudo apt install python3-pip -y && sudo python3 -m pip install numpy pandas msgpack scikit-learn plotly matplotlib delta-spark==3.2.0 && export PYSPARK_DRIVER_PYTHON=/usr/bin/python3 && export PYSPARK_PYTHON=/usr/bin/python3) >> {vm_name}-log.txt",
                    f"/opt/spark/sbin/start-worker.sh {MASTER_URL}",
                ],
            }

        poller = compute_client.virtual_machines.begin_run_command(
            RESOURCE_GROUP_NAME, vm_name, run_command_parameters
        )
        result = poller.result()


def create_node(vm_name, node_type, node_rol, private_ip):

    ip_config_name = f"{vm_name}-ip-config"
    nic_name = f"{vm_name}-nic"

    if node_rol == "D":

        nic_params = NetworkInterface(
            location=LOCATION,
            ip_configurations=[
                IPConfiguration(
                    name=ip_config_name,
                    subnet=Subnet(id=subnet_result.id),
                    private_ip_allocation_method=IPAllocationMethod.static,
                    private_ip_address=private_ip,
                    public_ip_address=PublicIPAddress(id=ip_address_result.id)
                )
            ],
            network_security_group=NetworkSecurityGroup(id=nsg_result.id)
        )

    if node_rol == "W":

        nic_params = NetworkInterface(
            location=LOCATION,
            ip_configurations=[
                IPConfiguration(
                    name=ip_config_name,
                    subnet=Subnet(id=subnet_result.id),
                    private_ip_allocation_method=IPAllocationMethod.static,
                    private_ip_address=private_ip
                )
            ],
            network_security_group=NetworkSecurityGroup(id=nsg_result.id)
        )

    poller = network_client.network_interfaces.begin_create_or_update(
        RESOURCE_GROUP_NAME, nic_name, nic_params
    )

    nic_result = poller.result()

    print(f"Provisioned network interface client {nic_result.name}")

    global IMAGE_ID
    with_image = {
        "id": IMAGE_ID,
    }
    without_image = {
        "publisher": "Canonical",
        "offer": "0001-com-ubuntu-server-jammy",
        "sku": "22_04-lts-gen2",
        "version": "latest",
    }
    global CREATE_FROM_IMAGE
    poller = compute_client.virtual_machines.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        vm_name,
        {
            "location": LOCATION,
            "storage_profile": {
                "image_reference": with_image if CREATE_FROM_IMAGE == 1 else without_image
            },
            "hardware_profile": {"vm_size": node_type},
            "os_profile": {
                "computer_name": vm_name,
                "admin_username": USERNAME,
                "admin_password": PASSWORD,
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
    return vm_result


if __name__ == "__main__":

    # collects clusters data
    con = sqlite3.connect("/home/luser/git/datatool/db.sqlite3")
    con.row_factory = dict_factory
    cursor = con.execute(f"select * from api_cluster where cluster_id = '{sys.argv[1].replace("-", "")}'")
    lista_clusters = cursor.fetchall()
    cluster = lista_clusters[0]
    con.close()

    inicio_ejecucion = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    # Define variables
    credential = DefaultAzureCredential()
    SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID", "56f26a54-203e-406e-9b0f-0740228ad179")
    CLUSTER_ID = cluster["cluster_id"]
    LOCATION = "canadacentral"
    RESOURCE_GROUP_NAME = f"{CLUSTER_ID}-rg"
    NUM_WORKERS = cluster["num_workers"]
    WORKER_NODE_TYPE = cluster["worker_node_type"]
    DRIVER_NODE_TYPE = cluster["driver_node_type"]
    SCRIPT_URL = cluster["python_script_url"]
    STORAGE_NAME = cluster["storage_name"]
    CONTAINER_NAME = cluster["container_name"]
    ACCESS_KEY = cluster["access_key"]
    DELETE_AFTER_EXECUTION = cluster["delete_after_execution"]
    CREATE_FROM_IMAGE = cluster["create_from_image"]
    IMAGE_ID = cluster["image_id"]

    USERNAME = os.environ.get("USERNAME", "luser")
    PASSWORD = os.environ.get("PASSWORD", "changeThisPass##!1234")
    MASTER_URL = ""

    # set cluster_status = 1
    con = sqlite3.connect("/home/luser/git/datatool/db.sqlite3")
    cur = con.cursor()
    cur.execute(f"update api_cluster set cluster_status = 1 where cluster_id = '{CLUSTER_ID}'")
    con.commit()
    con.close()

    ############# Global variables
    public_key_path = "~/.ssh/id_rsa.pub"
    with open(os.path.expanduser(public_key_path), 'r') as f:
        authorized_key = f.read().strip()

    ############# Init cluster creation

    # Create resource group
    resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
    rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME, {"location": LOCATION})
    print(f'Provisioned resource group {rg_result.name} in the {rg_result.location} region')

    # Create virtual network
    VNET_NAME = f"{CLUSTER_ID}-vnet"

    network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)
    poller = network_client.virtual_networks.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        VNET_NAME,
        {
            "location": LOCATION,
            "address_space": {"address_prefixes": ["10.0.0.0/16"]},
        },
    )
    vnet_result = poller.result()

    print(
        f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}"
    )

    # Create subnet
    SUBNET_NAME = f"{CLUSTER_ID}-subnet"

    network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)
    poller = network_client.subnets.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        VNET_NAME,
        SUBNET_NAME,
        {"address_prefix": "10.0.0.0/24"},
    )
    subnet_result = poller.result()

    print(
        f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}"
    )

    # Create master node
    VM_MASTER_NAME = f"{CLUSTER_ID}-m-vm"

    # Create public ip
    IP_PUBLIC_NAME = f"{VM_MASTER_NAME}-pub-ip"

    network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)
    poller = network_client.public_ip_addresses.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        IP_PUBLIC_NAME,
        {
            "location": LOCATION,
            "sku": {"name": "Standard"},
            "public_ip_allocation_method": "Static",
            "public_ip_address_version": "IPV4",
        },
    )
    ip_address_result = poller.result()

    print(
        f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}"
    )

    # Enable ports (22, 8080, 8081)
    NSG_NAME = f"{VM_MASTER_NAME}-nsg"

    security_rules = [
        SecurityRule(
            name='allow-ssh',
            access='Allow',
            direction='Inbound',
            priority=100,
            protocol=SecurityRuleProtocol.tcp,
            source_address_prefix='*',
            source_port_range='*',
            destination_address_prefix='*',
            destination_port_range='22',
            description='Allow SSH traffic'
        ),
        SecurityRule(
            name='allow-8080-traffic',
            access='Allow',
            direction='Inbound',
            priority=300,
            protocol=SecurityRuleProtocol.tcp,
            source_address_prefix='*',
            source_port_range='*',
            destination_address_prefix='*',
            destination_port_range='8080',
            description='Allow 8080 traffic'
        ),
        SecurityRule(
            name='allow-8081-traffic',
            access='Allow',
            direction='Inbound',
            priority=400,
            protocol=SecurityRuleProtocol.tcp,
            source_address_prefix='*',
            source_port_range='*',
            destination_address_prefix='*',
            destination_port_range='8081',
            description='Allow 8081 traffic'
        ),
    ]

    nsg_params = NetworkSecurityGroup(
        location=LOCATION,
        security_rules=security_rules
    )
    poller = network_client.network_security_groups.begin_create_or_update(
        RESOURCE_GROUP_NAME, NSG_NAME, nsg_params
    )

    nsg_result = poller.result()

    ##################################
    compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
    node_list = []
    node_list.append((VM_MASTER_NAME, DRIVER_NODE_TYPE, "D", "10.0.0.10"))
    for e in range(NUM_WORKERS):
        node_list.append((f"{CLUSTER_ID}-w{e+1}-vm", WORKER_NODE_TYPE, "W", f"10.0.0.{11 + e}"))

    with Pool(3) as pool:
        b = pool.starmap(create_node, node_list)
    ##################################
    print("Start config driver.")
    with Pool(3) as pool:
        b = pool.starmap(configure_driver, node_list[:1])
    print("Fin config driver.")
    MASTER_URL = b[0]
    ##################################
    print("Start config workers.")
    with Pool(3) as pool:
        b = pool.starmap(configure_workers, node_list[1:])
    print("End config workers.")
    ##################################

    # Execute job
    res = os.popen(f'ssh -o StrictHostKeyChecking=no luser@{ip_address_result.ip_address} "/opt/spark/bin/spark-submit --master {MASTER_URL} /home/luser/script.py"').read()
    print(res)

    fin_ejecucion = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    # set cluster_status = 2
    con = sqlite3.connect("/home/luser/git/datatool/db.sqlite3")
    cur = con.cursor()
    cur.execute(f"update api_cluster set cluster_status = 2, message = '{res}', uri_master = '{MASTER_URL}', ip = '{ip_address_result.ip_address}', start_timestamp = '{inicio_ejecucion}', end_timestamp = '{fin_ejecucion}' where cluster_id = '{CLUSTER_ID}'")
    con.commit()
    con.close()

    if DELETE_AFTER_EXECUTION == 1:
        print("Deleting resource group {}".format(RESOURCE_GROUP_NAME))
        async_operation = resource_client.resource_groups.begin_delete(RESOURCE_GROUP_NAME)
        async_operation.wait()
        print("Resource group {} deleted successfully.".format(RESOURCE_GROUP_NAME))
