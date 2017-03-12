import os
import json
import pygame
import traceback

from hypatia.default_config import default_game_config, default_user_config
from hypatia.resources.filesystem import FilesystemResourcePack
from hypatia.tilemap import Tilemap
from hypatia.scenes.traceback import TracebackScene
from hypatia.scenes.tilemap import TilemapScene


class Game:
    def __init__(self, path):
        self.path = path
        with open(os.path.join(path, "config.json"), 'r') as fh:
            self.gameconfig = json.load(fh)

        self.gamename = self.gameconfig['name']
        self.gamefriendlyname = self.gameconfig['friendly_name']

        if 'user_config_path' in self.gameconfig:
            user_config_path = self.gameconfig['user_config_path']

        else:
            try:
                xdg_config_path = os.environ["XDG_CONFIG_PATH"]
            except:
                xdg_config_path = os.path.expanduser("~/.config/")

            user_config_path = os.path.join(xdg_config_path, self.gamename, "config.json")

        if os.path.exists(user_config_path):
            with open(user_config_path, "r") as fh:
                self.userconfig = json.load(fh)

        else:
            if 'user_config' in self.gameconfig:
                self.userconfig = self.gameconfig['user_config']
            else:
                self.userconfig = default_user_config

            if not os.path.exists(os.path.dirname(user_config_path)):
                os.makedirs(os.path.dirname(user_config_path), exist_ok=True)

            with open(user_config_path, 'w') as fh:
                json.dump(self.userconfig, fh, sort_keys=True, indent=4)

        self.resourcepack = FilesystemResourcePack(os.path.join(path, "resources"))

        self.clock = pygame.time.Clock()

        self.running = False
        self.scene_stack = []

    def scene_push(self, scenecls, *args, **kwargs):
        self.scene_stack.append(scenecls(self, *args, **kwargs))

    def scene_pop(self):
        self.scene_stack.pop()

    def scene_replace(self, scenecls, *args, **kwargs):
        self.scene_stack = []
        self.scene_push(scenecls, *args, **kwargs)

    def run(self):
        pygame.init()

        if self.gameconfig["font_face"] != "default":
            font_obj = self.resourcepack.open(os.path.join("/fonts", self.gameconfig["font_face"]))
        else:
            font_obj = None

        self.font = pygame.font.Font(font_obj, int(self.gameconfig['font_size']))

        self.running = True

        if self.userconfig['display']['fullscreen']:
            self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.display = pygame.display.set_mode(self.userconfig['display']['window_size'])

        self.scene_push(TilemapScene, self.resourcepack, self.gameconfig['starting_tilemap'], self.gameconfig["player_character"])

        while self.running:
            self.display.fill((0, 0, 0))

            # update current scene
            try:
                self.scene_stack[-1].update()
            except Exception as ex:
                if isinstance(self.scene_stack[-1], TracebackScene):
                    raise

                tb = traceback.format_exc()
                self.scene_push(TracebackScene, ex, tb)
                continue

            self.display.blit(self.scene_stack[-1].surface, (0, 0))

            # handle events
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False

                try:
                    self.scene_stack[-1].handle_event(ev)
                except Exception as ex:
                    if isinstance(self.scene_stack[-1], TracebackScene):
                        raise

                    tb = traceback.format_exc()
                    self.scene_push(TracebackScene, ex, tb)
                    continue

            # display FPS if it's asked for
            if 'fpsdisplay' in self.userconfig['display'] and self.userconfig['display']['fpsdisplay'] is True:
                fps = self.clock.get_fps()
                text = self.font.render("%.02f FPS" % fps, True, (255, 255, 255))
                self.display.blit(text, (0, 0))

            # clock tick
            if 'fpslimit' in self.userconfig['display']:
                if self.userconfig['display']['fpslimit'] > 0:
                    fpslimit = self.userconfig['display']['fpslimit']
                else:
                    fpslimit = 60
            else:
                fpslimit = 60

            self.clock.tick(fpslimit)
            pygame.display.flip()