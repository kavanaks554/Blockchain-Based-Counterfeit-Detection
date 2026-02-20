import hashlib
import json
from time import time
import pickle


class Block:
    def __init__(self, index, timestamp, sellerid, mid, pid, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.sellerid = sellerid
        self.mid = mid
        self.pid = pid
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()



class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
        self.load_chain()  # Load the existing blockchain data if it exists

    def create_genesis_block(self):
        genesis_block = Block(0, time(), None, None, None, "0")
        self.chain.append(genesis_block)

    def add_block(self, sellerid, mid, pid):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), time(), sellerid, mid, pid, previous_block.hash)
        self.chain.append(new_block)

    def save_chain(self):
        with open('blockchain_data.pkl', 'wb') as file:
            pickle.dump(self.chain, file)

    def load_chain(self):
        try:
            with open('blockchain_data.pkl', 'rb') as file:
                self.chain = pickle.load(file)
        except FileNotFoundError:
            # If the file does not exist, just create a new chain
            self.create_genesis_block()

    def get_blocks(self):
        return [(block.index, block.timestamp, block.sellerid, block.mid, block.pid, block.hash) for block in self.chain[1:]]


# Example usage
if __name__ == "__main__":
    # Create a blockchain
    blockchain = Blockchain()

    # Get blocks from the blockchain
    blocks = blockchain.get_blocks()
    #print("Blocks in the blockchain:")
    for block in blocks:
        print(block[2])
