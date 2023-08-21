from rpc import Client

def test_client():
    client = Client()
    print(client.sum((10, 20, 30, 40)))
    print(client.sub((10, 20, 30, 40)))
    print(client.mul((2, 3, 4, 5, 6)))
    print(client.div((100, 2)))
    print(client.div((100, 2, 2, 5)))
    client.close()


if __name__ == "__main__":
    test_client()