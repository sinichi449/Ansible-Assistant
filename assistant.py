#!/usr/bin/env python
# coding: utf-8

# In[6]:


import grpc
import logging
import json
import concurrent.futures

from tenacity import (
    retry, 
    stop_after_attempt, 
    retry_if_exception
)
from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)
from utils import (
    assistant_helpers,
    audio_helpers,
    browser_helpers,
    device_helpers
)


# In[7]:


END_OF_UTTERANCE = embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.DialogStateOut.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.DialogStateOut.CLOSE_MICROPHONE
PLAYING = embedded_assistant_pb2.ScreenOutConfig.PLAYING

class VoiceInput(object):
    def __init__(
        self,
        device_model_id,
        device_id,
        conversation_stream,
        display,
        channel,
        device_handler,
        language_code='en-US'
    ):
        self.device_model_id = device_model_id
        self.device_id = device_id
        self.conversation_stream = conversation_stream
        self.display = display
        self.channel = channel
        self.device_handler = device_handler
        self.language_code = language_code

        self.is_new_conversation = False
        self.conversation_state = None
        self.text_response = ''
        self.deadline = 60 * 3 + 5
        
        assistant_stub = embedded_assistant_pb2_grpc.EmbeddedAssistantStub
        self.assistant = assistant_stub(channel)

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False
        self.conversation_stream.close()

    def is_grpc_error_unavailable(e):
        is_grpc_error = isinstance(e, grpc.RpcError)
        is_status_unavailable = grpc.StatusCode.UNAVAILABLE
        if is_grpc_error and e.code() == is_status_unavailable:
            logging.error('grpc unavalilable error: %s', e)
            return True
        return False
    
    def generate_assist_requests(self):
        audio_in_config = embedded_assistant_pb2.AudioInConfig(
            encoding='LINEAR16',
            sample_rate_hertz=self.conversation_stream.sample_rate
        )
        audio_out_config = embedded_assistant_pb2.AudioOutConfig(
            encoding='LINEAR16',
            sample_rate_hertz=self.conversation_stream.sample_rate,
            volume_percentage=self.conversation_stream.volume_percentage
        )
        dialog_state_in = embedded_assistant_pb2.DialogStateIn(
            language_code=self.language_code,
            conversation_state=self.conversation_state
        )
        device_config = embedded_assistant_pb2.DeviceConfig(
            device_id=self.device_id,
            device_model_id=self.device_model_id
        )
        
        config = embedded_assistant_pb2.AssistConfig(
            audio_in_config=audio_in_config,
            audio_out_config=audio_out_config,
            dialog_state_in=dialog_state_in,
            device_config=device_config
        )
        if self.display:
            config.screen_out_config.screen_mode = PLAYING
            
        self.is_new_conversation = False
        
        assist_request = embedded_assistant_pb2.AssistRequest
        yield assist_request(config=config)
        # Send voice data
        for data in self.conversation_stream:
            yield assist_request(audio_in=data)
    
    @retry(reraise=True, 
           stop=stop_after_attempt(3),
          retry=retry_if_exception(is_grpc_error_unavailable))
    def assist(self):
        continue_conversation = False
        device_actions_futures = []
        
        self.conversation_stream.start_recording()
        print('Now Recording...')
        
        def iter_log_assist_requests():
            for c in self.generate_assist_requests():
                assistant_helpers.log_assist_request_without_audio(c)
                yield c
            
        logging.debug('Reached end of AssistRequest iteration.')
        for resp in self.assistant.Assist(iter_log_assist_requests(), self.deadline):
            assistant_helpers.log_assist_response_without_audio(resp)
            
            if resp.event_type == END_OF_UTTERANCE:
                print('Recording ended.')
            if resp.speech_results:
                print('Transcript of user request: ', ' '.join(r.transcript for r in resp.speech_results))
            if len(resp.audio_out.audio_data) > 0:
                if not self.conversation_stream.playing:
                    self.conversation_stream.stop_recording()
                    self.conversation_stream.start_playback()
                    logging.info('Playing assistant response.')
                self.conversation_stream.write(resp.audio_out.audio_data)
            if resp.dialog_state_out.volume_percentage != 0:
                volume_percentage = resp.dialog_state_out.volume_percentage
                logging.info('Setting volume to %s%%', volume_percentage)
                self.conversation_stream.volume_percentage = volume_percentage
            if resp.dialog_state_out.microphone_mode == DIALOG_FOLLOW_ON:
                continue_conversation = True
                logging.info('Expecting follow-on query from user.')
            elif resp.dialog_state_out.microphone_mode == CLOSE_MICROPHONE:
                continue_conversation = False
            if resp.device_action.device_request_json:
                device_request = json.loads(resp.device_action.device_request_json)
                fs = self.device_handler(device_request)
                if fs:
                    device_actions_futures.extend(fs)
            if self.display and resp.screen_out.data:
                system_browser = browser_helpers.system_browser
                system_browser.display(resp.screen_out.data)
            if resp.dialog_state_out.supplemental_display_text:
                self.text_response = resp.dialog_state_out.supplemental_display_text
        
        if len(device_actions_futures):
            logging.info('Waiting for device executions to complete.')
            concurrent.futures.wait(device_actions_futures)

        logging.info('Finished playing assistant response.')
        self.conversation_stream.stop_playback()
        return continue_conversation

