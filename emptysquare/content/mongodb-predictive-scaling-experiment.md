+++
category = ["MongoDB", "Research"]
description = "At MongoDB, we experimented to see if we could predict each DBaaS customer's demand fluctuations, and auto-scale them using this foreknowledge."
draft = true
enable_lightbox = true
tag = ["distributedsystems"]
title = "Predictive Scaling in MongoDB Atlas, an Experiment"
type = "post"
+++

At MongoDB, we experimented to see if we could predict each DBaaS customer's demand fluctuations, and auto-scale them using this foreknowledge. Senior Data Scientist Matthieu Humeau and I spoke about this experiment at [Data Council](https://www.datacouncil.ai/austin) and [NYC Systems](https://nycsystems.xyz/october-2024.html). Here's the video from NYC Systems, and a written version is below. 

<iframe width="560" height="315" src="https://www.youtube.com/embed/VLi9MHnBJzQ?si=RPxsPt1SjPNX8tkM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

***

# Replica Sets

MongoDB is generally deployed as a group of servers, where one is the primary and at least two are secondaries. The client sends all writes to the primary, and the secondaries replicate those writes, usually within milliseconds. The client can read from the primary or the secondaries. So secondaries can take some of the query load, and they're hot standbys. If the primary fails, a secondary automatically becomes primary within a few seconds, with zero data loss.

![A drawing of three servers. One is primary, the others are secondaries. Replication goes from the primary to the secondaries. A MongoClient reads and writes at the primary and also reads from the secondaries.](replica-set.png)
<figcaption><h4>MongoDB replica set.</h4></figcaption>

# Atlas

MongoDB is free and open source, you can download it and deploy a replica set yourself, and lots of people do. But these days people mostly use our cloud service, [MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-database). Atlas started out as a database-as-a-service. Now we call it a Developer Data Platform because it offers a lot more than a database; we have triggers and events and streaming analysis and edge computing and vector search. But this experiment focuses on the DBaaS.

The DBaaS is multi-region&mdash;customers can spread their data around the world or locate it close to their users&mdash;and it's multi-cloud, it runs on AWS, GCP, and Azure. A customer can even deploy a replica set that includes servers in multiple clouds at once.

MongoDB's cloud is actually Amazon's, Microsoft's, or Google's cloud.

![A flowchart. At the top a customer sends three dollars to MongoDB, which sends two dollars to Amazon, Google, and Microsoft.](business-model.png)
<figcaption><h4>MongoDB's secret business model (not drawn to scale).</h4></figcaption>

