from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import hashlib
import json

app = Flask(__name__)

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.is_tampered = False

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def tamper(self, new_data):
        self.data = new_data
        self.hash = self.calculate_hash()
        self.is_tampered = True

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Genesis Block", "0")
        self.chain.append(genesis_block)

    def add_block(self, new_block):
        if not self.is_valid_block(new_block):
            raise ValueError("Invalid block")
        self.chain.append(new_block)

    def get_last_block(self):
        return self.chain[-1]

    def is_valid_block(self, block):
        last_block = self.get_last_block()
        if block.previous_hash != last_block.hash:
            return False
        if not block.hash.startswith('0000'):
            return False
        return True

    def mine_new_block(self, new_block):
        while not new_block.hash.startswith('0000'):
            new_block.hash = new_block.calculate_hash()
        self.add_block(new_block)

blockchain = Blockchain()

tax_data = []
grouped_tax = {
    'below_2_5_lakh': 0,
    'between_2_5_and_5_lakh': 0,
    'between_5_and_10_lakh': 0,
    'above_10_lakh': 0
}

expenditure_details = {
    'Road Development': 0,
    'Healthcare': 0,
    'Education': 0,
    'Defense': 0,
    'Social Welfare': 0,
    'Agriculture': 0,
    'Infrastructure': 0,
    'Environment': 0
}

@app.route('/')
def index():
    latest_transactions = tax_data[-5:]
    return render_template('index.html', latest_transactions=latest_transactions, blockchain=blockchain)

@app.route('/submit_tax', methods=['POST'])
def submit_tax():
    salary = float(request.form['salary'])
    amount = salary * 0.05
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tax_data_entry = {'salary': salary, 'amount': amount, 'timestamp': timestamp}
    tax_data.append(tax_data_entry)

    new_block = Block(
        index=len(blockchain.chain),
        timestamp=timestamp,
        data=tax_data_entry,
        previous_hash=blockchain.get_last_block().hash
    )
    blockchain.mine_new_block(new_block)

    if salary < 250000:
        grouped_tax['below_2_5_lakh'] += amount
    elif 250000 <= salary < 500000:
        grouped_tax['between_2_5_and_5_lakh'] += amount
    elif 500000 <= salary < 1000000:
        grouped_tax['between_5_and_10_lakh'] += amount
    else:
        grouped_tax['above_10_lakh'] += amount

    total_tax_collected = sum(grouped_tax.values())

    expenditure_details['Road Development'] = total_tax_collected * 0.15
    expenditure_details['Healthcare'] = total_tax_collected * 0.20
    expenditure_details['Education'] = total_tax_collected * 0.20
    expenditure_details['Defense'] = total_tax_collected * 0.10
    expenditure_details['Social Welfare'] = total_tax_collected * 0.10
    expenditure_details['Agriculture'] = total_tax_collected * 0.05
    expenditure_details['Infrastructure'] = total_tax_collected * 0.10
    expenditure_details['Environment'] = total_tax_collected * 0.05

    remaining_10_percent = total_tax_collected * 0.10
    expenditure_details['Reserve Fund'] = remaining_10_percent

    return redirect(url_for('index'))

@app.route('/government_expenditure')
def government_expenditure():
    total_tax_collected = sum(grouped_tax.values())
    total_expenditure = sum([amt for amt in expenditure_details.values()])
    remaining_10_percent = total_tax_collected * 0.10

    return render_template('government.html', 
                           grouped_tax=grouped_tax, 
                           expenditure_details=expenditure_details,
                           total_tax_collected=total_tax_collected, 
                           total_expenditure=total_expenditure, 
                           remaining_10_percent=remaining_10_percent)

@app.route('/tax_information')
def tax_information():
    return render_template('tax_information.html')

@app.route('/tamper_data', methods=['POST'])
def tamper_data():
    block_index = int(request.form['block_index'])
    new_data = request.form['new_data']
    
    try:
        new_data = json.loads(new_data)
    except ValueError as e:
        return f"Invalid data format: {e}", 400

    if block_index < 1 or block_index >= len(blockchain.chain):
        return "Invalid block index", 400

    block_to_tamper = blockchain.chain[block_index]
    block_to_tamper.tamper(new_data)

    for i in range(block_index + 1, len(blockchain.chain)):
        blockchain.chain[i].previous_hash = blockchain.chain[i - 1].hash
        blockchain.chain[i].hash = blockchain.chain[i].calculate_hash()
        blockchain.chain[i].is_tampered = True

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
