from flask import Flask, request, jsonify
import math

app = Flask(__name__)

# SIP Required Amount Calculation
@app.route('/api/investment/sip/required/', methods=['POST'])
def sip_required():
    data = request.json
    target_value = data['target_value']
    annual_rate_of_return = data['annual_rate_of_return'] / 100
    years = data['years']
    
    monthly_rate = annual_rate_of_return / 12
    number_of_months = years * 12
    
    if monthly_rate == 0:
        required_sip = target_value / number_of_months
    else:
        required_sip = target_value * (monthly_rate / (math.pow(1 + monthly_rate, number_of_months) - 1))
    
    return jsonify({
        "annual_rate_of_return": data['annual_rate_of_return'],
        "required_sip": round(required_sip, 2),
        "target_value": target_value,
        "years": years
    })

# SWP Withdrawals Calculation
@app.route('/api/investment/swp/withdrawals/', methods=['POST'])
def swp_withdrawals():
    data = request.json
    initial_investment = data['initial_investment']
    withdrawal_amount = data['withdrawal_amount']
    withdrawal_frequency = data['withdrawal_frequency']
    num_withdrawals = data['num_withdrawals']
    inflation_rate = data['inflation_rate']
    roi = data['roi']
    
    results = []
    current_investment = initial_investment
    
    for i in range(1, num_withdrawals + 1):
        investment_growth = current_investment * roi
        withdrawal_amount_adjusted = withdrawal_amount * (1 + inflation_rate) ** (i - 1) if withdrawal_frequency == 'annually' else withdrawal_amount
        current_investment = current_investment + investment_growth - withdrawal_amount_adjusted
        
        results.append({
            "current_investment": round(current_investment, 2),
            "investment_growth": round(investment_growth, 2),
            "withdrawal": i,
            "withdrawal_per_period": round(withdrawal_amount_adjusted, 2)
        })
    
    return jsonify({
        "inflation_rate": inflation_rate,
        "initial_investment": initial_investment,
        "number_of_withdrawals": num_withdrawals,
        "results": results,
        "roi": roi,
        "withdrawal_amount": withdrawal_amount,
        "withdrawal_frequency": withdrawal_frequency
    })

# SWP Withdrawals Number Until Depleted
@app.route('/api/withdrawals/swp/num_until_depleted/', methods=['POST'])
def swp_num_until_depleted():
    data = request.json
    initial_investment = data['initial_investment']
    withdrawal_amount = data['withdrawal_amount']
    withdrawal_frequency = data['withdrawal_frequency']
    inflation_rate = data['inflation_rate']
    roi = data['roi']
    
    num_withdrawals = 0
    current_investment = initial_investment
    
    while current_investment > 0:
        num_withdrawals += 1
        investment_growth = current_investment * roi
        withdrawal_amount_adjusted = withdrawal_amount * (1 + inflation_rate) ** (num_withdrawals - 1) if withdrawal_frequency == 'annually' else withdrawal_amount
        current_investment = current_investment + investment_growth - withdrawal_amount_adjusted
        
        if current_investment < 0:
            break
    
    return jsonify({
        "inflation_rate": inflation_rate,
        "initial_investment": initial_investment,
        "num_withdrawals_until_depleted": num_withdrawals,
        "roi": roi,
        "withdrawal_amount": withdrawal_amount,
        "withdrawal_frequency": withdrawal_frequency
    })

# SWP Total Withdrawn
@app.route('/api/withdrawals/swp/total_withdrawn/', methods=['POST'])
def swp_total_withdrawn():
    data = request.json
    initial_investment = data['initial_investment']
    withdrawal_amount = data['withdrawal_amount']
    withdrawal_frequency = data['withdrawal_frequency']
    inflation_rate = data['inflation_rate']
    roi = data['roi']
    
    num_withdrawals = 0
    current_investment = initial_investment
    total_withdrawn = 0
    
    withdrawals_per_year = 1 if withdrawal_frequency == 'annually' else (12 if withdrawal_frequency == 'monthly' else 4 if withdrawal_frequency == 'quarterly' else 0)
    
    if withdrawals_per_year == 0:
        return jsonify({"error": "Invalid withdrawal frequency"})
    
    while current_investment > 0:
        num_withdrawals += 1
        investment_growth = current_investment * roi
        withdrawal_amount_adjusted = withdrawal_amount * (1 + inflation_rate) ** (num_withdrawals - 1)
        total_withdrawn += withdrawal_amount_adjusted
        current_investment = current_investment + investment_growth - withdrawal_amount_adjusted
        
        if num_withdrawals > 1000:
            break
    
    return jsonify({
        "inflation_rate": inflation_rate,
        "initial_investment": initial_investment,
        "num_withdrawals": num_withdrawals,
        "roi": roi,
        "total_amount_withdrawn": round(total_withdrawn, 2),
        "withdrawal_amount": withdrawal_amount,
        "withdrawal_frequency": withdrawal_frequency,
        "withdrawals_per_year": withdrawals_per_year
    })

if __name__ == '__main__':
    app.run(debug=True)
