from user_profile import UserProfile
from datetime import date
import words


class DialogueManager:
    def __init__(self, chat_id, mob):
        self.p2p_state = 'UNREGISTERED'
        self.id = chat_id
        self.mob = mob

    def set_status(self, status):
        self.mob.get_user_by_id(self.id).promises[date.today().toordinal()]['status'] = status

    def get_status(self):
        return self.mob.get_user_by_id(self.id).today_status()

    def promise_exists(self):
        return date.today().toordinal() in self.mob.get_user_by_id(self.id).promises.keys()

    def handle_message(self, message):
        if not self.p2p_state == 'UNREGISTERED':
            self.mob.get_user_by_id(self.id).update_nickname(message['from'])
        text = message['text']
        if self.p2p_state == 'AWAIT_PROMISE':
            if not self.promise_exists():
                self.mob.get_user_by_id(self.id).add_promise(date.today().toordinal(), text)
                self.p2p_state = 'IDLE'
                return words.promise_accept, words.menu,
            else:
                self.p2p_state = 'IDLE'
                return words.promise_decline.format(
                    self.mob.get_user_by_id(self.id).promises[date.today().toordinal()]), words.menu
        if self.p2p_state == 'AWAIT_STATUS':
            if self.get_status() in {-1, 2, 3}:
                self.p2p_state = 'IDLE'
                return words.status_decline, words.menu,
            if text.lower().replace(' ', '') == 'да':
                self.set_status(3)
                self.p2p_state = 'IDLE'
                return words.status_success, words.menu,
            if text.lower().replace(' ', '') == 'нет':
                self.set_status(2)
                self.p2p_state = 'IDLE'
                return words.status_fail, words.menu,
            return words.status_unknown, words.status_listen,
        if self.p2p_state == 'UNREGISTERED':
            if text.lower().replace(' ', '') == '/participate':
                self.p2p_state = 'IDLE'
                if not self.mob.user_id_present(id):
                    self.mob.users.append(UserProfile(self.id))
                return words.registered, words.menu,
            return words.greet,
        if self.p2p_state == 'IDLE':
            if text == '/stats':
                return self.mob.get_user_by_id(self.id).stats_str(),
            if text == '/promise':
                if not self.promise_exists():
                    self.p2p_state = 'AWAIT_PROMISE'
                    return words.promise_listen,
                return words.promise_decline.format(
                    self.mob.get_user_by_id(self.id).promises[date.today().toordinal()]['text']), words.menu
            if text == '/complete':
                if not self.promise_exists():
                    return words.no_promise,
                if self.get_status() in {0, 1}:
                    self.set_status(3)
                    return words.status_success, words.menu,
                return words.status_decline, words.menu,
            return words.menu,
