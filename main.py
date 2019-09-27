import datetime

import tgbot_api as bot
from dialogue_manager import DialogueManager
from mob_manager import MobManager

# TODO: Add timezone support
upd_offset = 0
mob = MobManager()
dialogues = {}
morning = [8, 10, 11, 12]
evening = [18, 21, 22]
night = 23
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
                bot.send_message(u['message']['from']['id'], msg)
            print(u['message']['from'] + " - '" + u['message']['text'] + "'")
        mob.swap('mob_swap')

    # Check timers
    if full_time(datetime.datetime.now()):
        hr = datetime.datetime.now().hour
        for i in range(len(evening) - 1):
            if hr == morning[i] and morning_reminders[i]:
                print('NOTIFY MORN: {}'.format(morning[i]))
                mob.remind_promise()
                mob.announce_promise(False)
                set_global_p2p_state({-1}, 'AWAIT_PROMISE')
                morning_reminders[i] = False
        if hr == morning[-1] and morning[-1]:
            print('NOTIFY DAY: {}'.format(evening[-1]))
            mob.announce_promise(True)
            morning_reminders[-1] = False
        for i in range(len(evening)):
            if hr == evening[i] and evening_reminders[i]:
                print('NOTIFY EVEN: {}'.format(evening[i]))
                mob.remind_status()
                set_global_p2p_state({1}, 'AWAIT_STATUS')
                evening_reminders[i] = False
        if hr == night and night_reminder:
            morning_reminders = [True] * len(morning_reminders)
            evening_reminders = [True] * len(morning_reminders)
            night_reminder = False
            mob.reset_status()
            mob.announce_status()
            print('NOTIFY DAY: {}'.format(night))
