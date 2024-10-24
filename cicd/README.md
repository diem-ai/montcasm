# Monte Carlo Simulation on Historical Backtesting
- An investment may make sense if we expect it to return more money than it costs. But returns are only part of the story because they are risky - there may be a range of possible outcomes. 
- How to capture unpredictable events which are happened in the past could happen in the future ? How to find out and be well-prepared for upcomming black swans events in the investment and finance markets ? 
- The project aims to run the backtesting simulation on 20 years financial historical data on HPC to evaluate investment risk of porfolio of 50 assets. </br>
    ![](/images/AAPL_1640262084.7378035.png)
# Project Description
In this project, Monte Carlo Simulation is used to evaluate the risk and return value of investment porfolio of 50 ETFs. First step is to collect historical financial data in 20 years available on [fmpcloud](https://fmpcloud.io/api/v3/historical-price-full). Next step is to forecast future prices with Brownian Emotion. This step is repeated n times with a hope that the more we run, the better outcome we get according to The [Law of Large Number](https://en.wikipedia.org/wiki/Law_of_large_numbers) . We chose the best model which has the least standard deviation error.
# Project Structure
## Data Collection
20 years of historial timeseries data is collected from [fmpcloud](https://fmpcloud.io/api/v3/historical-price-full). This site provides a parameterized RESTFul API with 255 free requests. The return object is an array of JSON which contains Close, Adjusted Close, High, Open, Volume of Price Exchange, Pricing Date. 
## Data Processing
We extract only Close price and price date from raw dataset, convert Date from string to DateTime. The processed data is saved into csv files.

![](/images/dataset.PNG)

## Future Price Simulation with Geometric Brownian Motion
- ### The mathematical expression according to ([Making Sense of Monte Carlo](https://corpgov.law.harvard.edu/2019/08/18/making-sense-of-monte-carlo/)):
    ![](/images/monte.webp)

    - The definitions for each of the variables in this formula are
        - ST: Simulated future stock price at the time T.
        - S0: Beginning stock price at the time T0
        - e: The mathematical constant e (~2.72, i.e., the base of the natural logarithm).
        - Rf: The risk-free interest rate based on zero-coupon U.S. Treasuries (the “drift”).
        - d: The dividend yield (if applicable). In this case, we work on Close price only and dividend=0.
        - σ: Annual volatility.
        - T: The term of the award, from the grant date to the end of the applicable period.
        - Z: Normally distributed random variable (Z-score); for simplicity, one can think of “Z” as a random number that changes for each simulation.
- ### Implementation
    - #### Calculate Asset's Return Values and normalise it with Logrithm
    ```python
    @jit(fastmath=True, forceobj=True)
    def f_log_return_value(np_price):
        """Calulate the return value of assets on stock market.
        returns = (price(t) - price(t-1))/price(t-1)
        """
        next_price = np_price[1:]
        # this step is like series.shift(1).iloc[1:]
        next_shift_price = np.append(np.NAN, np_price[:-1])[1:]
        return np.log(next_price/next_shift_price)    
    ```
    - #### Calculate Drift Rate
        - Drift rate is the risk-free interest rate which is calculated using the standard deviation to measure stock's volatility.
        ```python
        @jit(fastmath=True, forceobj=True)
         def f_get_drift_rate(np_returns):
            """
            Drift rate is the risk-free interest rate. 
            It is calculated using the standard deviation to measure stock's volatility.
            """
            return np.mean(np_returns) - np.var(np_returns)/2       
        ```
    - #### Predict future price with Geometric Brownian Motion
        ```python
        @jit(fastmath=True, forceobj=True)
        def f_forecast_price(np_returns, np_drift_rate, current_price):
            """
            Forecast the future prices with Geometric_Brownian_motion.
            The mathematical expression is taken from this article: https://corpgov.law.harvard.edu/2019/08/18/making-sense-of-monte-carlo/
            """
            # Calculate normally distributed random variable
            zscore =  rd.gauss(0,1)   
            # Calculate stochastic differential equation (SDE)
            np_sde = np_drift_rate + ( np.std(np_returns) * zscore )
            # Calculate simulated future stock price in the the future.
            simulated_price = current_price * np.exp(np_sde)
            return simulated_price
        ```
    - #### Monte Carlo Simulation
        - We construct a model to get mean and variance of its residual (return). 
        - We forcast the future price using Geometric Brownian Motion (GBM) with drift rate.
        - We calculate the output of MC Simulation using GBM with drift rate and determine the best fit along with its standard deviation error.
        - The pseudo random number is generated via empirical distribution.
        - We run this simulations as n times. The more , the better according to the [Law of Large Number](https://en.wikipedia.org/wiki/Law_of_large_numbers)
        - We pick the forecast that has the least standard deviation against the original Close prices
        - we would check if the best forecast can predict the future direction (instead of actual price) and how well monte - carlo catches black swans
        ```python
        @jit(parallel=True, forceobj=True)
        def f_monte_carlo(np_price, simulation):
            prediction = {}
            for c_sim in prange(simulation):
                #we only care about close price, if there has been dividend issued, we use adjusted close price instead
                prediction[c_sim] = f_gbm_simulation(np_price)
            # Determine the best fitted simulation wit minimum standard deviation
            pickers = f_get_best_fit(simulation, prediction, np_price)
            return prediction, pickers
        ```
        ```python
        @jit(parallel=True, forceobj=True)
        def f_gbm_simulation(np_price):
            """
            Simulate the future prices with Geometric_Brownian_motion (https://en.wikipedia.org/wiki/Geometric_Brownian_motion)
            """
            np_returns = f_log_return_value(np_price)
            np_drift_rate = f_get_drift_rate(np_returns)

            prediction = []
            prediction.append(np_price[0])
            for idx in prange(len(np_price) - 1):
                simulated_price = f_forecast_price(np_returns, np_drift_rate, prediction[-1])
                prediction.append(simulated_price)
            return prediction
        ```
        ```python
        @jit(parallel=True, forceobj=True)
        def f_get_best_fit(simulation, prediction, np_price):
            """
            # we use simple criterias, the smallest standard deviation
            # we iterate through every simulation and compare it with actual data
            # The winner is the one with minimum standard deviation.
            """
            std = np.finfo(np.float64).max
            pickers = {}
            for c_sim in prange(simulation):
                temp = np.std(np.subtract(prediction[c_sim], np_price))
                if (std > temp):
                    std = temp
                    pickers = {c_sim: std}
            return pickers
        ```

## Run simulation on [MeluXina](https://docs.lxp.lu)
### Resource Allocations
- The simulation is run on [HPC MeluXina](https://docs.lxp.lu) with 1 CPU Node and 2 CPU Nodes. 
- It is scaled from 1 core to 128 cores in order to measure the performance benchmark. 
### Slurm Jobs
- In order to use the computing and memory resources on [HPC MeluXina](https://docs.lxp.lu), a [slurm job](https://slurm.schedmd.com/documentation.html) should be created and submitted to the queue before executing on MeluXina Cluster.
- Here are few examples of how to Slurm Job look like
    - [1 CPU Node](/jobs/1cpu.sh):
        ```bash
        #!/bin/bash -l
        #SBATCH --job-name="1cpu"
        #SBATCH -N 1
        #SBATCH --ntasks=1
        #SBATCH --cpus-per-task=128
        #SBATCH --output=cpu_scaling.%J.out
        #SBATCH --error=cpu_scaling.%J.err
        #SBATCH -p cpu
        #SBATCH -q default
        #SBATCH --time=48:00:00
        #SBATCH --constraint=cpuonly
        #SBATCH -A LXP
        ```
    - [2 CPU Nodes]((/jobs/2cpu.sh))
        ```bash
        #!/bin/bash -l
        #SBATCH --job-name="2cpu"
        #SBATCH -N 2
        #SBATCH --ntasks=2
        #SBATCH --cpus-per-task=128
        #SBATCH --output=2cpu.%J.out
        #SBATCH --error=2cpu.%J.err
        #SBATCH -p cpu
        #SBATCH -q default
        #SBATCH --time=48:00:00
        #SBATCH --constraint=cpuonly
        #SBATCH -A LXP
        ```
- To know more about how to write an efficient Slurm scripts and schedule them on our HPC, check out our website [Handling jobs](https://docs.lxp.lu/first-steps/handling_jobs/#submitting-batch-jobs)
### Slurm Job Optimization
- Submitting job to  [HPC MeluXina](https://docs.lxp.lu) is not the end but it is just a beginning. The job needs to be paralelled and vectorized to leverage the HPC power.
- In this project, we use [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) and [ProcessPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor) which are high-level interface task distribution to asynchonously schedule and execute tasks on seperated processes. In addition, we use [Numba](https://numba.pydata.org) to speed up Python code. [Numba](https://numba.pydata.org) provides [a number of compilation options](https://numba.readthedocs.io/en/stable/user/jit.html#compilation-options) to accelarate the computation. In this project, ``@jit(nopython=True, parallel=True)``and ``@jit(fastmath=True, forceobj=True)`` decorators are used to enable the automatic interations and vectorize mathematical calculations. Below are a few examples of how to apply [Numba](https://numba.pydata.org) decorators on the codes
    - Parallelization
        ```python
        @jit(parallel=True, forceobj=True)
        def f_get_best_fit(simulation, prediction, np_price):
            """
            # we use simple criterias, the smallest standard deviation
            # we iterate through every simulation and compare it with actual data
            # The winner is the one with minimum standard deviation.
            """
            std = np.finfo(np.float64).max
            pickers = {}
            for c_sim in prange(simulation):
                temp = np.std(np.subtract(prediction[c_sim], np_price))
                if (std > temp):
                    std = temp
                    pickers = {c_sim: std}
            return pickers
        ```
    - Vectorization
        ```python
        @jit(fastmath=True, forceobj=True)
        def f_log_return_value(np_price):
            """Calulate the return value of assets on stock market.
            returns = (price(t) - price(t-1))/price(t-1)
            """
            next_price = np_price[1:]
            # this step is like series.shift(1).iloc[1:]
            next_shift_price = np.append(np.NAN, np_price[:-1])[1:]
            return np.log(next_price/next_shift_price)
        ```
### Job Submit Automation (CI/CD)
<b> TBD </b>
## HPC Performance Report
- The difference betwen non-vectorization and vectorization on [HPC MeluXina](https://docs.lxp.lu) </br>

    ![](/images/vectorization.PNG)

- The difference betwen [1 CPU Node](/jobs/1cpu.sh) and [2 CPU Node](/jobs/2cpu.sh)  on [HPC MeluXina](https://docs.lxp.lu)</br>

    ![](/images/1cpu&2cpu.PNG)



## References
- [HPC MeluXina](https://docs.lxp.lu)
- [Making Sense of Monte Carlo](https://corpgov.law.harvard.edu/2019/08/18/making-sense-of-monte-carlo/)
- [Backtesting](https://www.investopedia.com/terms/b/backtesting.asp)
- [Law of Large Number](https://en.wikipedia.org/wiki/Law_of_large_numbers)
- [fmpcloud](https://fmpcloud.io/api/v3/historical-price-full)





