from typing import Type
from ollama import Client
from .logger import Logger
import time
import concurrent.futures

class OllamaWrapper:
    def __init__(self, ollama_endpoint: str, client: Type[Client], logger: Type[Logger]) -> None:
        '''
            This class assumes a running ollama server that follows the standard ollama api documentation: https://github.com/ollama/ollama/blob/main/docs/api.md
        '''
        self.ollama_endpoint: str = ollama_endpoint
        self.client: Client = client(host=ollama_endpoint)
        self.logger = logger(name='ollama_wrapper').get_logger()
        self.logger.info('initializing ollama client')

    def list_models(self) -> list[str]:
        '''
            Lists all downloaded models
        '''
        try:
            output: list[str] = []
            data = self.client.list()
            for model in data.models:
                output.append(model['model'])
            self.logger.info('listed running models')
            return output
        
        except Exception as e:
            self.logger.error('error listing running models \n %s ', e)
            return []

    def is_active_model(self, model_name: str) -> bool:
        '''
            Check if model is active
        '''
        self.logger.info('checking active model')
        return model_name in self.list_models()
        
    def pull_model(self, model_name: str) -> bool:
        '''
            Pulls model from ollama
        '''
        try:
            if model_name in self.list_models():
                self.logger.info('model %s already downloaded', model_name)
                return True
            
            pulling_model = self.client.pull(model_name, stream=True)
            self.logger.info('pulling model... \n %s', model_name)
            start_time = time.time()
            self.logger.info(next(pulling_model))
            while True:
                current_time = time.time()
                next_digest = next(pulling_model)
                if  next_digest['status'] == 'success':
                    self.logger.info('pulled model %s', model_name)
                    break  
                elif next_digest['status'] == 'error':
                    raise Exception('errored out while pulling model')
                elif current_time - start_time >= 600:
                    raise Exception('timeout of 10 minutes reached while pulling model')
            
            return True

        except Exception as e:
            self.logger.error('error pulling model %s \n %s', model_name, e)
            return False
        
    def delete_model(self, model_name: str) -> bool:
        '''
            Deletes a downloaded model
        '''
        try:
            if model_name not in self.list_models():
                self.logger.info('model %s not downloaded', model_name)
                return False
            
            delete_model_status  = self.client.delete(model_name)
            
            while delete_model_status.status != None and delete_model_status.status != 'completed':
                self.logger.info('deleting model: %s', model_name)
            return True

        except Exception as e:
            self.logger.error('error deleting model %s \n %s', model_name, e)
            return False
        
    def generate_embedding(self, model_name: str, input_list: list[str]) -> list[float]:
        '''
            Generates an embedding with a downloaded model
        '''
        try:
            if model_name not in self.list_models():
                self.logger.info('model %s not downloaded', model_name)
                return []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                embeddings_future = executor.submit(self.client.embed, model_name, input_list)
                embeddings = embeddings_future.result()
                self.logger.info('generated embedding with model %s', model_name)
                return embeddings['embeddings']

        except Exception as e:
            self.logger.error('error generating embedding for model %s \n %s', model_name, e)
            return []
        
    def generate_completion(self, model_name: str, prompt: str) -> str:
        '''
            Generates completion with downloaded model
        '''
        try:
            if model_name not in self.list_models():
                self.logger.info('model %s not downloaded', model_name)
                return ''

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                response_future = executor.submit(self.client.generate, model_name, prompt)
                response = response_future.result()
                self.logger.info('generated completion with model %s \n %s', model_name, response)
                return response.response
        
        except Exception as e:
            self.logger.error('error generating completion for model %s \n %s', model_name, e)
            return ''

    def configure_system(self, model_name: str, system_prompt: str) -> str:
        '''
            Set system prompt for downloaded model
        '''
        try:
            if model_name not in self.list_models():
                self.logger.info('model %s not downloaded', model_name)
                return ''

            response = self.client.generate(model=model_name, system=system_prompt)

            self.logger.info('configured system prompt for model %s', model_name)
            return response.response
        
        except Exception as e:
            self.logger.error('error configuring system for model %s \n %s', model_name, e)
            return ''