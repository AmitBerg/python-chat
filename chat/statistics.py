def word_count(logs):
    message_list = []
    for log in logs:
        _, messages, _ = log.parse_data()
        message_list += messages

    words = {}

    for message in message_list:
        for word in message.split():
            if word not in words:
                words[word] = 1
            else:
                words[word] += 1

    return sorted(words.items(), reverse=True, key=lambda x: x[1])


def msg_count_by_user(logs):
    msg_count = {}

    for log in logs:
        data = log.read()['conversation']
        for msg in data:
            if msg['user'] not in msg_count:
                msg_count[msg['user']] = 1
            else:
                msg_count[msg['user']] += 1

    return msg_count
