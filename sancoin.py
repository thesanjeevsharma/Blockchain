#Blockchain - Core Project

#Importing Files
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from uuid import uuid4
# from urllib.parse import urlparse
from urlparse import urlparse
import requests

#Building Blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.createBlock(proof = 1, prevHash = '0')
        self.nodes = set()
    
    def createBlock(self, proof, prevHash):
        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : str(datetime.datetime.now()),
            'proof' : proof,
            'prevHash' : prevHash,
            'transactions' : self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block
    
    def getPrevBlock(self):
        return self.chain[-1]
    
    def proofOfWork(self, prevProof):
        newProof = 1
        checkProof = False
        while(not(checkProof)):
            hashOp = hashlib.sha256(str(newProof**2 - prevProof**2).encode()).hexdigest()
            if hashOp[:4] == '0000':
                checkProof = True
            else:
                newProof += 1
        return newProof
    
    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()
    
    def isChainValid(self, chain):
        prevBlock = chain[0]
        blockIndex = 1
        while (blockIndex < len(chain)):
            block = chain[blockIndex]
            if block['prevHash'] != self.hash(prevBlock):
                return False
            prevProof = prevBlock['proof']
            proof = block['proof']
            hashOp = hashlib.sha256(str(proof**2 - prevProof**2).encode()).hexdigest()
            if (hashOp[:4] != '0000'):
                return False
            prevBlock = block
            blockIndex += 1
        return True
    
    def addTransaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender' : sender,
            'receiver' : receiver,
            'amount' : amount
        })
        previousBlock = self.getPrevBlock()
        return previousBlock['index'] + 1
    
    def addNode(self, address):
        parsedURL = urlparse(address)
        self.nodes.add(parsedURL.netloc)
        
    def replaceChain(self):
        network = self.nodes
        longestChain = None
        maxLength = len(self.chain)
        for node in network:
            response = requests.get('http://' + node + '/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > maxLength and self.isChainValid(chain):
                    maxLength = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False
                    
        

#Mining Blockchain
## Web App

app = Flask(__name__)

# Creating an address for the node
nodeAddress = str(uuid4()).replace('-','')

##Blockchain Instance

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prevBlock = blockchain.getPrevBlock()
    prevProof = prevBlock['proof']
    proof = blockchain.proofOfWork(prevProof)
    prevHash = blockchain.hash(prevBlock)
    blockchain.addTransaction(sender = nodeAddress, receiever = 'Sanjeev', amount = 10)
    block = blockchain.createBlock(proof, prevHash)
    response = {
                'message' : "Congratulations! You've just mined a block.",
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'prevHash' : block['prevHash'] ,
                'transactions' : block['transactions']
    }
    return jsonify(response), 200
    
    
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.isChainValid(blockchain.chain)
    if is_valid:
        response = {'message' : "Everything's good!"}
        return jsonify(response), 200
    else:
        response = {'message' : "Oops! We've a problem."}
        return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements are missing.', 400
    index = blockchain.addTransaction(json['sender'], json['receiver'], json['amount'])
    response = {'message' : 'This transaction will be added to Block ' + index}
    return jsonify(response), 201
    
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.addNode(node)
    response = { 'message' : 'All the nodes are now connected. The Sancoin Blockchain now containes the following nodes:', 
                'total_nodes' : list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    isChainReplaced = blockchain.replaceChain()
    if isChainReplaced:
        response = {'message' : "Chains were different. Replaced!",
                   'new_chain' : blockchain.chain}
    else:
        response = {'message' : "All good. This chain is the largest one!",
                   'actual_chain' : blockchain.chain}
    return jsonify(response), 200

#Running the App
app.run(host = '0.0.0.0', port = 5001)

