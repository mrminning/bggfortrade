# BGG for trade

A small program that searches BoardGameGeek.com for games marked "For Trade" and matches with games on your list
"Want In Trade". 


## Install
Install python3.12-venv libxml2-dev libxslt-dev

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run tests

```bash
# In active venv
pytest
```

## Create .env file
```
country=<country to search>
city=<city>,<another city>,<yet another city>
user=<bgg username>
show=<true or false. If true, will print all found users games marked for trade>  
```

## Run program
```bash
# Start venv if not already running 
source venv/bin/activate

# Run program with --env flag if a .env file was created
python main.py --env
```
