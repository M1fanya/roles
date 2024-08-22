import discord
from discord import utils

# Конфигурация
POST_ID = 1275972380010876999  # Замените на реальный ID сообщения
CHANNEL_ID = 1275967567390838858  # Замените на реальный ID канала
ROLES = {
    '💜': 1208520871837171773,
    '🧡': 1209620663032217650,
    '❤️': 1091409706687406170,
    '💚': 1207090823104036905,
    '💙': 1209620565565112381,
    '🩷': 1236271929921372180,
    '💔': 1217052890011537428,
    '📛': 1275984835340406867,
    # Добавьте другие эмоджи и роли по необходимости
}

EXCROLES = []  # Замените на реальные ID исключаемых ролей
MAX_ROLES_PER_USER = 15  # Установите нужное значение
TOKEN = 'YOUR_TOKEN'  # Замените на реальный токен вашего бота

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(intents=intents, **options)

    async def on_ready(self):
        print(f'Вошел как {self.user}!')
        await self.sync_roles()

    async def sync_roles(self):
        channel = self.get_channel(CHANNEL_ID)
        if channel is None:
            print(f'[ОШИБКА] Не удалось получить канал с ID {CHANNEL_ID}')
            return

        message = await channel.fetch_message(POST_ID)
        
        # Получаем текущие реакции на сообщении
        reactions = message.reactions
        current_reacts = {str(r.emoji): set() for r in reactions}
        
        for reaction in reactions:
            async for user in reaction.users():
                if not user.bot:
                    current_reacts[str(reaction.emoji)].add(user.id)

        for emoji, role_id in ROLES.items():
            role = utils.get(message.guild.roles, id=role_id)
            if role:
                for member in message.guild.members:
                    if role in member.roles and member.id not in current_reacts.get(emoji, set()):
                        try:
                            await member.remove_roles(role)
                            print(f'[СИНХРОНИЗАЦИЯ] Роль {role.name} была снята у пользователя {member.display_name}')
                        except Exception as e:
                            print(f'[ОШИБКА] Не удалось снять роль {role.name} у пользователя {member.display_name}: {repr(e)}')

    async def on_raw_reaction_add(self, payload):
        if payload.message_id == POST_ID:
            channel = self.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            member = utils.get(message.guild.members, id=payload.user_id)

            try:
                emoji = str(payload.emoji)
                role_id = ROLES.get(emoji)
                if role_id:
                    role = utils.get(message.guild.roles, id=role_id)
                    if len([r for r in member.roles if r.id not in EXCROLES]) < MAX_ROLES_PER_USER:
                        await member.add_roles(role)
                        print(f'[УСПЕХ] Пользователь {member.display_name} получил роль {role.name}')
                    else:
                        await message.remove_reaction(payload.emoji, member)
                        print(f'[ОШИБКА] Слишком много ролей у пользователя {member.display_name}')
                else:
                    print(f'[ОШИБКА] Роль не найдена для эмодзи {emoji}')

            except Exception as e:
                print(repr(e))

    async def on_raw_reaction_remove(self, payload):
        channel = self.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = utils.get(message.guild.members, id=payload.user_id)

        try:
            emoji = str(payload.emoji)
            role_id = ROLES.get(emoji)
            if role_id:
                role = utils.get(message.guild.roles, id=role_id)
                await member.remove_roles(role)
                print(f'[УСПЕХ] Роль {role.name} была удалена у пользователя {member.display_name}')
            else:
                print(f'[ОШИБКА] Роль не найдена для эмодзи {emoji}')

        except Exception as e:
            print(repr(e))

# Запуск клиента
client = MyClient()
client.run(TOKEN)
