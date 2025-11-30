[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=21886248)
# Lab 11 - Grocery Store Simulation

In this lab, we will look at using Simpy to create a simple simulation of customers shopping in a grocery store. We are interested in seeing how log they have to wait to checkout based on how many checkers are working.

### Install Simpy in your Code Space terminal
```
pip install simpy
```

### Imports and setup
There are a number of things we need to setup as global variables or other packages we need to import.
Import
- Simpy: Supplies the simulation environment
- Random: Shoppers will need a random number of items
Global variables
- eventLog: List of all the info for the simulation
- waitingShoppers: List of shoppers who are done shopping and waiting on a checker.
- idleTime: Cumulative time the checkers are not busy across all checkers.

```
import simpy
import random
eventLog = []
waitingShoppers = []
idleTime = 0
```

### Creating a shopper
Each shopper will arrive and record their arrival time. Then they will randomly be assigned a number of items to go shopping for. Finally, once they are done shopping they will again record the time and add themselves to the queue of people waiting to checkout.

Assumptions:
- How many items will they need?
  - Is a truly random number useful for this or should it be weighted?
- How long does it take to shop given a number of items?
  - Should there be some random fluctuation to the shopping time?

The shopper info is stored as a tuple and added to the waitingCustomers list at the end.

```
def shopper(env, id):
    arrive = env.now
    items = random.randint(5, 20)
    shoppingTime = items // 2 # shopping takes 1/2 a minute per item.
    yield env.timeout(shoppingTime)
    # join the queue of waiting shoppers
    waitingShoppers.append((id, items, arrive, env.now))
```

### Creating a checker
Once the shoppers are added to the queue then the checker will pick them up. The checker will look to see if there are people waiting and if so, will begin to checkout their items.
If there are no people waiting, the checker will wait a minute of idle time and check again.

Assumptions:
- A checker can ring up 10 items a minute.
- All transactions take at least 1 minute.
- Checkers will take the first person waiting in the overall customer queue.

After the customer is all checked out, the final stats will be logged to the event log with the final time included.

```
def checker(env):
    global idleTime
    while True:
        while len(waitingShoppers) == 0:
            idleTime += 1
            yield env.timeout(1) # wait a minute and check again

        customer = waitingShoppers.pop(0)
        items = customer[1]
        checkoutTime = items // 10 + 1
        yield env.timeout(checkoutTime)

        eventLog.append((customer[0], customer[1], customer[2], customer[3], env.now))
```

### Controlling customer arrival
We need a process that doles out the new customers. This is a continuous process whereas the individual shoppers are created and end as processes once they are done shopping.

Assumptions:
- How frequently do new shoppers arrive?
- Do shoppers arrive at a steady rate or should we figure out how to surge and lull?
```
def customerArrival(env):
    customerNumber = 0
    while True:
        customerNumber += 1
        env.process(shopper(env, customerNumber))
        yield env.timeout(2) #New shopper every two minutes
```

### Processing the results
Once the simulation is done running, we will want to look at any relevant data. There are some obvious things to look at like the average wait time for the shoppers and the idle time for the checkers.
Data we might look at:
- Number of shoppers
- Average items purchased
- Total idle time
- Average wait time
- Average shopping time
- Max wait time

```
def processResults():
    totalWait = 0
    totalShoppers = 0

    for e in eventLog:
        waitTime = e[4] - e[3] #depart time - done shopping time
        totalWait += waitTime
        totalShoppers += 1

    avgWait = totalWait / totalShoppers

    print("The average wait time was %.2f minutes." % avgWait)
    print("The total idle time was %d minutes" % idleTime)
```

### Main method
The main method is the function that does the setup for the simpy environment and also begins the processes.

Options:
- How many checkers do we want?
- How long will the simulation run?
- Does the simulation breakdown over time?

```
def main():
    numberCheckers = 5

    env = simpy.Environment()

    env.process(customerArrival(env))
    for i in range(numberCheckers):
        env.process(checker(env))

    env.run(until=180 )
    print(len(waitingShoppers))
    processResults()

if __name__ == '__main__':
    main()
```

### For you to do:
- Get the simulation working.
- Test the simulation with different values.
- Process some other data than average wait time.
- Write a short summary of what you learned from the simulation.
  - Include the summary as a different document in your repo.

## End of class
- Add a commit message
- Commit to GitHub
- Sync work with Repo
- Submit your repo link to Canvas
