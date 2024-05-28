from flask import Flask, render_template, request, Response
import matplotlib.pyplot as plt


app = Flask(__name__)

# Declare the finance 
finance = {
  'Shopping': {'amounts': [], 'descriptions': []},
  'Bills': {'amounts': [], 'descriptions': []},
  'Eating out': {'amounts': [], 'descriptions': []},
  'Groceries': {'amounts': [], 'descriptions': []},
  'Remaining budget': 0,
  'Total expense': 0
}

# Record the expenses . This is for the table to be shown in html
def get_all_expenses():
  expenses = []
  for category, details in finance.items():
    if category not in ('Total expense', 'Remaining budget'):
      expense = {'category': category, 'amounts': details['amounts'], 'descriptions': details['descriptions']}
      expenses.append(expense)
  return expenses

# Update the expense with description
def add_expense(category, amount, description):
  finance[category]['amounts'].append(amount)               # Since 4 spending categories are lists, I used 'append'
  finance[category]['descriptions'].append(description)  
  finance['Total expense'] += amount                       # Also update the total expense as the user submit

# Generate the graphical spendings
# This is pie chart of the categories
def generate_pie_chart():
  labels = list(finance.keys())[:-2]                       # Exclude 'Total expense' and 'Remaining budget'
  values = [sum(finance[label]['amounts']) for label in labels]   # because values of the above 4 is map of lists

  labels.append('Remaining Budget')                        # Then add the remaining budget which is just simple key and value of the map 'finance'
  values.append(finance['Remaining budget'])

  colors = ['pink'] * len(labels)                          # set color

  explode = [0.1 if label == 'Remaining Budget' else 0 for label in labels]   # to make the remaining budget sector pop

  plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, explode=explode, wedgeprops={'linewidth': 1, 'edgecolor':'black'})
  plt.savefig('static/pie_chart.png')
  plt.close()

# This is to generate the spending of each category
def generate_cat():
  finance_1 = {key: value for key, value in finance.items() if key not in ['Remaining budget', 'Total expense']} # Exlude the last two rows
  fig, axs = plt.subplots(2, 2)

  axs = axs.flatten()    # to make the indexing easier

  for i, (category, details) in enumerate(finance_1.items()):    
    amounts = details['amounts']
    descriptions = details['descriptions']

    axs[i].bar(descriptions, amounts, color='pink')
    axs[i].set_xlabel('Items')
    axs[i].set_ylabel('Amount')
    axs[i].set_title(f'{category} Expenses')
    axs[i].set_xticks(range(len(descriptions)))
    axs[i].tick_params(axis='x', rotation=45)  # for better readability

  plt.tight_layout()
  plt.savefig('static/Groceries_pie_chart.png')
  plt.close()


@app.route('/', methods=['GET', 'POST'])
def index():
  error = None
  expenses = get_all_expenses() 

  if request.method == 'POST':

    # Get the input from the user
    category = request.form['category']
    amount_str = request.form['amount']
    description = request.form['description'] 

    # if the amount is the number
    try:
      amount = float(amount_str)
      category_name = category_mapping[category]     # category from html is passed as '1','2','3','4'. So it is traced to get the name using the map 'category_mapping'
      add_expense(category_name, amount, description)

      initial_budget = 1000                           # Declare the initial budget
      finance['Remaining budget'] = initial_budget - finance['Total expense']   # Calculate the remaining budget

      generate_pie_chart()     # Generate the graphs
      generate_cat()
      return render_template('index.html', finance=finance, error=None, expenses=expenses)   # pass to html

    except ValueError:
      error = 'Please enter a valid numeric amount.'

  return render_template('index.html', finance=finance, error=error, expenses=expenses)


if __name__ == '__main__':
  category_mapping = {  
    '1': 'Shopping',
    '2': 'Bills',
    '3': 'Eating out',
    '4': 'Groceries'
  }
  app.run(debug=True)


'''
When you enter the same description in the same category,
The description doesn't update in detail of the graph. (bar graph)
Eg. you submmited the spending of 'clothes' in the 'Shopping' twice like 30 and 50,
it only takes the first input. like clothes - 30
it doesn't combine into clothes-80 or changes into clothes-50

But it does update the pie chart correctly.

So you might have to input DIFFERENT DESCRIPTION each time you SUBMIT.
'''