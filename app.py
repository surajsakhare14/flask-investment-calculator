from flask import Flask, request, jsonify
import math

app = Flask(__name__)

@app.route('/')
def Run():
    return "Investment Calculations assigenment! Hello Vercel 2"


# Endpoint for SIP Required Amount Calculation
@app.route('/api/investment/sip/required/', methods=['POST', 'GET'])
def sip_required():
    if request.method == 'POST':
        data = request.json
        target_value = data['target_value']
        annual_rate_of_return = data['annual_rate_of_return'] / 100
        years = data['years']
    elif request.method == 'GET':
        target_value = float(request.args.get('target_value'))
        annual_rate_of_return = float(request.args.get('annual_rate_of_return')) / 100
        years = int(request.args.get('years'))
    
    monthly_rate = annual_rate_of_return / 12
    number_of_months = years * 12
    
    if monthly_rate == 0:
        required_sip = target_value / number_of_months
    else:
        required_sip = target_value * (monthly_rate / (math.pow(1 + monthly_rate, number_of_months) - 1))
    
    return jsonify({
        "annual_rate_of_return": annual_rate_of_return * 100,
        "required_sip": round(required_sip, 2),
        "target_value": target_value,
        "years": years
    })

# Endpoint for SWP Withdrawals Calculation
@app.route('/api/investment/swp/withdrawals/', methods=['POST', 'GET'])
def swp_withdrawals():
    if request.method == 'POST':
        data = request.json
        initial_investment = data['initial_investment']
        withdrawal_amount = data['withdrawal_amount']
        withdrawal_frequency = data['withdrawal_frequency']
        num_withdrawals = data['num_withdrawals']
        inflation_rate = data['inflation_rate']
        roi = data['roi']
    elif request.method == 'GET':
        initial_investment = float(request.args.get('initial_investment'))
        withdrawal_amount = float(request.args.get('withdrawal_amount'))
        withdrawal_frequency = request.args.get('withdrawal_frequency')
        num_withdrawals = int(request.args.get('num_withdrawals'))
        inflation_rate = float(request.args.get('inflation_rate'))
        roi = float(request.args.get('roi'))
    
    results = []
    current_investment = initial_investment
    withdrawals_per_year = 1 if withdrawal_frequency == 'annually' else (12 if withdrawal_frequency == 'monthly' else 4)
    
    for i in range(1, num_withdrawals + 1):
        investment_growth = current_investment * roi / withdrawals_per_year
        withdrawal_amount_adjusted = withdrawal_amount * (1 + inflation_rate) ** (i - 1)
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

# Endpoint for SWP Number of Withdrawals Until Depletion
@app.route('/api/withdrawals/swp/num_until_depleted/', methods=['POST', 'GET'])
def swp_num_until_depleted():
    if request.method == 'POST':
        data = request.json
        initial_investment = float(data.get('initial_investment'))
        withdrawal_amount = float(data.get('withdrawal_amount'))
        withdrawal_frequency = data.get('withdrawal_frequency')
        inflation_rate = float(data.get('inflation_rate'))
        roi = float(data.get('roi'))
    elif request.method == 'GET':
        initial_investment = float(request.args.get('initial_investment'))
        withdrawal_amount = float(request.args.get('withdrawal_amount'))
        withdrawal_frequency = request.args.get('withdrawal_frequency')
        inflation_rate = float(request.args.get('inflation_rate'))
        roi = float(request.args.get('roi'))

    num_withdrawals = 0
    current_investment = initial_investment
    withdrawals_per_year = 1 if withdrawal_frequency == 'annually' else (12 if withdrawal_frequency == 'monthly' else 4)

    while current_investment > 0:
        num_withdrawals += 1
        investment_growth = current_investment * roi / withdrawals_per_year
        withdrawal_amount_adjusted = withdrawal_amount * (1 + inflation_rate) ** (num_withdrawals / withdrawals_per_year)
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



@app.route('/api/withdrawals/swp/total_withdrawn', methods=['GET', 'POST'])
def total_withdrawn():
    # Handle GET and POST requests
    if request.method == 'POST':
        data = request.json
    else:
        data = request.args

    # Parse input data
    try:
        initial_investment = float(data.get('initial_investment'))
        withdrawal_amount = float(data.get('withdrawal_amount'))
        withdrawal_frequency = data.get('withdrawal_frequency')
        inflation_rate = float(data.get('inflation_rate'))
        roi = float(data.get('roi'))
    except (TypeError, ValueError) as e:
        return jsonify({"error": "Invalid input format."}), 400

    # Determine the number of withdrawals per year based on frequency
    if withdrawal_frequency == 'monthly':
        withdrawals_per_year = 12
    elif withdrawal_frequency == 'quarterly':
        withdrawals_per_year = 4
    elif withdrawal_frequency == 'annually':
        withdrawals_per_year = 1
    else:
        return jsonify({"error": "Invalid withdrawal frequency."}), 400

    # Initialize current investment, withdrawals, and total amount withdrawn
    current_investment = initial_investment
    num_withdrawals = 0
    total_amount_withdrawn = 0

    # Check if the withdrawal amount is larger than the initial investment
    if withdrawal_amount > initial_investment:
        return jsonify({
            "inflation_rate": inflation_rate,
            "initial_investment": initial_investment,
            "num_withdrawals": 0,
            "roi": roi,
            "total_amount_withdrawn": 0,
            "withdrawal_amount": withdrawal_amount,
            "withdrawal_frequency": withdrawal_frequency,
            "withdrawals_per_year": withdrawals_per_year
        })

    # Calculate withdrawals until the investment is depleted
    while current_investment > 0:
        # Apply ROI for the current period
        current_investment += (current_investment * (roi / withdrawals_per_year))

        # If current investment is less than the withdrawal amount, stop
        if current_investment < withdrawal_amount:
            break

        # Deduct the withdrawal amount and increase the counter
        current_investment -= withdrawal_amount
        num_withdrawals += 1
        total_amount_withdrawn += withdrawal_amount

    # Prepare the output JSON
    result = {
        "inflation_rate": inflation_rate,
        "initial_investment": initial_investment,
        "num_withdrawals": num_withdrawals,
        "roi": roi,
        "total_amount_withdrawn": total_amount_withdrawn,
        "withdrawal_amount": withdrawal_amount,
        "withdrawal_frequency": withdrawal_frequency,
        "withdrawals_per_year": withdrawals_per_year
    }

    # Return the result as JSON
    return jsonify(result)










