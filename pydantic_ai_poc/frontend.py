import os
from modules import OllamaWrapper, Logger
from ollama import Client
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel

ollama_endpoint = str(os.getenv("OLLAMA_ENDPOINT"))
model_name = str(os.getenv("MODEL_NAME")) # model selected must support tools
system_prompt = str(os.getenv("SYSTEM_PROMPT"))

logger = Logger(name='frontend').get_logger()
ollama_wrapper = OllamaWrapper(ollama_endpoint=ollama_endpoint, client=Client, logger=Logger)
ollama_model = OpenAIModel(model_name=model_name, provider=OpenAIProvider(base_url=f'{ollama_endpoint}/v1', api_key='fake-api-key')) # api_key is needed even when running locally

class GenericResponse(BaseModel):
    message: str

def configure_services():
    '''
        configure services
    '''
    logger.info('configuring services')
    try:
        if not model_name:
            raise Exception('no model name was found')

        if not ollama_wrapper.pull_model(model_name):
            raise Exception(f'unable to pull model: {model_name}')

        logger.info('services are properly configured')

    except Exception as e:  
        logger.error('unable to configure services: \n %s', e)

configure_services()

agent = Agent(ollama_model, result_type=GenericResponse, system_prompt=system_prompt)

def main():
    try:
        while True:
            user_input = input("Enter something (type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                logger.info("Exiting the program.")
                break
            result = agent.run_sync(user_input)
            logger.info(result.data)

    except Exception as e:
        logger.error('error generating response: %s', e)

if __name__ == "__main__":
    main()