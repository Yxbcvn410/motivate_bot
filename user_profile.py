from ast import literal_eval


class UserProfile:
    promise_status = {-1: 'NOT_ASSIGNED', 0: 'UNDELIVERED', 1: 'DELIVERED', 2: 'CONFIRMED_FAILED',
                      3: 'CONFIRMED_SUCCESS'}

    def __init__(self, chat_id):
        self.id = chat_id
        self.promises = {}
        self.nickname = 'Unknown nickname'

    def load(self, str_p):
        self.id = int(str_p.split('\n')[0])
        self.promises = literal_eval(str_p.split('\n')[1])
        self.nickname = str_p.split('\n')[2]

    def __str__(self):
        return str(self.id) + '\n' + str(self.promises) + '\n' + self.nickname + '\n'

    def add_promise(self, date, text):
        self.promises.update({date: {'text': text, 'status': 0}})

    def deliver_promise(self, date):
        if self.promises[date]['status'] != -1:
            self.promises[date]['status'] = 1

    def confirm_promise(self, date, status):
        if not self.promises[date]['status'] in {0, 1}:
            raise RuntimeError(
                'Promise status already set to {}'.format(self.promise_status[self.promises[date]['status']]))
        elif status in {-1, 0, 1}:
            raise RuntimeError('Cannot set promise status to {}'.format(self.promise_status[status]))
        else:
            self.promises[date]['status'] = status

    def purge_promises(self, date):
        i = 0
        while i < len(self.promises):
            if list(self.promises.keys())[i] < date:
                self.promises.pop(list(self.promises.keys())[i])
            else:
                i += 1

    def update_nickname(self, message):
        if message['username'] == '':
            self.nickname = "[{}](tg://user?id=123456789)".format(message['first_name'] + " " + message['last_name'])
        else:
            self.nickname = '{} {}: @{}'.format(message['first_name'], message['last_name'], message['username'])

    def stats_str(self):
        pass  # TODO: Add stats
