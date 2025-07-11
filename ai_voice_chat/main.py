import os
from fastrtc import (
    ReplyOnPause,
    Stream,
    AdditionalOutputs,
    get_stt_model, get_tts_model,
    KokoroTTSOptions
)
from modules import OllamaWrapper, Logger
from ollama import Client
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from numpy.typing import NDArray
from multiprocessing import Process

import numpy as np
import time

ollama_endpoint = str(os.getenv("OLLAMA_ENDPOINT"))
model_name = str(os.getenv("MODEL_NAME")) # model selected must support tools
system_prompt = str(os.getenv("SYSTEM_PROMPT"))

logger = Logger(name='main').get_logger()
ollama_wrapper = OllamaWrapper(ollama_endpoint=ollama_endpoint, client=Client, logger=Logger)
ollama_model = OpenAIModel(model_name=model_name, provider=OpenAIProvider(base_url=f'{ollama_endpoint}/v1', api_key='fake-api-key')) # api_key is needed even when running locally
agent = Agent(ollama_model, system_prompt=system_prompt)

# Text To Speech (TTS)
tts_client = get_tts_model(model="kokoro")
# Speech To Text (STT)
stt_model = get_stt_model(model="moonshine/base")

GENERATING_RESPONSE = False
 
options = KokoroTTSOptions(
    voice="af_heart",
    speed=1.0,
    lang="en-us"
)

def configure_services():
    '''configure services'''
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

def call_llm(message: str = ''):
    try:
        logger.info('calling llm')
        result = agent.run_sync(message)
        return result
    
    except Exception as e:
        logger.error('unable to call llm: \n %s', e)

def generate_response(
    audio: tuple[int, NDArray[np.int16 | np.float32]],
    chatbot: list[dict] | None = None
):
    '''generate a response from llm'''
    try:
        logger.info('generating response')

        chatbot = chatbot or []
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in chatbot]

        start = time.time()

        # Use local STT model
        text = stt_model.stt(audio)

        if len(text) < 1:
            yield "no prompt provided"
            return

        logger.info(f"transcription time: {time.time() - start}\n", )
        logger.info(f"prompt: {text} \n")

        chatbot.append({"role": "user", "content": text})

        yield AdditionalOutputs(chatbot)

        messages.append({"role": "user", "content": text})
        logger.info('calling llm with: %s \n', str(messages))

        response_text = call_llm(str(messages))

        if response_text != None:
            chatbot.append({"role": "assistant", "content": response_text.output})
            yield response_text.output
        else:
            chatbot.append({"role": "assistant", "content": "no response generated"})
            yield "no response generated"

        logger.info('response generated successfully')

    except Exception as e:
        yield "unable to generate a response"
        logger.error('unable to generate response: \n %s', e)

def response(
    audio: tuple[int, NDArray[np.int16 | np.float32]],
    chatbot: list[dict] | None = None,
    tts_options: KokoroTTSOptions | None = None, generating_response = GENERATING_RESPONSE
):
    '''respond to user'''
    try:
        logger.info('responding via voice')
        # Use tts_client.stream_tts_sync for TTS (Local TTS)
        # Pass tts_options if provided, else use default options
        tts_options = KokoroTTSOptions(
            voice="bf_alice",
            speed=1.0,
            lang="en-us"
        )

        if generating_response == False:
            generating_response = True
            gen = generate_response(audio=audio, chatbot=chatbot)

            # First yield is AdditionalOutputs with updated chatbot
            chatbot = next(gen)

            # Second yield is the response text
            response_text = next(gen)

            logger.info(f"response: {response_text}")

            for chunk in tts_client.stream_tts_sync(
                response_text, options=tts_options or options
            ):
                yield chunk
            
            generating_response = False

        else:
            for chunk in tts_client.stream_tts_sync(
                "still working on the previous request", options=tts_options or options
            ):
                yield chunk
        
        logger.info('responding successful')

    except Exception as e:
        logger.error('unable to respond: \n %s', e)


if __name__ == "__main__":
    try:
        logger.info('starting main program')

        stream = Stream(
            handler=ReplyOnPause(response, input_sample_rate=16000),
            modality="audio",
            mode="send-receive",
            ui_args={
                "title": "AI Motivational Speaker ⚡️",
                "inputs": [
                    {"name": "voice", "type": "dropdown", "choices": [
                        "af_heart", "af_sun", "af_moon"], "label": "Voice", "value": "af_heart"},
                    {"name": "speed", "type": "slider", "min": 0.5, "max": 2.0,
                        "step": 0.1, "label": "Speed", "value": 1.0},
                    {"name": "lang", "type": "dropdown", "choices": [
                        "en-us", "en-uk"], "label": "Language", "value": "en-us"},
                ]
            },
        )

        stream.ui.launch()

    except Exception as e:
        logger.error('unable to start main program: \n %s', e)