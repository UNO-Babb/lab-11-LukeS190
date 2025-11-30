#GroceryStoreSim.py
#Name:
#Date:
#Assignment:
# Lab 11 - Grocery Store Simulation
# Name:
# Date:
# Description: SimPy-based grocery store checkout simulation.

import simpy
import random

# ----- Global variables -----
eventLog = []          # (id, items, arriveTime, doneShoppingTime, departTime)
waitingShoppers = []   # (id, items, arriveTime, doneShoppingTime)
idleTime = 0           # cumulative idle minutes across all checkers


# ----- Shopper process -----
def shopper(env, id):
    """
    One shopper:
      - records arrival time
      - gets a random number of items
      - 'shops' for a while
      - then joins the checkout queue
    """
    arrive = env.now
    # Random number of items between 5 and 20
    items = random.randint(5, 20)

    # Shopping: 0.5 minute per item
    shoppingTime = items / 2.0
    yield env.timeout(shoppingTime)

    # join the queue of waiting shoppers
    waitingShoppers.append((id, items, arrive, env.now))


# ----- Checker process -----
def checker(env):
    """
    A checker repeatedly:
      - waits if no customers
      - takes first waiting customer
      - checks them out
      - logs event
    """
    global idleTime

    while True:
        # If no shoppers, checker is idle for 1 minute at a time
        while len(waitingShoppers) == 0:
            idleTime += 1
            yield env.timeout(1)

        # Take the first shopper in the queue (FIFO)
        customer = waitingShoppers.pop(0)
        cid, items, arrive, doneShopping = customer

        # Checker can ring up 10 items per minute, minimum 1 minute
        checkoutTime = items / 10.0
        if checkoutTime < 1:
            checkoutTime = 1
        yield env.timeout(checkoutTime)

        # Log: (id, items, arriveTime, doneShoppingTime, departTime)
        eventLog.append((cid, items, arrive, doneShopping, env.now))


# ----- Customer arrival process -----
def customerArrival(env, arrival_interval=2):
    """
    Creates shoppers forever at a fixed interval.
    arrival_interval: minutes between shopper arrivals.
    """
    customerNumber = 0
    while True:
        customerNumber += 1
        env.process(shopper(env, customerNumber))
        yield env.timeout(arrival_interval)  # New shopper every X minutes


# ----- Results processing -----
def processResults():
    """
    Process the eventLog and print:
      - number of shoppers
      - average items purchased
      - total idle time
      - average wait time
      - average shopping time
      - max wait time
      - average total time in system
    """
    if not eventLog:
        print("No customers were fully processed.")
        return

    totalWait = 0.0
    totalShopping = 0.0
    totalItems = 0
    totalShoppers = 0
    maxWait = 0.0
    totalSystemTime = 0.0  # from arrival to departure

    for e in eventLog:
        cid, items, arrive, doneShopping, depart = e

        waitTime = depart - doneShopping            # time in checkout line
        shoppingTime = doneShopping - arrive        # time spent shopping
        systemTime = depart - arrive                # total time in system

        totalWait += waitTime
        totalShopping += shoppingTime
        totalItems += items
        totalSystemTime += systemTime
        totalShoppers += 1

        if waitTime > maxWait:
            maxWait = waitTime

    avgWait = totalWait / totalShoppers
    avgShopping = totalShopping / totalShoppers
    avgItems = totalItems / totalShoppers
    avgSystemTime = totalSystemTime / totalShoppers

    print("----- Simulation Results -----")
    print(f"Total shoppers processed: {totalShoppers}")
    print(f"Average items purchased: {avgItems:.2f}")
    print(f"Average shopping time: {avgShopping:.2f} minutes")
    print(f"Average wait time (checkout line): {avgWait:.2f} minutes")
    print(f"Max wait time: {maxWait:.2f} minutes")
    print(f"Average total time in system: {avgSystemTime:.2f} minutes")
    print(f"Total checker idle time: {idleTime:.0f} minutes")


# ----- Main -----
def main():
    # You can change these to test different scenarios
    numberCheckers = 5       # how many checkers
    simDuration = 180        # how long to run the simulation (minutes)
    arrivalInterval = 2      # minutes between new customers

    env = simpy.Environment()

    # Start customer arrival process
    env.process(customerArrival(env, arrival_interval=arrivalInterval))

    # Start checker processes
    for i in range(numberCheckers):
        env.process(checker(env))

    # Run the simulation
    env.run(until=simDuration)

    # How many shoppers are still waiting when the sim stops
    print(f"Shoppers still waiting at end of sim: {len(waitingShoppers)}")

    # Process results
    processResults()


if __name__ == '__main__':
    main()
