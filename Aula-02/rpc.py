import socket
import threading

BUFFER_SIZE = 1024
STD_PORT = 14000
LOCAL_HOST = "127.0.0.1"

SUM = "__SUM__"
SUB = "__SUB__"
MUL = "__MUL__"
DIV = "__DIV__"
END = "__END__"

UTF = "utf-8"
SPLIT_CHAR = ";"

class Client:
    """
    Classe para criar um cliente que se conecta a um servidor remoto para executar operações.
    """

    def __init__(self, server_ip=LOCAL_HOST, server_port=STD_PORT):
        """
        Inicializa um cliente com o endereço do servidor e o número da porta.

        :param server_ip: Endereço IP do servidor.
        :param server_port: Número da porta do servidor.
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = create_client_connection(server_ip, server_port)

    def __del__(self):
        """
        Fecha a conexão do cliente com o servidor ao destruir o objeto.
        """
        self.close()

    def sum(self, args: int):
        """
        Envia uma solicitação de soma para o servidor e retorna o resultado.

        :param args: Números a serem somados.
        :return: Resultado da soma.
        """
        return int(self.__execute_server_task(SUM, args))

    def sub(self, args: int):
        """
        Envia uma solicitação de subtração para o servidor e retorna o resultado.

        :param args: Números a serem usados na subtração.
        :return: Resultado da subtração.
        """
        return int(self.__execute_server_task(SUB, args))

    def mul(self, args: float):
        """
        Envia uma solicitação de multiplicação para o servidor e retorna o resultado.

        :param args: Números a serem usados na multiplicação.
        :return: Resultado da multiplicação.
        """
        return float(self.__execute_server_task(MUL, args))

    def div(self, args: float):
        """
        Envia uma solicitação de divisão para o servidor e retorna o resultado.

        :param args: Números a serem usados na divisão.
        :return: Resultado da divisão.
        """
        return float(self.__execute_server_task(DIV, args))

    def __execute_server_task(self, task_id: str, args):
        """
        Executa uma tarefa no servidor e retorna o resultado.

        :param task_id: ID da tarefa a ser executada.
        :param args: Argumentos da tarefa.
        :return: Resultado da tarefa.
        """
        self.client_socket.send(self.__encode_message(task_id, args))
        return self.client_socket.recv(BUFFER_SIZE).decode(UTF)

    def close(self):
        """
        Fecha a conexão do cliente com o servidor.
        """
        self.client_socket.close()

    def __encode_message(self, operation: str, args):
        """
        Codifica uma mensagem para ser enviada ao servidor.

        :param operation: Operação a ser realizada.
        :param args: Argumentos da operação.
        :return: Mensagem codificada.
        """
        message = f"{operation}"
        if type(args) == int:
            message += f"{SPLIT_CHAR}{args}"
        else:
            for arg in args:
                message += f"{SPLIT_CHAR}{arg}"
        return message.encode(UTF)


class Server:
    """
    Classe para criar um servidor que aceita conexões de clientes e executa operações.
    """

    def __init__(self, port=STD_PORT):
        """
        Inicializa um servidor com o número da porta.

        :param port: Número da porta do servidor.
        """
        self.port = port
        self.server_socket = None

    def __del__(self):
        """
        Fecha o socket do servidor ao destruir o objeto.
        """
        self.server_socket.close()

    def start(self):
        """
        Inicia o servidor e espera por conexões de clientes.
        """
        self.server_socket = create_server_connection(self.port)
        print(f"O servidor está ouvindo na porta {self.port}...")
        try:
            while True:
                connection, address = self.server_socket.accept()
                thread = threading.Thread(target=self.__listen_client, args=(connection, address))
                thread.start()
        except KeyboardInterrupt:
            self.server_socket.close()
            print("\nO servidor foi finalizado...")

    def __listen_client(self, connection, address):
        """
        Escuta as mensagens do cliente e processa as tarefas solicitadas.

        :param connection: Conexão com o cliente.
        :param address: Endereço do cliente.
        """
        print(f"{address[0]} conectou\n")
        while True:
            message = connection.recv(BUFFER_SIZE)
            if message:
                task, args = self.__decode_message(message.decode(UTF))
                print(f"Cliente {address[0]} está executando alguma tarefa...")
                connection.send(self.__process_task(task, args).encode(UTF))
            else:
                break
        print(f"{address[0]} desconectou\n")
        connection.close()

    def __decode_message(self, message: str):
        """
        Decodifica uma mensagem recebida do cliente.

        :param message: Mensagem recebida.
        :return: Tarefa e argumentos da tarefa.
        """
        args = message.split(SPLIT_CHAR)
        cod = args[0]
        res = [obj for obj in args[1:]]
        return cod, res

    def __process_task(self, task_id: str, args) -> str:
        """
        Processa a tarefa solicitada pelo cliente.

        :param task_id: ID da tarefa a ser executada.
        :param args: Argumentos da tarefa.
        :return: Resultado da tarefa.
        """
        if task_id == SUM:
            return self.__sum_task(args)
        elif task_id == SUB:
            return self.__sub_task(args)
        elif task_id == MUL:
            return self.__mul_task(args)
        elif task_id == DIV:
            return self.__div_task(args)

    def __sum_task(self, args):
        """
        Executa a tarefa de soma.

        :param args: Números a serem somados.
        :return: Resultado da soma.
        """
        return f"{sum([int(num) for num in args])}"

    def __sub_task(self, args):
        """
        Executa a tarefa de subtração.

        :param args: Números a serem usados na subtração.
        :return: Resultado da subtração.
        """
        return f"{int(args[0]) + sum([(int(num) * -1) for num in args[1:]])}"

    def __mul_task(self, args):
        """
        Executa a tarefa de multiplicação.

        :param args: Números a serem usados na multiplicação.
        :return: Resultado da multiplicação.
        """
        res = 1
        for number in args:
            res *= int(number)
        return f"{res}"

    def __div_task(self, args):
        """
        Executa a tarefa de divisão.

        :param args: Números a serem usados na divisão.
        :return: Resultado da divisão.
        """
        res = int(args[0])
        for number in args[1:]:
            res /= int(number)
        return f"{res}"


def create_server_connection(port=STD_PORT):
    """
    Cria e configura um socket do servidor.

    :param port: Número da porta do servidor.
    :return: Socket do servidor configurado.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", port))
    server_socket.listen(0)
    return server_socket


def create_client_connection(server, port=STD_PORT):
    """
    Cria uma conexão de cliente para o servidor.

    :param server: Endereço IP do servidor.
    :param port: Número da porta do servidor.
    :return: Conexão do cliente.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, port))
    return client_socket