# -*- coding: utf-8 -*-
# CloudLab Profile for c4130 Node with Tesla V100 GPUs
# Ubuntu 22.04 + NVIDIA Driver + (可选) CUDA 11.7



import geni.portal as portal
import geni.rspec.pg as pg

# 初始化 Request 对象
request = portal.context.makeRequestRSpec()

# Request 一个 c4130 节点
node = request.RawPC("node")
node.hardware_type = "c4130"
# 修改为你所在站点可用的 Ubuntu 22.04 镜像 URN
node.disk_image = "urn:publicid:IDN+your-site+image+UBUNTU22-64-STD"
node.exclusive = True
# 使控制网络可路由，便于 SSH 访问；如不需可注释以下行
node.routable_control_ip = "true"

# 1. 更新系统并安装 ubuntu-drivers 工具
node.addService(pg.Execute(shell="sh", command="sudo apt-get update -y"))
node.addService(pg.Execute(shell="sh", command="sudo apt-get install -y ubuntu-drivers-common"))

# 2. 自动安装推荐 NVIDIA 驱动
node.addService(pg.Execute(shell="sh", command="sudo ubuntu-drivers autoinstall"))

# 3. 记录驱动安装及 GPU 状态
node.addService(pg.Execute(shell="sh", command="nvidia-smi > ~/gpu_info.log 2>&1 || echo 'nvidia-smi 执行失败' >> ~/gpu_info.log"))

# 4. 可选：安装 CUDA 11.7（如需，取消下面命令注释；若镜像已预装或不需完整 CUDA，可注释此块）
node.addService(pg.Execute(shell="sh", command="""
CUDA_VER="11.7"
# 以下流程需在镜像或网络允许的情况下启用
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin -O /tmp/cuda.pin
sudo mv /tmp/cuda.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/7fa2af80.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"
sudo apt-get update -y
sudo apt-get install -y cuda-toolkit-${CUDA_VER}
# 建立符号链接（若需要）
sudo ln -s /usr/local/cuda-${CUDA_VER} /usr/local/cuda || true
# 验证 nvcc 并记录
if command -v nvcc &> /dev/null; then
    nvcc --version >> ~/gpu_info.log 2>&1
else
    echo "nvcc 未安装或不在 PATH 中" >> ~/gpu_info.log
fi
"""))

# 5. 设置 CUDA 环境变量到 .bashrc（如安装了 CUDA）
node.addService(pg.Execute(shell="sh", command="""
echo 'export PATH=/usr/local/cuda-11.7/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.7/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
"""))

# 6. 安装 NVIDIA Container Toolkit，以便后续运行 GPU 容器（如不需要可注释）
node.addService(pg.Execute(shell="sh", command="""
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
sudo apt-get update -y
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker || echo "docker 重启失败" >> ~/gpu_info.log
"""))

# 7. 完成标志
node.addService(pg.Execute(shell="sh", command="echo 'c4130 驱动和 CUDA 配置完成' >> ~/setup_driver.log"))

# 输出 RSpec
portal.context.printRequestRSpec(request)
