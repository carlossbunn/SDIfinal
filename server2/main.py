from flask import Flask, request, jsonify
import hashlib
import datetime as date
import json
import os
import requests
import threading
import time

app = Flask(__name__)

class Block:
    def __init__(self, index, timestamp, cpf, nome, naturalidade, data_nascimento, previous_hash, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.cpf = cpf
        self.nome = nome
        self.naturalidade = naturalidade
        self.data_nascimento = data_nascimento
        self.previous_hash = previous_hash
        self.hash = hash if hash else self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update(
            str(self.index).encode('utf-8')
            + str(self.timestamp).encode('utf-8')
            + self.cpf.encode('utf-8')
            + self.nome.encode('utf-8')
            + self.naturalidade.encode('utf-8')
            + self.data_nascimento.encode('utf-8')
            + str(self.previous_hash).encode('utf-8')
        )
        return sha.hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp.isoformat(),
            'cpf': self.cpf,
            'nome': self.nome,
            'naturalidade': self.naturalidade,
            'data_nascimento': self.data_nascimento,
            'previous_hash': self.previous_hash,
            'hash': self.hash,
        }

    @classmethod
    def from_dict(cls, block_dict):
        timestamp = date.datetime.fromisoformat(block_dict['timestamp'])
        return cls(
            block_dict['index'],
            timestamp,
            block_dict['cpf'],
            block_dict['nome'],
            block_dict['naturalidade'],
            block_dict['data_nascimento'],
            block_dict['previous_hash'],
            block_dict['hash'],
        )

class Blockchain:
    def __init__(self, filename, server1_url):
        self.chain = []
        self.filename = filename
        self.server1_url = server1_url
        self.load_from_file()

    def create_genesis_block(self):
        return Block(0, date.datetime.now(), '0', 'Genesis Block', 'N/A', 'N/A', '0')

    def add_block(self, block_dict):
        new_block = Block.from_dict(block_dict)
        if self.chain:
            if new_block.previous_hash == self.chain[-1].hash:
                self.chain.append(new_block)
                self.save_to_file()
                return new_block
            else:
                print("Erro: o hash do bloco anterior não corresponde.")
        else:
            if new_block.index == 0:
                self.chain.append(new_block)
                self.save_to_file()
                return new_block
            else:
                print("Erro: primeiro bloco não é um bloco Gênesis.")
        return None

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verifica se o hash do bloco atual está correto
            if current_block.hash != current_block.calculate_hash():
                print(f"Erro: Hash do bloco {current_block.index} está incorreto.")
                return False
            
            # Verifica se o hash do bloco anterior corresponde
            if current_block.previous_hash != previous_block.hash:
                print(f"Erro: Hash do bloco anterior {current_block.index} não corresponde.")
                return False
        
        # Se todos os blocos são válidos
        return True

    def save_to_file(self):
        with open(self.filename, 'w') as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=4)

    def load_from_file(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                blocks = json.load(f)
                self.chain = [Block.from_dict(block) for block in blocks]
        else:
            self.sync_with_server1()

    def sync_with_server1(self):
        try:
            response = requests.get(f'{self.server1_url}/chain')
            if response.status_code == 200:
                blocks = response.json()
                self.chain = [Block.from_dict(block) for block in blocks]
                
                # Validar a blockchain recebida
                if not self.is_valid():
                    print("Erro: A blockchain do servidor 1 é inválida.")
                    # Enviar solicitação para encerrar o servidor 1
                    requests.post(f'{self.server1_url}/shutdown')
                    return
                
                self.save_to_file()
            else:
                print("Erro ao sincronizar com o servidor 1:", response.text)
        except Exception as e:
            print("Erro ao sincronizar com o servidor 1:", e)

# URL do servidor 1
server1_url = 'http://localhost:5000'

# Instância da blockchain do servidor 2
blockchain = Blockchain('blockchain2.json', server1_url)

# Função para sincronizar com o servidor 1 periodicamente
def sync_with_server1():
    while True:
        blockchain.sync_with_server1()
        time.sleep(30)

sync_thread = threading.Thread(target=sync_with_server1, daemon=True)
sync_thread.start()

@app.route('/replicate_block', methods=['POST'])
def replicate_block():
    block_data = request.get_json()
    new_block = blockchain.add_block(block_data)
    if new_block:
        return jsonify(new_block.to_dict()), 201
    else:
        return jsonify({'error': 'Erro ao replicar o bloco'}), 400

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify([block.to_dict() for block in blockchain.chain])

if __name__ == '__main__':
    app.run(port=5001)
