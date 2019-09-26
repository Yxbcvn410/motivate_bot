import tgbot_api as bot
from mob_manager import MobManager
from dialogue_manager import DialogueManager
import datetime

upd_offset = 0
mob = MobManager()
dialogues = {}
morning_reminders = [True] * 3
evening_reminders = [True] * 3
night_reminder = True


def set_global_p2p_state(state, p2p_state):
    global mob
    for member in mob.users:
        if member.today_status() in state:
            dialogues[member.id].p2p_state = p2p_state


def full_time(t: datetime):
    return t.minute > 58


try:
    mob.load('mob_swap')
    for member in mob.users:
        dm = DialogueManager(member.id, mob)
        dm.p2p_state = 'IDLE'
        dialogues.update({member.id: dm})
except FileNotFoundError:
    print('WARNING: No mob swapfile detected')  # Swap does not exist

while True:
    # Check for updates
    updates = []
    try:
        updates = bot.get_updates(upd_offset)['result']
    except KeyboardInterrupt:
        mob.swap('mob_swap')
        mob.broadcast('Бот упал и не встанет, пока вы не попросите об этом @aryavorskiy')
        exit()
    for u in updates:
        if u['update_id'] >= upd_offset:
            upd_offset = u['update_id'] + 1
            if not u['message']['from']['id'] in dialogues.keys():
                dialogues.update({u['message']['from']['id']: DialogueManager(u['message']['from']['id'], mob)})
            msgs_to_send = dialogues[u['message']['from']['id']].handle_message(u['message'])
            for msg in msgs_to_send:
                print(bot.send_message(u['message']['from']['id'], msg))
            print(u)
        mob.swap('mob_swap')

    # Check timers
    if full_time(datetime.datetime.now()):
        hr = datetime.datetime.now().hour
        if hr == 7 and morning_reminders[0]:
            mob.remind_promise()
            mob.announce_promise(False)
            set_global_p2p_state({-1}, 'AWAIT_PROMISE')
            morning_reminders[0] = False
            night_reminder = True
        if hr == 9 and morning_reminders[1]:
            mob.remind_promise()
            mob.announce_promise(False)
            set_global_p2p_state({-1}, 'AWAIT_PROMISE')
            morning_reminders[1] = False
        if hr == 11 and morning_reminders[1]:
            mob.announce_promise(True)
            morning_reminders[2] = False
        if hr == 18 and morning_reminders[0]:
            mob.remind_status()
            set_global_p2p_state({1}, 'AWAIT_STATUS')
            evening_reminders[0] = False
        if hr == 20 and morning_reminders[1]:
            mob.remind_promise()
            set_global_p2p_state({1}, 'AWAIT_STATUS')
            evening_reminders[1] = False
        if hr == 22 and morning_reminders[1]:
            mob.remind_promise()
            set_global_p2p_state({1}, 'AWAIT_STATUS')
            evening_reminders[2] = False
        if hr == 23 and night_reminder:
            morning_reminders = [True] * 3
            evening_reminders = [True] * 3
            night_reminder = False
            mob.reset_status()
            mob.announce_status()

