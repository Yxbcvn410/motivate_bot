import tgbot_api as bot
from mob_manager import MobManager
from dialogue_manager import DialogueManager
import time

upd_offset = 0
mob = MobManager()
dialogues = {}

try:
    mob.load('mob_swap')
    for member in mob.users:
        dm = DialogueManager(member.id, mob)
        dm.p2p_state = 'IDLE'
        dialogues.update({member.id: dm})
except FileNotFoundError:
    print('WARNING: No mob swapfile detected')  # Swap does not exist

while True:
    updates = bot.get_updates(upd_offset)['result']
    for u in updates:
        if u['update_id'] >= upd_offset:
            upd_offset = u['update_id'] + 1
            if not mob.user_id_present(u['message']['from']['id']):
                dialogues.update({u['message']['from']['id']: DialogueManager(u['message']['from']['id'], mob)})
            msgs_to_send = dialogues[u['message']['from']['id']].handle_message(u['message'])
            for msg in msgs_to_send:
                print(bot.send_message(u['message']['from']['id'], msg))
            print(u)
        mob.swap('mob_swap')
