#### Local AI Voice Chat
A POC of an llm powered voice chat system. [Docker](https://www.docker.com/), [ollama](https://ollama.com/), [ElevenLabs](https://elevenlabs.io/), and [pydantic_ai](https://ai.pydantic.dev/)

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
2. Navigate to project root directory and run ```bash run.sh```
3. Access the application by navigating to [127.0.0.1:7860](http://127.0.0.1:7860)

#### Stop steps
1. Navigate to project root directory and run ```ctl + c```
2. Run ```docker-compose down --volumes``` to turn off containers and delete volumes

#### Key Project Config
- [Ollama model](https://ollama.com/search): The model used in ollama is set in the ```run.sh``` file under the ```MODEL_NAME``` environment variable
- System prompt: The system prompt can be configured in the ```run.sh``` file under the ```SYSTEM_PROMPT``` environment variable
- GPU: To enable gpu usage, uncomment the ```devices``` section in the ```docker-compose.yaml```

#### Resources
- Docker daemon start [guide](https://docs.docker.com/config/daemon/start/)

#### Troubleshooting
###### Windows operating system
- [Install Windows Subsystem for Linux(wsl)](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Enable virtualization on windows](https://learn.microsoft.com/en-us/windows/wsl/troubleshooting#error-0x80370102-the-virtual-machine-could-not-be-started-because-a-required-feature-is-not-installed)
- Make sure to use [Git Bash](https://git-scm.com/downloads) when running on a windows system

###### Mac operating system
- [Change docker desktop settings on mac](https://docs.docker.com/desktop/settings/mac/#namespaces)
- [Docker file sharing](https://docs.docker.com/desktop/settings/mac/?uuid=51156F3F-7CDF-494C-B5D6-B96B2060A073#file-sharing)
