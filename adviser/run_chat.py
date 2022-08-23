###############################################################################
#
# Copyright 2020, University of Stuttgart: Institute for Natural Language Processing (IMS)
#
# This file is part of Adviser.
# Adviser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3.
#
# Adviser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adviser.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################

"""
This module allows to chat with the dialog system.
"""

import argparse
import os

from services.bst import HandcraftedBST
from services.domain_tracker.domain_tracker import DomainTracker
from services.service import DialogSystem
from utils.logger import DiasysLogger, LogLevel


def load_console():
    from services.hci.console import ConsoleInput, ConsoleOutput

    user_in = ConsoleInput(domain="")
    user_out = ConsoleOutput(domain="")
    return [user_in, user_out]


def load_gui():
    from services.hci.gui import GUIServer

    return GUIServer()


def load_nlg(backchannel: bool, domain=None):
    if backchannel:
        from services.nlg import BackchannelHandcraftedNLG

        nlg = BackchannelHandcraftedNLG(domain=domain, sub_topic_domains={"predicted_BC": ""})
    else:
        from services.nlg.nlg import HandcraftedNLG

        nlg = HandcraftedNLG(domain=domain)
    return nlg


# Create weblike domain for the restaurant search. Then return domain and service list
def load_search_domain():
    from examples.webapi.restaurants import RestaurantDomain, RestaurantNLU, RestaurantNLG
    from services.policy.policy_api import HandcraftedPolicy as PolicyAPI

    rest = RestaurantDomain()
    rest_nlu = RestaurantNLU(domain=rest)
    rest_nlg = RestaurantNLG(domain=rest)
    rest_bst = HandcraftedBST(domain=rest)
    rest_policy = PolicyAPI(domain=rest)
    return rest, [rest_nlu, rest_nlg, rest_bst, rest_policy]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ADVISER 2.0 Dialog System for restaurants")
    parser.add_argument(
        "domains",
        nargs="+",
        choices=["search", "booking"],
        help="Chat domain(s). For multidomain type as list: domain1 domain2 .. \n",
        default="ImsLecturers",
    )
    parser.add_argument("-g", "--gui", action="store_true", help="Start Webui server")
    parser.add_argument("--asr", action="store_true", help="enable speech input")
    parser.add_argument("--tts", action="store_true", help="enable speech output")
    parser.add_argument("--bc", action="store_true", help="enable backchanneling (doesn't work with 'weather' domain")
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    parser.add_argument(
        "--log_file",
        choices=["dialogs", "results", "info", "errors", "none"],
        default="none",
        help="specify file log level",
    )
    parser.add_argument(
        "--log",
        choices=["dialogs", "results", "info", "errors", "none"],
        default="results",
        help="specify console log level",
    )
    parser.add_argument("--cuda", action="store_true", help="enable cuda (currently only for asr/tts)")
    parser.add_argument(
        "--privacy",
        action="store_true",
        help="enable random mutations of the recorded voice to mask speaker identity",
        default=False,
    )
    args = parser.parse_args()

    num_dialogs = 100
    domains = []
    services = []

    # setup logger
    file_log_lvl = LogLevel[args.log_file.upper()]
    log_lvl = LogLevel[args.log.upper()]
    conversation_log_dir = "./conversation_logs"
    speech_log_dir = None
    if file_log_lvl == LogLevel.DIALOGS:
        # log user audio, system audio and complete conversation
        import time
        from math import floor

        print("This Adviser call will log all your interactions to files.\n")
        if not os.path.exists(f"./{conversation_log_dir}"):
            os.mkdir(f"./{conversation_log_dir}/")
        conversation_log_dir = "./" + conversation_log_dir + "/{}/".format(floor(time.time()))
        os.mkdir(conversation_log_dir)
        speech_log_dir = conversation_log_dir
    logger = DiasysLogger(
        file_log_lvl=file_log_lvl,
        console_log_lvl=log_lvl,
        logfile_folder=conversation_log_dir,
        logfile_basename="full_log",
    )

    # load domain specific services
    s_domain, s_services = load_search_domain()
    domains.append(s_domain)
    services.extend(s_services)

    # load HCI interfaces
    if args.gui:
        gui_service = load_gui()
        services.append(gui_service)
    else:
        services.extend(load_console())

    # setup dialog system
    services.append(DomainTracker(domains=domains))
    debug_logger = logger if args.debug else None
    ds = DialogSystem(services=services, debug_logger=debug_logger)
    error_free = ds.is_error_free_messaging_pipeline()
    if not error_free:
        ds.print_inconsistencies()
    if args.debug:
        ds.draw_system_graph()

    if args.gui:
        # run dialogs in webui
        import tornado
        import tornado.websocket
        import json
        from utils.topics import Topic

        class SimpleWebSocket(tornado.websocket.WebSocketHandler):
            def open(self, *args):
                gui_service.websocket = self

            def on_message(self, message):
                data = json.loads(message)
                # check token validity
                topic = data["topic"]
                if topic == "start_dialog":
                    # dialog start is triggered from web ui here
                    ds._start_dialog({"gen_user_utterance": ""})
                elif topic == "gen_user_utterance":
                    gui_service.user_utterance(message=data["msg"])

            def check_origin(self, *args, **kwargs):
                # allow cross-origin
                return True

        app = tornado.web.Application([(r"/ws", SimpleWebSocket)])
        app.listen(21512)
        tornado.ioloop.IOLoop.current().start()
    else:
        # run dialogs in terminal
        try:
            for _ in range(num_dialogs):
                ds.run_dialog({"gen_user_utterance": ""})
            # free resources
            ds.shutdown()
        except:
            import traceback

            print("##### EXCEPTION #####")
            traceback.print_exc()
