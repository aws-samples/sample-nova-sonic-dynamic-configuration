"""Multi-agent orchestrator for Nova 2 Sonic conversations."""
import asyncio
import logging
import os
import pygame

from src.session.conversation_state import ConversationState
from src.agents.tool_registry import ToolRegistry
from src.connection.bedrock_connection import BedrockConnection
from src.session.session_controller import SessionController
from src.audio.audio_streamer import AudioStreamer
from src.agents.agent_config import AGENTS
from src import display


logger = logging.getLogger("sonic.orchestrator")


class MultiAgentSonic:
    """Orchestrates multi-agent voice conversations."""

    def __init__(self, model_id: str, region: str, debug: bool = False):
        self.model_id = model_id
        self.region = region
        self.debug = debug
        self.state = ConversationState()
        self.registry = ToolRegistry.from_agents(AGENTS)
        logger.info("Initialized MultiAgentSonic (model=%s, region=%s)", model_id, region)

    async def start_conversation(self):
        """Start voice conversation with agent switching."""
        while True:
            try:
                agent = AGENTS.get(self.state.active_agent, AGENTS["customer_support"])
                logger.info("Starting session with agent=%s, voice=%s",
                            self.state.active_agent, agent.voice_id)
                display.show_agent_start(self.state.active_agent)

                await asyncio.sleep(0.1)

                # Create per-session components
                connection = BedrockConnection(self.model_id, self.region)
                audio_streamer = AudioStreamer(send_audio_fn=lambda b: None)  # wired below
                controller = SessionController(
                    connection=connection,
                    state=self.state,
                    registry=self.registry,
                    callback=audio_streamer,
                    voice_id=agent.voice_id,
                    system_prompt=agent.instruction,
                )
                # Wire audio streamer to send audio through the controller
                audio_streamer._send_audio = controller.send_audio
                audio_streamer._send_audio_content_start = controller.send_audio_content_start_event

                # Initialize and start
                await controller.start_session()

                # Stop transition music
                self._stop_music()

                # Start conversation (blocks until stop event)
                await audio_streamer.start_streaming()

                # Check for agent switch
                if self.state.switch_requested:
                    old = self.state.active_agent
                    new = self.state.complete_switch()
                    logger.info("Agent switch: %s → %s", old, new)
                    display.show_agent_switch(old, new)

                    # Play transition music
                    self._play_music()

                    # Close connection
                    await controller.stop()
                    await audio_streamer.stop_streaming()
                    continue
                else:
                    display.show_conversation_ended()
                    break

            except KeyboardInterrupt:
                display.show_interrupted()
                break
            except Exception as e:
                logger.exception("Session error")
                display.show_error(str(e))
                if self.debug:
                    import traceback
                    traceback.print_exc()
                break

    def _play_music(self):
        """Play transition music."""
        try:
            pygame.mixer.init()
            music_path = os.path.join(os.path.dirname(__file__), "..", "assets", "music.mp3")
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                display.show_music_playing()
        except Exception as e:
            display.show_error(f"Could not play music: {e}")

    def _stop_music(self):
        """Stop transition music."""
        try:
            pygame.mixer.music.stop()
            display.show_music_stopped()
        except:
            pass
