docker-compose uo -d --build

para entrar no container cliente:

docker exec -it cliente bash 
 

dentro do container, execute os testes de requisições aos servidores: 

python3 cliente.py --host servidor_seq --port 80 --requests 10 
python3 cliente.py --host servidor_conc --port 8080 --requests 10 

link para o video:

https://youtu.be/K27tiNHxBxw
