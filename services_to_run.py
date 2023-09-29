
services_to_run = {
    "payment":   {
        "host":"127.0.0.1","port":5555
    },"payment_db":   {
        "host":"127.0.0.1","port":5556
    },
    "casino":{
        "host":"127.0.0.1","port":5050
    },"casino_db":{
        "host":"127.0.0.1","port":5051
    }
}
def main():
    for service in services_to_run:
        ...