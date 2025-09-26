# Datatool
Cloud engine for Big Data processing based on Apache Spark

## Online Documentation

Azure virtual machine creation
https://youtu.be/KvMG8uI2CJw

Datatool app configuration
https://youtu.be/aiCwvGYi9k4

Orchestrator configuration and runtime creation
https://youtu.be/5Soq9U-ovVU

Job cluster creation
https://youtu.be/ZBDTavyjU4U

Job execution
https://youtu.be/_-j3WJiwMro

## Building Datatool

Configure ssh key

```bash
ssh-keygen -t rsa
```

Configure Django app

```bash
mkdir git && cd git && git clone https://github.com/juliom6/datatool.git && cd datatool && sudo apt update && sudo apt install python3-pip -y && sudo apt install python3-venv -y && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

Enable waitress service

```bash
sudo cp datatool.service /etc/systemd/system/datatool.service
sudo systemctl start datatool
sudo systemctl enable datatool
sudo systemctl status datatool
# sudo systemctl restart datatool
```
Additionally, enable port 8080 for inbound traffic in the Azure portal (see documentation, https://youtu.be/KvMG8uI2CJw).

Configure Orchestrator

Instalar Azure CLI

```bash
chmod +x ./run.sh
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
```

Set enviroment variable
```bash
sudo nano /etc/environment
```
and add the variable SUBSCRIPTION_ID="xyz" with the subscription id from Azure account and login again. Then, create a runtime for the cluster
```bash
python create_image.py
```

Create a job cluster
```bash
.\scripts\create_cluster.ps1
```


and finally execute the job created
```bash
./run.sh 165b7f0a-01f2-421a-8892-41335d19bf93
```

<sub>From <a href="https://en.wikipedia.org/wiki/Jauja" >Jauja</a> with 💙.</sub>