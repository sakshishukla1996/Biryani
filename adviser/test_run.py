import sys
sys.path.append("..")
import inspect
from utils.domain.jsonlookupdomain import JSONLookupDomain
from services.nlu import HandcraftedNLU
from services.bst import HandcraftedBST

from utils.logger import DiasysLogger, LogLevel
from services.hci import ConsoleInput, ConsoleOutput
from services.domain_tracker import DomainTracker

domain = JSONLookupDomain(name='booking')
nlu = HandcraftedNLU(domain=domain)
bst = HandcraftedBST(domain=domain)

user_input = input('>>> ')
while user_input.strip().lower() not in ('', 'exit', 'bye', 'goodbye'):
    user_acts = nlu.extract_user_acts(user_input)['user_acts']
    update_bst = bst.update_bst(user_acts)
    user_act_bst = bst._handle_user_acts(user_acts)
    print('\n'.join([repr(user_act) for user_act in user_acts]))
    print('updated bst:', update_bst, 'handle user act:', user_act_bst)
    user_input = input('>>> ')
