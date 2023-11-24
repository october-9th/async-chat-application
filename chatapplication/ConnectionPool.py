import asyncio
from textwrap import dedent


class ConnectionPool:
    def __init__(self):
        self.connection_pool = set()

    def send_welcome_message(self, writer):
        """
        Send a welcome message to new connection from client
        :param writer:
        :return:
        """
        message = dedent(f"""
            ===
            (Welcome {writer.nickname}!
    
            our network has {len(self.connection_pool) - 1} user active
            Action: 
                - type anything to chat
                - type /list to show all the active user
                - type /quit to quit
            ===
        """)
        writer.write(f'{message}\n'.encode())

    def broadcast_message(self, writer, message):
        """
        Broadcast a general message to entire pool
        :param writer: 
        :param message: 
        :return: 
        """
        for user in self.connection_pool:
            if user != writer:
                user.write(f"{message}\n".encode())

    def broadcast_user(self, writer):
        """
        Call the broadcast method with a message "new user join"
        :param writer:
        :return:
        """
        self.broadcast_message(writer, f"{writer.nickname} just joined the network")

    def broadcast_quit(self, writer):
        """
        Call the broadcast method with a message "user quit"
        :param writer:
        :return:
        """
        self.broadcast_message(writer, f"{writer.nickname} just quit")

    def broadcast_new_message(self, writer, message):
        """
        Call the broadcast method with a user's chat message
        :param writer:
        :param message:
        :return:
        """
        self.broadcast_message(writer, f"[{writer.nickname}] {message} ")

    def list_user(self, writer):
        """
        List all users in pool
        :return:
        """
        message = "===\n"
        message += "Currently connected user: "
        for user in self.connection_pool:
            if user == writer:
                message += f"\n - {user.nickname} (you)"
            else:
                message += f"\n - {user.nickname}"
        message += "\n==="
        writer.write(f'{message}\n'.encode())

    def add_user_to_pool(self, writer):
        """
        Add new user to the pool
        :param writer:
        :return:
        """
        self.connection_pool.add(writer)

    def remove_user_from_pool(self, writer):
        """
        Remove user from the pool
        :param writer:
        :return:
        """
        self.connection_pool.remove(writer)


async def handle_connection(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
):
    writer.write("> Enter your nickname: ".encode())
    response = await reader.readuntil(b'\n')
    nickname = response.decode().strip()
    writer.nickname = nickname
    connection_pool.add_user_to_pool(writer)
    connection_pool.send_welcome_message(writer)

    connection_pool.broadcast_user(writer)
    while True:
        try:
            data = await reader.readuntil(b'\n')
        except asyncio.exceptions.IncompleteReadError:
            connection_pool.broadcast_quit(writer)
            break
        message = data.decode().strip()
        if message.startswith('/quit'):
            connection_pool.broadcast_quit(writer)
            break
        elif message.startswith("/list"):
            connection_pool.list_user(writer)
            break
        else:
            connection_pool.broadcast_new_message(writer, message)
        await writer.drain()
        if writer.is_closing():
            break

    writer.close()
    await writer.wait_closed()
    connection_pool.remove_user_from_pool(writer)


async def main():
    server = await asyncio.start_server(handle_connection, "0.0.0.0", "9999")
    async with server:
        await server.serve_forever()


connection_pool = ConnectionPool()
asyncio.run(main())