Atlas customers decide how many MongoDB servers to deploy in Atlas, what clouds to deploy them in, and what size of server: how many CPUs, how much RAM, and so on. Each server in a replica set must use the same tier. ([With exceptions](https://www.mongodb.com/blog/post/introducing-ability-independently-scale-atlas-analytics-node-tiers).) We charge customers according to their choices: how many servers, what size, and how many hours they're running. Of course, most of the money we charge our customers, we then pay to the underlying cloud providers. Those providers charge **us** according to the number and size of servers and how long they're running. If we could save money by anticipating each customer's needs and perfectly scaling their server sizes up and down, according to their changing demands, that would save our customers money and reduce our carbon emissions.

<table class="table table-striped table-bordered">
<thead>
<tr>
<th>Tier</th>
<th style="text-align:right">Storage</th>
<th style="text-align:right">RAM</th>
<th style="text-align:right">vCPUs</th>
<th style="text-align:right">Base Price</th>
</tr>
</thead>
<tbody>
<tr>
<td>M10</td>
<td style="text-align:right">10 GB</td>
<td style="text-align:right">2 GB</td>
<td style="text-align:right">2 vCPUs</td>
<td style="text-align:right">$0.08/hr</td>
</tr>
<tr>
<td>M20</td>
<td style="text-align:right">20 GB</td>
<td style="text-align:right">4 GB</td>
<td style="text-align:right">2 vCPUs</td>
<td style="text-align:right">$0.20/hr</td>
</tr>
<tr>
<td>M30</td>
<td style="text-align:right">40 GB</td>
<td style="text-align:right">8 GB</td>
<td style="text-align:right">2 vCPUs</td>
<td style="text-align:right">$0.54/hr</td>
</tr>
<tr>
<td>M40</td>
<td style="text-align:right">80 GB</td>
<td style="text-align:right">16 GB</td>
<td style="text-align:right">4 vCPUs</td>
<td style="text-align:right">$1.04/hr</td>
</tr>
<tr>
<td>M50</td>
<td style="text-align:right">160 GB</td>
<td style="text-align:right">32 GB</td>
<td style="text-align:right">8 vCPUs</td>
<td style="text-align:right">$2.00/hr</td>
</tr>
<tr>
<td>M60</td>
<td style="text-align:right">320 GB</td>
<td style="text-align:right">64 GB</td>
<td style="text-align:right">16 vCPUs</td>
<td style="text-align:right">$3.95/hr</td>
</tr>
<tr>
<td>M80</td>
<td style="text-align:right">750 GB</td>
<td style="text-align:right">128 GB</td>
<td style="text-align:right">32 vCPUs</td>
<td style="text-align:right">$7.30/hr</td>
</tr>
<tr>
<td>M140</td>
<td style="text-align:right">1000 GB</td>
<td style="text-align:right">192 GB</td>
<td style="text-align:right">48 vCPUs</td>
<td style="text-align:right">$10.99/hr</td>
</tr>
<tr>
<td>M200</td>
<td style="text-align:right">1500 GB</td>
<td style="text-align:right">256 GB</td>
<td style="text-align:right">64 vCPUs</td>
<td style="text-align:right">$14.59/hr</td>
</tr>
<tr>
<td>M300</td>
<td style="text-align:right">2000 GB</td>
<td style="text-align:right">384 GB</td>
<td style="text-align:right">96 vCPUs</td>
<td style="text-align:right">$21.85/hr</td>
</tr>
<tr>
<td>M400</td>
<td style="text-align:right">3000 GB</td>
<td style="text-align:right">488 GB</td>
<td style="text-align:right">64 vCPUs</td>
<td style="text-align:right">$22.40/hr</td>
</tr>
<tr>
<td>M700</td>
<td style="text-align:right">4000 GB</td>
<td style="text-align:right">768 GB</td>
<td style="text-align:right">96 vCPUs</td>
<td style="text-align:right">$33.26/hr</td>
</tr>
</tbody>
</table>
<figcaption><h4>MongoDB Atlas-on-AWS pricing</h4></figcaption>

We sell MongoDB server sizes as a set of "tiers", those are named like M10, M20, and so on, on the left. Those map to specific instance sizes in the cloud provider, so an M10 is a certain size of AWS server, and we charge [a certain price on AWS](https://www.mongodb.com/pricing). If the customer chooses to deploy their M10 on Azure or GCP then the size and price will be slightly different.

# Manually-Triggered Scaling

A customer can change their server size with zero downtime. Here's the process:

<div style="display: flex">
<div style="flex: 1; padding-right: 1em">

* The customer clicks a button or executes an API call to resize their servers to a chosen tier.
* Atlas chooses a secondary and takes it offline,
* detaches its network storage,
* restarts it with a different server size,
* reattaches the storage,
* and waits for it to catch up to the primary, by replaying all the writes it missed while it was down.
* Atlas scale the other secondary likewise.
* Atlas tells the primary to become a secondary and [hand off its responsibilities to another server](https://www.mongodb.com/docs/manual/reference/method/rs.stepDown/#election-handoff).
* Atlas scales the former primary.

</div>
<div style="flex: 1">

![Black and white photo of 1940s-era climber ascending a vertical rock wall](gaston-rebuffat.jpg)
<figcaption><h4><a href="https://www.flickr.com/photos/nordique/4889485440">Gaston Rebuffat.</a></h4></figcaption>

</div>
</div>

The whole process takes about 15 minutes, and the customer can read and write their data normally throughout. Usually the customer's application doesn't even notice the scaling operation, except that once scaling is complete, performance is faster or slower, and the price is different.

# Atlas Autoscaling Today

![Yellowed old patent diagram of a two-man vehicle, steered by the man in front and hand-cranked by the man behind](bolton-machine.png)
<figcaption><h4><a href="https://publicdomainreview.org/collection/cycling-art/">Today's state of the art.</a></h4></figcaption>

Atlas customers can opt in to autoscaling, but today's autoscaling is **infrequent** and **reactive**. The rules are:

- scale up by one tier after 1 hour of overload,
- scale down by one tier after 4 hours of underload.

Overload is defined as over 75% CPU or RAM utilization, and underload is less than 50% of either. ([Details here](https://www.mongodb.com/docs/atlas/cluster-autoscaling/).) Atlas only scales between adjacent tiers, e.g. if an M60 replica set is underloaded, Atlas will scale it down to M50, but not directly to any tier smaller than that. If the customer's demand changes dramatically, it takes several scaling operations to reach the optimum server size. This means servers can be overloaded or underloaded for long periods! An underloaded server is a waste of money. An overloaded server is bad for performance, and if it's really slammed it could interfere with the scaling operation itself. So Matthieu and I envisioned...

# The Ideal Future

![Yellowed old patent diagram of a human-powered flying machine with feathered wings and tail.](flying-machine.png)
<figcaption><h4><a href="https://publicdomainreview.org/collection/cycling-art/">The prototype.</a></h4></figcaption>

In the ideal future, we would forecast each replica set's resource needs. We could scale a replica set up just before it's overloaded, and scale it down as soon as it's underloaded. We would scale it directly to the right server size, skipping intermediate tiers. We'd always use the cheapest size that could meet the customer's demand.

![Hand-drawn chart, a smooth line labeled "demand" fluctuates up and down, a rectilinear line labeled "capacity" goes up and down in sharp steps, always a bit above the demand line](predictive-scaling-drawing.png)

# Predictive Scaling Experiment

Matthieu and I performed on experiment over the last year to see if predictive scaling was possible in the MongoDB Atlas DBaaS. 

The experiment was possible because Atlas keeps servers' performance metrics in a data warehouse. We have a couple of years of data about all servers' CPU and memory utilization, the numbers of queries per second, inserts per second, etc., all at one-minute intervals. Atlas has about 170,000 replica sets now, each with at least three servers, so it's a stout data set. We chose 10,000 replica sets where customers had opted in to the existing reactive auto-scaler, and we analyzed their 2023 history. We split the history into a training period and a testing period, as usual with machine learning, and trained models to forecast the clusters' demand and CPU utilization. (CPU is the simplest and most important metric; eventually we'll forecast RAM, disk I/O, and so on.) Once we'd prototyped this predictive scaler, we estimated how it would've performed during testing period, compared to the reactive scaler that was running at that time.

The prototype had three components:

- **Forecaster:** tries to predict each cluster's future workload.
- **Estimator:** estimates CPU% for any workload, any instance size.
- **Planner:** chooses cheapest instance that satisfies forecasted demand.

![Diagram of components, explained below](predictive-scaler-components.png)

For each replica set, its history is an input to the Short-Term and Long-Term Forecasters. (I'll explain why we have two Forecasters soon.) The Forecasters must be retrained every few minutes, as new samples arrive.

From the same data warehouse we sampled 25 million points in time from any replica set in Atlas. Each of these samples includes a count of operations per second (queries, inserts, updates, etc.), an instance size, and the CPU utilization at that moment. We used this to train the Estimator, which can predict the CPU utilization for any amount of customer demand and any instance size. This is a hard problem, since we can't see our customers' queries or their data, but we did our best. The Estimator must be retrained rarely, when there's new hardware available, or a more efficient version of the MongoDB software. (Eventually we plan to train an Estimator for each MongoDB version.)

The Forecasters and Estimator cooperate to predict each replica set's future CPU on any instance size available. E.g., they might predict that 20 minutes in the future, some replica set will use 90% CPU if it's on M40 servers, and 60% CPU if it's on more powerful M50 servers. 

## Predictive Scaling: Planner

Let's look at the Planner in more detail. Here's a forecasted workload, it's forecasted to rise and then fall.

![A hand-drawn chart, CPU versus time. A line labeled "M40 estimate" rises above 75% CPU, then falls. A line labeled "M50" rises and falls but never rises above 75% CPU. A line labeled "plan" follows the M40 line except where it would cross 75% CPU. There, it follows the M50 line.](forecasted-workload.png)

So the Planner's plan is to use M40 servers until it would be overloaded, then switch to M50 during the peak, then switch back. Notice the replica set should start scaling up 15 minutes **before** the overload arrives, so the scale-up is complete in time to avoid overload. It starts scaling down as soon as the risk of overload has passed.

## Predictive Scaling: Long-Term Forecaster

Our goal is to forecast a customer's CPU utilization, but we can't just train a model based on recent fluctuations of CPU, because that would create a circular dependency: if we predict a CPU spike and scale accordingly, we eliminate the spike, invalidating the forecast. Instead we forecast metrics unaffected by scaling, which we call "customer-driven metrics", e.g. queries per second, number of client connections, and database sizes. We assume these are **independent** of instance size or scaling actions. (Sometimes this is false; a saturated server exerts backpressure on the customer's queries. But customer-driven metrics are normally exogenous.)

![A chart showing queries per second over several weeks. There are obvious weekly patterns, where weekdays have peaks and weekends don't, and obvious daily spikes each weekday.](seasonal.png)

Our forecasting model, MSTL (multi-seasonal trend decomposition using LOESS), extracts components from the time series for each customer-driven metric for an individual replica set. It separates long-term trends (e.g., this replica set's query load is steadily growing) and "seasonal" components (daily and weekly) while isolating residuals. We handle these residuals with a simple autoregressive model from the ARIMA family.

![A chart showing an observed history of demand fluctuating over several weeks. Beneath it is a smooth line labeled "trend", then a periodic wavy line labeled "daily", a line with longer waves labeled "weekly", and a semi-random-looking line labeled "residuals".](MSTL.png)
<figcaption><h4>MSTL (multi-seasonal trend decomposition using LOESS)</h4></figcaption>

By combining these components, we forecast each metric separately, creating a "Long-Term Forecaster" for each. Despite the name, the Long-Term Forecaster doesn't project far into the future; it's trained on several weeks of data to capture patterns, then predicts a few hours ahead.

![Three pie charts: 3% of servers have strong hourly seasonality and 5% have weak hourly seasonality. 24% of servers have strong daily seasonality and 32% have weak daily seasonality. 7% of servers have strong weekly seasonality and 17% have weak weekly seasonality.](percent-seasonal.png)
<figcaption><h4>How often is demand seasonal?</h4></figcaption>

Most Atlas replica sets have daily seasonality. About 25% have weekly seasonality. Generally if a replica set has weekly seasonality it **also** has daily seasonality. Hourly seasonality is rare, and anyway it isn't helpful for planning a scaling operation that takes a quarter-hour. Replica sets with sufficient daily/weekly seasonality are predictable by the Long-Term Forecaster.

![A chart of queries per second over time, the same as shown earlier. In the final day of the chart is a line representing actual history, and a closely-matching green line labeled "forecast".](example-forecast.png)
<figcaption><h4>Example "long-term" forecast.</h4></figcaption>

But only some replica sets have seasonality! For non-seasonal clusters, the Long-Term Forecaster's prediction of customer-driven metrics is unusable.

<table class="table table-striped table-bordered">
  <thead>
    <tr>
      <th></th>
      <th>Seasonal Clusters</th>
      <th>Non-seasonal Clusters</th>
    </tr>
  </thead>
  <tr>
    <td>Connections</td>
    <td>3%</td>
    <td><span style="color:red">50%</span></td>
  </tr>
  <tr>
    <td>Query Rate</td>
    <td>19%</td>
    <td><span style="color:red">71%</span></td>
  </tr>
  <tr>
    <td>Scanned objects Rate</td>
    <td>27%</td>
    <td><span style="color:red">186%</span></td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td><span style="color:red; font-weight: bold">&uparrow; unusable</span></td>
  </tr>
</table>

So we added a "self-censoring" mechanism to our prototype: the Long-Term Forecaster scores its own confidence based on its recent accuracy, and only trusts its prediction if its recent error has been small. 

## Predictive Scaling: Short-Term Forecaster

What can we do when the Long-Term Forecaster isn't trustworthy? We didn't want to fall back to purely-reactive scaling; we can still do better than that. We prototyped a "Short-Term Forecaster": this model uses only the last hour or two of data and does trend interpolation. We compared this to a naïve baseline Forecaster, which assumes the future will look like the last observation, and found that trend interpolation beats the baseline 68% of the time (29% reduction in error).

![A chart with a spiky and semi-random-looking line labeled "query executor scanned objects per second". In the final day of the chart, there are flat green lines labeled "baseline", which show a forecast that assumes each measurement will remain the same for two hours. Angled red lines labeled "forecast" assume the current trend will continue for two hours, these are a closer match to reality than the baseline forecast.](short-term-forecaster.png)
<figcaption><h4>Approximation of local trends for near future forecast.</h4></figcaption>

## Predictive Scaling: Estimator

The Forecasters predict customer demand, but we still need to know whether CPU utilization will be within the target range (50-75%). That's the Estimator's job. The Estimator takes the forecasted demand and an instance size (defined by CPU and memory), and outputs projected CPU. Using a regression model based on boosted decision trees trained on millions of samples, we've achieved fairly accurate results. For around 45% of clusters, our error rate is under 7%, allowing us to make precise scaling decisions. For another 42%, the model is somewhat less accurate but useful in extreme cases. We exclude the remaining 13% of clusters with higher error rates from predictive scaling.

![A chart with four inputs on the left and the output on the right. The four inputs are charts of metrics over time: connections created per second, queries per second, documents updated per second, and scanned objects per second. The output is a line labeled "historical CPU", and a closely-matching line labeled "estimator prediction".](estimator-example.png)
<figcaption><h4>Example of input and output of Estimator.</h4></figcaption>

## Predictive Scaling: Putting It All Together

With both forecasts and CPU estimates, the Planner can choose the cheapest instance size that we guess can handle the next 15 minutes of customer demand without exceeding 75% CPU. Our experiment showed that this predictive scaler, compared to the reactive scaler in use during the test period, would've stayed closer to the CPU target and reduced over- and under-utilization. For the average replica set it saved 9 cents an hour. That translates to millions of dollars a year if the predictive scaler were enabled for all Atlas users.

<table class="table table-striped table-bordered">
    <thead>
        <tr>
            <th></th>
            <th>Predictive auto-scaler</th>
            <th>Reactive auto-scaler</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Average distance from 75% CPU target</td>
            <td style="background-color: #e0f2e0">18.6%</td>
            <td>32.1%</td>
        </tr>
        <tr>
            <td>Average under-utilization</td>
            <td style="background-color: #e0f2e0">18.3%</td>
            <td>28.3%</td>
        </tr>
        <tr>
            <td>Average over-utilization</td>
            <td style="background-color: #e0f2e0">0.4%</td>
            <td>3.8%</td>
        </tr>
    </tbody>
</table>

What's next? Matthieu and other MongoDB people are improving the Estimator's accuracy by adding more customer-driven metrics, and estimating more hardware metrics: not just CPU, but also memory, and perhaps co-modeling CPU and memory to capture interactions between them. We want to investigate the minority of customers with bad estimates and ensure the Estimator works for them too. We'll try building specialized Estimators for each cloud provider and each MongoDB version. MongoDB can't see our customers' data or queries, but we can gather statistics on [query shapes](https://www.mongodb.com/docs/upcoming/core/query-shapes/)&mdash;maybe we could use this to improve estimation.

I can't tell you a release date. Par for a public blog post, but still disappointing, I know. In this case we honestly need more experiments before we can plan a release. A private beta for a few customers will come soon. Before we can unleash a complex algorithm on our customers' replica sets we need a lot more confidence in its accuracy, and a lot of safeguards. We'll always need the reactive auto-scaler to handle unexpected changes in demand. But I'm excited at the prospect of eventually saving a ton of money and electricity with precise and proactive auto-scaling.

![A yellowed patent diagram from 1830 showing a large bicycle. One man standing upright is propelling the contraption with foot pedals and holds a two-handed crank labeled "steering wheel". A man behind him lies prone and appears to use only his feet. Both wear tophats.](propelling-carriage.png)
<figcaption><h4>Predictive and reactive auto-scalers, cooperating.</h4></figcaption>

***

Further reading:
* [This work was heavily inspired by Rebecca Taft's PhD thesis](/e-store-and-p-store/)
* Also interesting: [Is Machine Learning Necessary for Cloud Resource Usage Forecasting?](https://christofidi.github.io/docs/2023_SoCC_Presentation.pdf), ACM Symposium on Cloud Computing 2023. 
* [MongoDB Atlas](https://mongodb.com/atlas).
* Cycling images from [Public Domain Review](https://publicdomainreview.org/collection/cycling-art/).
