#### Local AI Voice Chat
A completely local AI chat bot power by large language models. [Docker](https://www.docker.com/), [ollama](https://ollama.com/), and [FastRTC](https://fastrtc.org/) are the major components of this project. 

#### Requirements
- [Docker](https://www.docker.com/products/docker-desktop/)

#### Project Structure
- modules
    - '__init\__.py': Outline python module exports
    - 'logger.py': Custom logger implementation
    - 'ollamawrapper.py': Custom ollama API Wrapper
- '.gitignore': Outline files for git to ignore
- 'docker-compose.yaml': Docker compose config
- 'dockerfile': Application docker config
- 'main.py': Application python file
- 'README.md': ReadMe file
- 'requirements.txt': Outline application dependencies
- 'run.sh': Bash script to start the application

#### Start steps
1. Start the docker daemon 
2. Navigate to project root directory using a bash terminal and run ```bash run.sh```
3. Once docker logs include "chat-1  | * Running on local URL:  http://0.0.0.0:7860", access the application by navigating to [127.0.0.1:7860](http://127.0.0.1:7860)

#### Stop steps
1. Navigate to bash terminal currently running the project and run ```ctl + c```
2. Run ```docker-compose down --volumes``` to turn off containers and delete volumes

#### Key Project Config in [Docker Compose File](./docker-compose.yaml)
- [Ollama model](https://ollama.com/search): The model used in ollama is set under the ```MODEL_NAME``` environment variable
- System prompt: The system prompt can be configured under the ```SYSTEM_PROMPT``` environment variable
- GPU: To enable gpu usage, uncomment the ```devices``` section in the ```docker-compose.yaml```

#### Resources
- Docker daemon start [guide](https://docs.docker.com/config/daemon/start/)
- Nvidia Cuda [download](https://developer.nvidia.com/cuda-downloads)

#### Troubleshooting
###### Windows operating system
- [Install Windows Subsystem for Linux(wsl)](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Enable virtualization on windows](https://learn.microsoft.com/en-us/windows/wsl/troubleshooting#error-0x80370102-the-virtual-machine-could-not-be-started-because-a-required-feature-is-not-installed)
- Make sure to use [Git Bash](https://git-scm.com/downloads) when running on a windows system

###### Mac operating system
- [Change docker desktop settings on mac](https://docs.docker.com/desktop/settings/mac/#namespaces)
- [Docker file sharing](https://docs.docker.com/desktop/settings/mac/?uuid=51156F3F-7CDF-494C-B5D6-B96B2060A073#file-sharing)
