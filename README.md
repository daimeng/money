# ATM simulation

## Directory structure
+ `bank` is the flask server simulating a bank.
  + `bank/bank` contains the code.
    + `bank/bank/api` contains controllers for auth flow, for withdraw/deposit, and querying data.
    + `bank/bank/models` contains the database models.
  + `bank/tests` contains some api tests.

+ `atm` is the atm console.
  + `atm/atm` contains the code.
  + `atm/tests` contains some unit tests and e2e tests.

## Setup
Start up processes

`docker-compose up`

Load money into the ATM and initial data into the the bank.

`./bootstrap.sh`

Start ATM console.

`./run_atm.sh`

Run unit and smoke tests

`./test.sh`

Run e2e tests. These will clear existing state.

`./test_e2e.sh`
