# OCI Designer Toolkit Installation Guide

Although OKIT can simply be downloaded and the command line executed it is recommended that it be executed within a
docker container that can be built using the Dockerfile within this repository. This will guarantee that all the required 
python modules are installed and in addition provide a simple flask server that will present the web based application on
[http://localhost/okit/designer](http://localhost/okit/designer).


## Table of Contents

1. [OCI Connection Information](#oci-connection-information)
    1. [Key File](#key-file)
    2. [Config File](#config-file)
2. [Git Connection](#git-connection)
    1. [GIT Repositories File](#git-repository-file)
3. [Quick Start Runtime](#quick-start-runtime)
4. [Container](#container)
    1. [Docker](#docker)
    2. [Lima (MacOS)](#lima-macos)
    3. [Vagrant / VirtualBox](#vagrant--virtualbox)
5. [Native](#native)
    1. [Oracle Linux](oracle-linux)
    2. [macOS](#macos)
3. [Build From Source](#build-from-source)
    1. [OKIT Repository](#okit-repository)
    2. [Create Container](#create-container)
        1. [Docker Compose](#docker-compose)
        2. [Docker](#docker)
        3. [Vagrant](#vagrant)
4. [Install on OCI Instance](#install-on-oci-instance)
    1. [OpenID Connect Configuration for IDCS](#openid-connect-configuration-for-idcs)
    2. [Dynamic Group](#dynamic-group)
    3. [Policies](#policies)
    4. [SSH Tunnel](#ssh-tunnel)
5. [Install on Oracle Linux](#install-on-oracle-linux)










## OCI Connection Information

If you already have the OCI sdk/cli installed on you machine you can use the previously generated pem key and config file
we will assume that this exists in &lt;USER HOME DIR&gt;/.oci 

### Key File

If you do not have a previously generated private key you will need to create a private/public key pair for use with OKIT and OCI.
These keys can be generated using the following commands as defined in [Required Keys and OCIDs](https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm).

```bash
openssl genrsa -out <USER HOME DIR>/.oci/oci_api_key.pem 2048   
openssl rsa -pubout -in <USER HOME DIR>/.oci/oci_api_key.pem -out <USER HOME DIR>/.oci/oci_api_key_public.pem                                  
```

Upload the generated __oci_api_key_public.pem__ to OCI through the [console](https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm) and record the associated fingerprint following upload.

### Config File

Create the OCI cli __config__ file in the directory __&lt;USER HOME DIR&gt;/.oci__ with contents similar to that below.
The __*key_file*__ is a fixed value because the contents of the __&lt;USER HOME DIR&gt;/.oci__ will be mounted to the
appropriate users home directory, as __~/.oci__, during the run process.

```properties
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaak6z......
fingerprint=3b:7e:37:ec:a0:86:1....
key_file=~/.oci/oci_api_key.pem  
tenancy=ocid1.tenancy.oc1..aaaaaaaawpqblfem........
region=us-phoenix-1
```
Further information on the config file can be found on the OCI sdk page [SDK and CLI Configuration File](https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm).










## Git Connection

### GIT Repositories File

If Git integration is required you will need to create a __git_repositories__ file within the directory
__&lt;USER HOME DIR&gt;/.oci__ with contents similar to that below.

```properties
[OKIT Community]
branch = master
url = git@url1.git

[Internal]
branch = BRANCHNAME
url = git@url2.git
```

This properties file contains a list of the Git repositories you want to access. It assumes that you are using public/private
key access and the key files exist within your __&lt;USER HOME DIR&gt;/.ssh__ directory and the __&lt;USER HOME DIR&gt;/.ssh/config__
defines the key/url mapping.











## Quick Start Runtime

Docker is the recommended runtime container for OKIT and the project contains a top-level Dockerfile to facilitate direct
building, of the runtime environment, from the docker command line.

### Build Docker Container
```bash
docker build --tag okit --no-cache --force-rm https://github.com/oracle/oci-designer-toolkit.git
```

### Run Container

```bash
docker run -d --rm -p 80:80 --volume <USER HOME DIR>/okit/user/templates:/okit/templates --volume <USER HOME DIR>/.oci:/root/.oci --volume <USER HOME DIR>/.ssh:/root/.ssh --name okit okit
```

Once started the Designer BUI can be accessed on [http://localhost/okit/designer](http://localhost/okit/designer)










## Container

### Docker

The docker image  can be built and started using the scripts in the docker sub directory.
It should be noted that the current Docker script is designed for development purposes and mounts the source directories
at runtime. 

#### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop).
- Create local directory __~/okit/user/templates__ for storage of custom templates.
- [Copy Config & Key Files](#copy-config--key-files)

#### Docker Build
```bash
cd oci-designer-toolkit
docker build --tag okit --file ./containers/docker/Dockerfile --force-rm .
```

#### Docker Update
```bash
cd oci-designer-toolkit
docker rmi okit
docker build --tag okit --no-cache --file ./Dockerfile --force-rm .
```

#### Start Docker Container
```bash
cd oci-designer-toolkit
docker run -d --rm -p 80:80 
        --name okit \
        --hostname okit \
        --volume <USER HOME DIR>/.oci:/root/.oci \
        --volume <USER HOME DIR>/.ssh:/root/.ssh \
        --volume <PATH TO USER TEMPLATES DIR>:/okit/instance/templates/user \
        --volume <PATH TO GIT DIR>:/okit/instance/git \
        --volume <PATH TO LOCAL DIR>:/okit/instance/local \
        okit
```

### Lima (MacOS)

[Lima](https://github.com/lima-vm/lima) is an alternative option to Docker Desktop to run a container based OKIT installation on MacOS. 
It will build a container based on the existing Dockerfile without any modifications.

Install Lima using Homebrew
```bash
brew install lima
```

Lima runs a Linux VM in the background that is used for running the containers, to start the Lima VM service run
```bash
limactl start
```

Lima uses containerd as its container run-time and nertctl as the Docker-compatible CLI for containerd. 
As containerd is running in the VM, not on the Mac directly the lima command passes the nerdctl commands to the VM.  
For most docker commands the equivalent is to run lima nerdctl

With Lima installed and running we need to build the OKIT container, replacing the regular docker build with
```bash
cd oci-designer-toolkit
lima nerdctl rmi okit
lima nerdctl build --tag okit --no-cache --file ./Dockerfile .
```

Run OKIT using the container run command, adjust or add additional required volume mounts as required
```bash
lima nerdctl run --rm -p 80:80 \
        --name okit \
        --hostname okit \
        --volume <USER HOME DIR>/.oci:/root/.oci \
        --volume <USER HOME DIR>/.ssh:/root/.ssh \
        --volume <PATH TO USER TEMPLATES DIR>:/okit/instance/templates/user \
        --volume <PATH TO GIT DIR>:/okit/instance/git \
        --volume <PATH TO LOCAL DIR>:/okit/instance/local \
        okit
```

To stop the OKIT container
```bash
lima nerdctl stop okit
```

To stop the Lima service VM
```bash
limactl stop
```

### Vagrant / VirtualBox

#### Prerequisites
- Install [Oracle VM VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- Install [Vagrant](https://vagrantup.com/)
- Create local directory __~/okit/user/templates__ for storage of custom templates.
- [Copy Config & Key Files](#copy-config--key-files)

#### Vagrant Build

##### MacOS / Linux
```bash
cd oci-designer-toolkit/containers/vagrant
vagrant up; vagrant reload; vagrant ssh
```
##### Windows
```bash
cd oci-designer-toolkit\containers\vagrant
vagrant up & vagrant reload & vagrant ssh
```
**NOTE**: This step takes about 30 minutes on my mac when you build the VM, a little longer the first time as the Vbox image 
is downloaded from github. Once the VM is built the vagrant up should just take a few seconds.










## Native

### Oracle Linux

If you have a Linux machine and would like to install OKIT directly without the need for Docker or Vagrant then 
this can be achieved using the following simple instructions. We assume that you have already created the appropriate OCI SDK config
file in ~/.oci and associated ssh keys/config in ~/.ssh.

The instructions below give 2 options for the server either HTTP or HTTPS and it is up to the user to choose the appropriate 
command based on their requirements.

These instructions will install OKIT in the root directory __/okit__. If you would like OKIT in an alternative directory 
modify the OKIT_DIR environment variable. In addition the __/etc/systemd/system/gunicorn.service__ and __${OKIT_DIR}/config/gunicorn_http*.py__ 
files will need to modified to reflect this new location.

```bash
export OKIT_DIR='/okit'
# Install Required Packages 
sudo bash -c "yum install -y git"
sudo bash -c "yum install -y openssl"
sudo bash -c "yum install -y oci-utils"
# This is not required for OL8
sudo bash -c "yum install -y python-oci-cli"
# Install Required Python Modules
sudo bash -c "python3 -m pip install -U pip"
sudo bash -c "python3 -m pip install -U setuptools"
sudo bash -c "python3 -m pip install --no-cache-dir authlib flask gitpython git-url-parse gunicorn oci openpyxl pandas python-magic pyyaml requests xlsxwriter"
# Clone OKIT
sudo bash -c "git clone -b master --depth 1 https://github.com/oracle/oci-designer-toolkit.git ${OKIT_DIR}"
sudo bash -c "mkdir -p ${OKIT_DIR}/{git,local,log,instance/git,instance/local,instance/templates/user,workspace,ssl}"
# Link Reference Architecture Templates to Template Directory
sudo bash -c "ln -sv ${OKIT_DIR}/okitweb/static/okit/templates/reference_architecture ${OKIT_DIR}/instance/templates/reference_architecture"
# Add additional environment information 
sudo bash -c "echo 'export OKIT_DIR=:${OKIT_DIR}' >> /etc/bashrc"
sudo bash -c "echo 'export PYTHONPATH=:${OKIT_DIR}/visualiser:${OKIT_DIR}/okitweb:/okit' >> /etc/bashrc"
sudo bash -c "echo 'export PATH=$PATH:/usr/local/bin' >> /etc/bashrc"
# Generate ssl Self Sign Key
sudo bash -c "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ${OKIT_DIR}/ssl/okit.key -out ${OKIT_DIR}/ssl/okit.crt -subj '/C=GB/ST=Berkshire/L=Reading/O=Oracle/OU=OKIT/CN=www.oci_okit.com'"

##################################################################################################################
#####                        If HTTPS / 443 Is required                                                      #####
##### Copy GUnicorn Service File (HTTPS)                                                                     #####
##################################################################################################################
sudo bash -c "cp -v ${OKIT_DIR}/containers/services/gunicorn.https.service /etc/systemd/system/gunicorn.service"
##################################################################################################################
#####                        If HTTP / 80 Is required                                                        #####
##### Copy GUnicorn Service File (HTTP)                                                                      #####
##################################################################################################################
sudo bash -c "cp -v ${OKIT_DIR}/containers/services/gunicorn.http.service /etc/systemd/system/gunicorn.service"

# Enable Gunicorn Service
sudo systemctl enable gunicorn.service
sudo systemctl start gunicorn.service
# Open Firewall
sudo firewall-offline-cmd  --add-port=80/tcp
sudo firewall-offline-cmd  --add-port=443/tcp
sudo systemctl restart firewalld
```

### MacOS

#### Package Install
Install the following packages using [Homebrew](https://brew.sh/)
```bash
brew install git
brew install python3
brew install libmagic
```

#### Install
```bash
export OKIT_DIR=${HOME}/okit
export OKIT_GITHUB_DIR=${HOME}/okit_github
export OKIT_BRANCH='master'
mkdir -p ${OKIT_DIR}
mkdir -p ${OKIT_GITHUB_DIR}
# Create Python Virtual Environment
python3 -m venv ${OKIT_DIR}/.venv
# Activate Virtual Environment
source ${OKIT_DIR}/.venv/bin/activate
# Update python & Install modules
python3 -m pip install -U pip
python3 -m pip install -U setuptools
python3 -m pip install --no-cache-dir authlib flask gitpython git-url-parse gunicorn oci openpyxl pandas python-magic pyyaml requests xlsxwriter
# Clone OKIT 
git clone -b ${OKIT_BRANCH} https://github.com/oracle/oci-designer-toolkit.git ${OKIT_GITHUB_DIR}/oci-designer-toolkit
# Create OKIT Required Directories
mkdir -p ${OKIT_DIR}/{log,instance/git,instance/local,instance/templates/user,workspace,ssl}
# Link Directories
ln -sv ${OKIT_GITHUB_DIR}/oci-designer-toolkit/config ${OKIT_DIR}/config
ln -sv ${OKIT_GITHUB_DIR}/oci-designer-toolkit/okitweb ${OKIT_DIR}/okitweb
ln -sv ${OKIT_GITHUB_DIR}/oci-designer-toolkit/visualiser ${OKIT_DIR}/visualiser
ln -sv ${OKIT_GITHUB_DIR}/oci-designer-toolkit/okitweb/static/okit/templates/reference_architecture ${OKIT_DIR}/instance/templates/reference_architecture
```

#### Run
```bash
export OKIT_DIR=${HOME}/okit
export OKIT_LOGFILE=${OKIT_DIR}/log/okit.log
export PYTHONPATH=:${OKIT_DIR}/visualiser:${OKIT_DIR}/okitweb:${OKIT_DIR}
# Activate Virtual Environment
source ${OKIT_DIR}/.venv/bin/activate
# Run Server
${OKIT_DIR}/.venv/bin/gunicorn okitweb.wsgi:app --config ${OKIT_DIR}/config/gunicorn_http.py
```

### Windows 10 / WSL (Ubuntu)

#### Package Install
```bash
sudo apt install git
sudo apt install python3
sudo apt install libmagic-dev
sudo apt install python3.8-venv
```

#### Install
```bash
export OKIT_DIR=${HOME}/okit
export OKIT_GITHUB_DIR=${HOME}/okit_github
export OKIT_BRANCH='master'
mkdir -p ${OKIT_DIR}
mkdir -p ${OKIT_GITHUB_DIR}
# Create Python Virtual Environment
python3 -m venv ${OKIT_DIR}/.venv
# Activate Virtual Environment
source ${OKIT_DIR}/.venv/bin/activate
# Update python & Install modules
python3 -m pip install -U pip
python3 -m pip install -U setuptools
python3 -m pip install --no-cache-dir authlib flask gitpython git-url-parse gunicorn oci openpyxl pandas python-magic pyyaml requests xlsxwriter
# Clone OKIT 
git clone -b ${OKIT_BRANCH} https://github.com/oracle/oci-designer-toolkit.git ${OKIT_GITHUB_DIR}/oci-designer-toolkit
# Create OKIT Required Directories
mkdir -p ${OKIT_DIR}/{git,local,log,instance/git,instance/local,instance/templates/user,workspace,ssl}
# Link Directories
ln -sv ${OKIT_GITHUB_DIR}/oci-designer-toolkit/config ${OKIT_DIR}/config
ln -sv ${OKIT_GITHUB_DIR}/oci-designer-toolkit/okitweb ${OKIT_DIR}/okitweb
ln -sv ${OKIT_GITHUB_DIR}/oci-designer-toolkit/visualiser ${OKIT_DIR}/visualiser
ln -sv ${OKIT_GITHUB_DIR}/oci-designer-toolkit/okitweb/static/okit/templates/reference_architecture ${OKIT_DIR}/instance/templates/reference_architecture
```

#### Run
```bash
export OKIT_DIR=${HOME}/okit
export OKIT_LOGFILE=${OKIT_DIR}/log/okit.log
export PYTHONPATH=:${OKIT_DIR}/visualiser:${OKIT_DIR}/okitweb:${OKIT_DIR}
# Activate Virtual Environment
source ${OKIT_DIR}/.venv/bin/activate
# Run Server
${OKIT_DIR}/.venv/bin/gunicorn okitweb.wsgi:app --config ${OKIT_DIR}/config/gunicorn_http.py
```

__Note:__ You may need to replace "localhost" in the OKIT URL with the IP Address of you WSL2 Virtual Machine.








## Build from Source

### OKIT Repository
Before the building either the Docker or Vagrant Images the project will need to be cloned, or downloaded, from the GitHub 
Repository.  

#### Clone
The command shows how this can be cloned to the local machine.

```bash
git clone -c core.autocrlf=input git@github.com:oracle/oci-designer-toolkit.git
```

or 

```bash
git clone -c core.autocrlf=input https://github.com/oracle/oci-designer-toolkit.git
```

#### Update
If you have previously cloned the GitHub Repository you can update to the latest release by pulling it from the repository 
with the following command.

```bash
cd oci-designer-toolkit
git pull
```

#### Download
If you do not have git installed locally the current release of OKIT can be retrieved by downloading it as a zip file from
[https://github.com/oracle/oci-designer-toolkit/archive/master.zip](https://github.com/oracle/oci-designer-toolkit/archive/master.zip)


### Create Container

#### Copy Config & Key Files
Before building/rebuilding your chosen container you will need to copy the contents of [&lt;USER HOME DIR&gt;/.oci](#config-file) 
to the __oci-designer-toolkit/containers/oci__ directory.

#### Create Git Repository Properties File & Copy SSH Keys
If you decide to use Git as a repository for your templates you will need to create the Git Repository properties file
[__oci-designer-toolkit/containers/oci/git_repositories__](#git-repositories-file). Once this has been done the contents of
__&lt;USER HOME DIR&gt;/.ssh__ will need to be copied to __oci-designer-toolkit/containers/ssh__



#### Docker Compose
The docker image is the recommended runtime server OKIT provides a simple Docker Compose script to build and start the container.

##### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop).
- Create local directory __~/okit/user/templates__ for storage of custom templates.
- [Copy Config & Key Files](#copy-config--key-files)

##### Docker Compose Build
```bash
cd oci-designer-toolkit/containers/docker
docker-compose up --detach
```

##### Docker Compose Update
```bash
cd oci-designer-toolkit/containers/docker
docker-compose stop
docker-compose build
```

#### Docker 











## Install on OCI Instance
```diff
- THIS IS NOT RECOMMENDED BUT THESE NOTES ARE FOR THOSE WHO INSIST ON TRYING THIS
- THE FOLLOWING WILL SHOW HOW TO CONFIGURE OKIT WITH INSTANCE PRINCIPAL FUNCTIONALITY.
-
- IF YOU INSTALL OKIT WITH PUBLIC ACCESS THEN THE INSTANCE WILL POTENTIALLY HAVE COMPLETE ACCESS
- TO YOUR TENANCY ALLOWING FOR INTERROGATION AND CREATION OF OCI RESOURCES.
```
To install OKIT and run it within an OCI instance you will need to configure [Instance Principal](https://docs.cloud.oracle.com/en-us/iaas/Content/Identity/Tasks/callingservicesfrominstances.htm)
functionality within your Tenancy to allow the OKIT Instance to access OCI API and Query the Tenancy / Access Resource Manager.

When creating the Instance it is recommended the Instance is within its own Virtual Cloud Network / Subnet. The Subnet should 
be secured with a Security List that __only__ allows TCP/22 and TCP/443 port access to the Instance to allow the configuration of a [SSH Tunnel](#ssh-tunnel)
to restrict access to the Instance to authorised users or https authenticated using the OCI console login. 

Once the Instance has been created the following commands will install OKIT and create the service to run the WebServer.
```bash
# Install Required Packages 
sudo bash -c "yum install -y git"
sudo bash -c "yum install -y openssl"
sudo bash -c "yum install -y oci-utils"
# This is not required for OL8
sudo bash -c "yum install -y python-oci-cli"
# Update
sudo bash -c "yum update -y"
# Install Required Python Modules
sudo bash -c "python3 -m pip install -U pip"
sudo bash -c "python3 -m pip install -U setuptools"
sudo bash -c "python3 -m pip install --no-cache-dir authlib flask gitpython git-url-parse gunicorn oci openpyxl pandas python-magic pyyaml requests xlsxwriter"
# Clone OKIT
sudo bash -c "mkdir -p /github"
sudo bash -c "git clone -b master https://github.com/oracle/oci-designer-toolkit.git /github/oci-designer-toolkit"
sudo bash -c "mkdir -p /okit/{git,local,log,instance/git,instance/local,instance/templates/user,workspace,ssl}"
# Link Directories
sudo bash -c "ln -sv /github/oci-designer-toolkit/config /okit/config"
sudo bash -c "ln -sv /github/oci-designer-toolkit/okitweb /okit/okitweb"
sudo bash -c "ln -sv /github/oci-designer-toolkit/visualiser /okit/visualiser"
sudo bash -c "ln -sv /github/oci-designer-toolkit/okitweb/static/okit/templates/reference_architecture /okit/instance/templates/reference_architecture"
# Copy Config
sudo bash -c "cp -v /github/oci-designer-toolkit/instance/config.py /okit/instance"
# Add additional environment information 
sudo bash -c "echo 'export PATH=$PATH:/usr/local/bin' >> /etc/bashrc"
sudo bash -c "echo 'export PYTHONPATH=:/okit/visualiser:/okit/okitweb:/okit' >> /etc/bashrc"
sudo bash -c "echo 'export OCI_CLI_AUTH=instance_principal' >> /etc/bashrc"
sudo bash -c "echo 'export OKIT_VM_COMPARTMENT=`oci-metadata -g compartmentID --value-only`' >> /etc/bashrc"
sudo bash -c "echo 'export OKIT_VM_REGION=`oci-metadata -g region --value-only`' >> /etc/bashrc"
# Generate ssl Self Sign Key
sudo bash -c "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /okit/ssl/okit.key -out /okit/ssl/okit.crt -subj '/C=GB/ST=Berkshire/L=Reading/O=Oracle/OU=OKIT/CN=www.oci_okit.com'"
# Copy GUnicorn Service File
# sudo bash -c 'sed "s/{COMPARTMENT_OCID}/`oci-metadata -g compartmentID --value-only`/" /okit/containers/services/gunicorn.oci.service > /etc/systemd/system/gunicorn.service'
sudo bash -c 'sed "s/{COMPARTMENT_OCID}/`oci-metadata -g compartmentID --value-only`/" /github/oci-designer-toolkit/containers/services/gunicorn.oci.service > /etc/systemd/system/gunicorn.service'
sudo bash -c 'sed -i "s/{REGION_IDENTIFIER}/`oci-metadata -g region --value-only`/" /etc/systemd/system/gunicorn.service'
sudo bash -c 'sed -i "s/<home_region>/`oci-metadata -g region --value-only`/" /okit/instance/config.py'
#####################################################################################
### Edit /okit/instance/config.py as described in OKIT Configuration File section ###
#####################################################################################
# Enable Gunicorn Service
sudo systemctl enable gunicorn.service
sudo systemctl start gunicorn.service
# Open Firewall
sudo firewall-offline-cmd  --add-port=443/tcp
sudo systemctl restart firewalld
```

### OpenID Connect Configuration for IDCS

To use OpenID Connect with IDCS two configurations are required.

#### Setup of IDCS
Ask your administrator to update the primary (default) IDCS instance of your tenancy. This instance is often labled as OracleIdentityCloudService in the OCI Console login screen drop down.

In the steps we use <server_base_url>. The format is protocol://fully.qualified.host.name.

Configuration steps:
1. Select Identity -> Federation from the OCI Console Hamburger Menu. ![Identity Federation](images/Identity_Federation.png?raw=true "Identity Federation")
1. From the Cloud Provider Select the "Oracle Identity Cloud Service Console" url. ![Cloud Provider](images/Identity_Cloud_Provider.png?raw=true "Cloud Provider")
1. Log into IDCS admin console (e.g. https://idcs-aabbccddee6677889900ddhhaa.identity.oraclecloud.com/ui/v1/adminconsole)
1. From the hamburger menu on the upper left, select Applications.
1. Click 'Add' ![Identity Application](images/Identity_Application.png?raw=true "Identity Application")
1. In the 'Add Application' window select 'Confidential Application'![Confidential Application](images/Identity_Confidential_App.png?raw=true "Confidential Application")
    1. In 'App Details' enter
        1. A unique 'Name'
        1. For 'Custom Logout URL' enter <server_base_url>/okit/postlogout
        1. Click 'Next'
1. In the Client step select 'Configure this application as a client now'
    1. In the Authorization section:
        1. Select the 'Grant Types': Client Credentials, JWT Assertion, Refresh Token, and Authorization Code
        1. Set the 'Redirect URL' to <server_base_url>/okit/postlogin
        1. Set the 'Logout URL' to <server_base_url>/okit/logout
        1. Set the 'Post Logout URL' to <server_base_url>/okit/postlogout
1. Click 'Next' until the 'Finish' button can be selected.
1. Click 'Finish'
1. An 'Application Added' window shows the values for Client ID and Client Secret. Copy both values for later use. Click on 'Close' to close the window.
1. Click 'Activate' to enable the configuration.
1. From the hamburger menu on the upper left, select Settings.
1. Click 'Default' ![Identity Application](images/Idcs_Defaults.png?raw=true "Identity Application")
1. Turn on "Access Signing Certificate"

#### OKIT Configuration File

OKIT has one configuration file that must be updated. It requires these values:
* home_region - Get this value from your Oracle Cloud Infrastructure admin
* tenant_name - Get this value from your Oracle Cloud Infrastructure admin
* client_id - Get this value from the IDCS Confidential Application configuration (see above)
* client_secret - Get this value from the IDCS Confidential Application configuration (see above)
* idcs_instance_id - The IDCS instance id is part of the IDCS URL, e.g., the URL is https://idcs-aabbccddee6677889900ddhhaa.identity.oraclecloud.com and the value is aabbccddee6677889900ddhhaa
* server_base_url - The OKIT fully qualified server base URL. The value you used during the IDCS configuration. The format is protocol://fully.qualified.host.name.

The OKIT configuration file is located in the directory 'instance'.
* config.py - Replace the values for <idcs_instance_id>, <client_id>, <client_secrect>, and <server_base_url> with the respective values.

### Dynamic Group
A Tenancy level Dynamic Group will need to be created to enable Instance Principal access for the instance.
#### OKITInstanceGroup
Create the OKITInstanceGroup Dynamic Group and add a single Rule relating to the OKIT Instance.
![OKIT Dynamic Group](images/DynamicGroup.png?raw=true "OKIT Dynamic Group")

### Policies
Tenancy level policies will need to be created for the Dynamic Group and depending on the required level of access either
the Query or Resource Manager level policies defined below should be specified.
#### Query
```text
Allow dynamic-group OKITInstanceGroup to read all-resources in tenancy
Allow dynamic-group OKITInstanceGroup to use instances in tenancy
```
#### Resource Manager
```text
Allow dynamic-group OKITInstanceGroup to manage orm-stacks in tenancy
Allow dynamic-group OKITInstanceGroup to manage orm-jobs in tenancy
Allow dynamic-group OKITInstanceGroup to manage all-resources in tenancy
```
#### OKITInstancePrincipal
Create the OKITInstancePrincipal Policy and add either the Query or Resource Manager Policies.
![OKIT Dynamic Group Policies](images/DynamicGroupPolicies.png?raw=true "OKIT Dynamic Group Policies")

### SSH Tunnel
```bash
ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -N -L 8080:127.0.0.1:80 opc@<Instance IP> -i <Private Key File>
```

Once the tunnel has been created the OKIT Designer BUI can be accessed on [http://localhost:8080/okit/designer](http://localhost:8080/okit/designer).


