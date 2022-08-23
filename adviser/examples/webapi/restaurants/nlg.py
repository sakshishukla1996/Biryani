from utils import DiasysLogger
from utils import SysAct, SysActionType
from services.service import Service, PublishSubscribe

# import locale

# locale.setlocale(locale.LC_TIME, "en_GB.UTF-8")


class RestaurantNLG(Service):
    """Simple NLG for the weather domain"""

    def __init__(self, domain, logger=DiasysLogger()):
        # only calls super class' constructor
        super(RestaurantNLG, self).__init__(domain, debug_logger=logger)

    @PublishSubscribe(sub_topics=["sys_act"], pub_topics=["sys_utterance"])
    def generate_system_utterance(self, sys_act: SysAct = None) -> dict(sys_utterance=str):
        """Main function for generating and publishing the system utterance

        Args:
            sys_act: the system act for which to create a natural language realisation

        Returns:
            dict with "sys_utterance" as key and the system utterance as value
        """
        # print(f"Generate system utterance: {sys_act}, '{sys_act.type}'")
        # print(f"System slots fromNLG are: {sys_act.slot_values.values()}")
        if sys_act is None or sys_act.type == SysActionType.Welcome:
            return {
                "sys_utterance": "Hi! Welcome to our restaurant recommendation system. What cuisine would you like to have today?"
            }
        if sys_act.type == SysActionType.Bad:
            return {"sys_utterance": "Sorry, I did not understand. Try rephrasing your response."}
        elif sys_act.type == SysActionType.Bye:
            return {"sys_utterance": "Thank you, good bye"}
        elif sys_act.type == SysActionType.Request:
            slot = list(sys_act.slot_values.keys())[0]
            # print(f"==== SysAction is Request and Slot is '{slot}'")
            if slot == "cuisine":
                return {"sys_utterance": "What cuisines are you planning to have today?"}
            elif slot == "location":
                return {"sys_utterance": "Which city are you at?"}
            elif slot == "restaurants":
                rest = sys_act.slot_values
                return {
                    "sys_utterance": f"Here are a list of restaurants: {rest}\nDo you also want see the list of restaurants?"
                }
            else:
                assert False, "Only the cuisine and the location can be requested"
        elif sys_act.type == SysActionType.RequestMore:
            try:
                slot = list(sys_act.slot_values.keys())[0]
            except:
                slot = list(sys_act.slot_values.keys())
                print(f"Exception raised and slot is {sys_act.slot_values}")

            # print(f"==== SysAction is RequestMore and Slot is '{slot}'")
            if slot == "cuisine":
                return {"sys_utterance": "What cuisines are you planning to have today?"}
            elif slot == "location":
                return {"sys_utterance": "Which city are you at?"}
            elif slot == "restaurants":
                rest = sys_act.slot_values
                return {
                    "sys_utterance": f"Here are a list of restaurants: {rest}\nDo you also want see the list of restaurants?"
                }
            else:
                assert False, "Only the cuisine and the location can be requested"
        else:
            # print(f"-------> Value of sys_act are {sys_act} and last results are: {self.domain.last_results}")
            location = sys_act.slot_values["location"]
            cuisine = sys_act.slot_values["cuisine"]
            rest = sys_act.slot_values["restaurants"]
            return {
                "sys_utterance": f"Recommended {cuisine[0]} restaurants in {location[0]} is {rest[0]}.\n\tWhich else cuisine would you like to try?"
            }
