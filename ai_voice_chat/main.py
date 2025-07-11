import os
import asyncio
from fastrtc import (
    ReplyOnPause,
    Stream,
    AdditionalOutputs,
    get_stt_model, get_tts_model,
    KokoroTTSOptions
)
from modules import OllamaWrapper, Logger
from ollama import Client
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
import time
from concurrent.futures import ThreadPoolExecutor

# --- CONFIG ---
OLLAMA_ENDPOINT = str(os.getenv("OLLAMA_ENDPOINT"))
MODEL_NAME = str(os.getenv("MODEL_NAME"))
SYSTEM_PROMPT = str(os.getenv("SYSTEM_PROMPT"))

logger = Logger(name='main').get_logger()
ollama_wrapper = OllamaWrapper(ollama_endpoint=OLLAMA_ENDPOINT, client=Client, logger=Logger)
ollama_model = OpenAIModel(model_name=MODEL_NAME, provider=OpenAIProvider(base_url=f'{OLLAMA_ENDPOINT}/v1', api_key='fake-api-key'))

tts_client = get_tts_model(model="kokoro")
stt_model = get_stt_model(model="moonshine/base")

executor = ThreadPoolExecutor(max_workers=4)  # For blocking IO

tts_options_default = KokoroTTSOptions(voice="af_heart", speed=1.0, lang="en-us")

def configure_services():
    '''
        Configure ollama
    '''
    logger.info('configuring services')
    try:
        if not MODEL_NAME:
            raise Exception('no model name was found')
        if not ollama_wrapper.pull_model(MODEL_NAME):
            raise Exception(f'unable to pull model: {MODEL_NAME}')
        logger.info('services are properly configured')
    except Exception as e:
        logger.error('unable to configure services: \n %s', e)

configure_services()

async def async_stt(audio):
    '''
        Async speech to text
    '''
    try:
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(executor, stt_model.stt, audio)
        return text
    except Exception as e:
        logger.error(f"STT error: {e}")
        return ""

async def async_tts_stream(text, options):
    '''
        Generate and send text to speech in async stream
    '''
    try:
        loop = asyncio.get_event_loop()
        for chunk in await loop.run_in_executor(executor, lambda: list(tts_client.stream_tts_sync(text, options=options))):
            yield chunk
    except Exception as e:
        logger.error(f"TTS stream error: {e}")

async def async_tts_stream_chunks(chunk_generator, options):
    '''
        Given a text chunk generator (async), streams audio as chunks appear
    '''
    loop = asyncio.get_event_loop()
    try:
        async for chunk in chunk_generator:
            try:
                for audio_chunk in await loop.run_in_executor(
                    executor,
                    lambda: list(tts_client.stream_tts_sync(chunk, options=options))
                ):
                    yield audio_chunk
            except Exception as tts_e:
                logger.error(f"TTS error on chunk: {tts_e}")
    except Exception as e:
        logger.error(f"TTS stream chunks error: {e}")

async def generate_response(audio, chatbot=None):
    '''
        Async generator: handles STT, yields new chatbot state, then streams LLM tokens
    '''
    try:
        chatbot = chatbot or []
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in chatbot]

        start = time.time()
        text = await async_stt(audio)
        if not text:
            yield "no prompt provided"
            return

        logger.info(f"transcription time: {time.time() - start}")
        logger.info(f"prompt: {text}")

        chatbot.append({"role": "user", "content": text})
        yield AdditionalOutputs(chatbot)
        messages.append({"role": "user", "content": text})

        logger.info('calling llm with: %s', str(messages))
        try:
            llm_stream = ollama_wrapper.generate_completion_stream(MODEL_NAME, str(messages))
            yield llm_stream  # yield async generator for downstream TTS streaming
        except Exception as llm_e:
            logger.error(f"LLM streaming error: {llm_e}")
            yield None
    except Exception as e:
        logger.error(f"Error in generate_response: {e}")
        yield "unable to generate a response"

async def response(
    audio,
    chatbot=None,
    tts_options=None,
    generating_response=False
):
    '''
        Generate response to provided speech
    '''
    try:
        chatbot = chatbot or []
        tts_options = tts_options or tts_options_default

        if not generating_response:
            generating_response = True
            gen = generate_response(audio=audio, chatbot=chatbot)
            # First yield is chatbot update
            try:
                chatbot_update = await gen.__anext__()
            except Exception as e:
                logger.error(f"Error yielding chatbot update: {e}")
                return

            # Second yield is the LLM stream generator
            try:
                llm_stream = await gen.__anext__()
                if llm_stream is None:
                    logger.warning("No LLM stream, sending fallback message.")
                    async for chunk in async_tts_stream("No response generated", tts_options):
                        yield chunk
                    return
            except Exception as e:
                logger.error(f"Error yielding LLM stream: {e}")
                return

            logger.info(f"received LLM stream, streaming TTS")
            # Stream LLM chunks to TTS and yield audio
            try:
                async for audio_chunk in async_tts_stream_chunks(llm_stream, tts_options):
                    yield audio_chunk
            except Exception as e:
                logger.error(f"Error streaming LLM/TTS chunks: {e}")
                async for chunk in async_tts_stream("Error during response synthesis", tts_options):
                    yield chunk

            generating_response = False
        else:
            try:
                async for chunk in async_tts_stream("still working on the previous request", tts_options):
                    yield chunk
            except Exception as e:
                logger.error(f"Error in fallback TTS: {e}")

        logger.info('responding successful')
    except Exception as e:
        logger.error(f"General error in response handler: {e}")

def run():
    '''
        Handle main program
    '''
    logger.info('starting main program')

    def sync_response(audio, chatbot=None, tts_options=None, generating_response=False):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            gen = response(audio, chatbot, tts_options, generating_response)
            while True:
                try:
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        except Exception as e:
            logger.error(f"Critical sync_response error: {e}")
            return

    try:
        stream = Stream(
            handler=ReplyOnPause(sync_response, input_sample_rate=16000),
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
        logger.error(f"Fatal error starting Stream UI: {e}")

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.error('unable to start main program: \n %s', e)
