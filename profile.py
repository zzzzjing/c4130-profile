# -*- coding: utf-8 -*-
# CloudLab Profile for c4130 Node with Tesla V100 GPUs
# Ubuntu 22.04 + NVIDIA Driver + (optional) CUDA 11.7

import geni.portal as portal
import geni.rspec.pg as pg

# Create a Context and RSpec request
pc = portal.Context()
request = pc.makeRequestRSpec()

# Request a single c4130 node
node = request.RawPC("node")
node.hardware_type = "c4130"
# Replace with the actual Ubuntu 22.04 image URN available in your CloudLab site
node.disk_image = "urn:publicid:IDN+your-site+image+UBUNTU22-64-STD"
# Enable routable control IP if SSH over public address is needed; otherwise comment out
node.routable_control_ip = "true"

# 1. System update and install ubuntu-drivers-common
node.addService(pg.Execute(shell="sh", command="sudo apt-get update -y"))
node.addService(pg.Execute(shell="sh", command="sudo apt-get install -y ubuntu-drivers-common"))

# 2. Auto-install NVIDIA driver
node.addService(pg.Execute(shell="sh", command="sudo ubuntu-drivers autoinstall"))

# 3. Log GPU status
node.addService(pg.Execute(
    shell="sh",
    command="nvidia-smi > ~/gpu_info.log 2>&1 || echo 'nvidia-smi failed' >> ~/gpu_info.log"
))

# 4. Optional: Install CUDA 11.7
#    Uncomment this block only if CUDA is needed and network/permissions allow.
node.addService(pg.Execute(shell="sh", command="""
CUDA_VER="11.7"
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin -O /tmp/cuda.pin
sudo mv /tmp/cuda.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/7fa2af80.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"
sudo apt-get update -y
sudo apt-get install -y cuda-toolkit-${CUDA_VER}
sudo ln -s /usr/local/cuda-${CUDA_VER} /usr/local/cuda || true
if command -v nvcc &> /dev/null; then
    nvcc --version >> ~/gpu_info.log 2>&1
else
    echo "nvcc not installed or not in PATH" >> ~/gpu_info.log
fi
"""))

# 5. Set CUDA environment variables if CUDA installed
node.addService(pg.Execute(shell="sh", command="""
echo 'export PATH=/usr/local/cuda-11.7/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.7/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
"""))

# 6. Optional: Install NVIDIA Container Toolkit for GPU containers
node.addService(pg.Execute(shell="sh", command="""
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
sudo apt-get update -y
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker || echo "docker restart failed" >> ~/gpu_info.log
"""))

# 7. Completion message
node.addService(pg.Execute(shell="sh", command="echo 'c4130 driver and CUDA setup complete' >> ~/setup_driver.log"))

# Output the RSpec
pc.printRequestRSpec(request)
