#Blockchain - Core Project

#Importing Files
import datetime
import hashlib
import json
from flask import Flask, jsonify

#Building Blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.createBlock(proof = 1, prevHash = '0')
    
    def createBlock(self, proof, prevHash):
        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : str(datetime.datetime.now()),
            'proof' : proof,
            'prevHash' : prevHash
        }
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
    

#Mining Blockchain
## Web App

app = Flask(__name__)

##Blockchain Instance

blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prevBlock = blockchain.getPrevBlock()
    prevProof = prevBlock['proof']
    proof = blockchain.proofOfWork(prevProof)
    prevHash = blockchain.hash(prevBlock)
    block = blockchain.createBlock(proof, prevHash)
    response = {
                'message' : "Congratulations! You've just mined a block.",
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'prevHash' : block['prevHash'] 
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

#Running the App
app.run(host = '0.0.0.0', port = 5000)
