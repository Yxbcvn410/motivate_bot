import datetime as dt
import random as rnd
from typing import List

import tgbot_api as bot
import user_profile as user
import words


class MobManager:
    users: List[user.UserProfile]

    def __init__(self):
        self.users = []

    def swap(self, file):
        stream = open(file, 'w')
        for member in self.users:
            stream.write(str(member) + '<END>\n')
        stream.flush()

    def load(self, file):
        stream = open(file, 'r')
        self.users = []
        buf = ''
        for line in stream:
            if line == '<END>\n':
                uprof = user.UserProfile(1)
                uprof.load(buf)
                self.users.append(uprof)
                buf = ''
            else:
                buf += line

    def assign_destination(self, seed):
        rnd.seed(seed)
        rnd.shuffle(self.users)

    def get_user_by_id(self, chat_id):
        for member in self.users:
            if member.id == chat_id:
                return member

    def user_id_present(self, chat_id):
        for member in self.users:
            if member.id == chat_id:
                return True
        return False

    def broadcast(self, text):
        for member in self.users:
            bot.send_message(member.id, text)

    def notify_of(self, member_index):
        message_text = '''Привет! Пользователь {} {} Можешь в конце дня связаться с ним 
        и спросить его, как успехи :)'''.format(
            self.users[member_index].nickname,
            {False: 'пообещал сделать это:\n""' +
                    self.users[member_index].promises[
                        dt.date.today().toordinal()]['text'] + '""\n',
             True: 'ничего не собирается делать, потому что он лентяй\nПопробуй пнуть его, если получится'}[
                self.users[member_index].promises['status'] == -1])
        if self.users[member_index].promises[dt.date.today().toordinal()]['status'] in {-1, 0}:
            bot.send_message(self.users[member_index - 1].id, message_text)
            bot.send_message(self.users[member_index - 3].id, message_text)
            if self.users[member_index].today_status() == -1:
                bot.send_message(self.users[member_index].id, words.promise_undef)
            self.users[member_index].deliver_promise(
                dt.date.today().toordinal())
            return 1  # Notification successful
        return 0  # Already notified of promise

    def announce_promise(self, force):
        for member_index in range(len(self.users)):
            try:
                self.notify_of(member_index)
            except KeyError:  # No promise yet
                if force:
                    self.users[member_index].promises.update({
                        dt.date.today().toordinal(): {
                            'text': '',
                            'status': -1}})
                    self.notify_of(member_index)

    def wrap_status(self, user: user.UserProfile):
        return {2: 'ничего не делал', 3: 'выполнил обещание: ' + user.promises[dt.date.today().toordinal()]['text']}[
            user.today_status()]

    def announce_status(self):
        for member_index in range(len(self.users)):
            bot.send_message(self.users[member_index - 1].id,
                             "Итоги сегодняшнего дня: Пользователь {} {}".format(self.users[member_index].nickname,
                                                                                 self.wrap_status(
                                                                                     self.users[member_index])))
            bot.send_message(self.users[member_index - 3].id,
                             "Итоги сегодняшнего дня: Пользователь {} {}".format(self.users[member_index].nickname,
                                                                                 self.wrap_status(
                                                                                     self.users[member_index])))

    def remind_promise(self):
        for member in self.users:
            if member.today_status() == -1:
                bot.send_message(member.id,
                                 words.promise_listen)

    def remind_status(self):
        for member in self.users:
            if member.today_status() == 1:
                bot.send_message(member.id,
                                 words.status_listen.format(member.promises[dt.date.today().toordinal()]['text']))

    def reset_status(self):
        for member in self.users:
            if member.today_status() == 1:
                member.confirm_promise(dt.date.today().toordinal(), 3)
