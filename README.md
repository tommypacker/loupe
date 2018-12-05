# Loupe

Loupe is a tool that analyzes how accurate ESPN "Expert" fantasy football rankings really are. It takes an expert's rankings each week 
and compares them with the actual scoring leaders from that week. Afterwards, it calculates the normalized root mean square
errors for each analyst for each position and displays the results on a grouped bar chart.

## Background

Every week, ESPN fantasy "experts" make predictions about how well players will do - these predictions are then published in ESPN's weekly rankings page. However, often times these rankings are quite wrong, so I decided to look closer at how wrong each analyst is.

## Methodology

To find a metric that would somehow rank how each analyst does, I decided to use the root mean square deviation [(RMSD)](https://en.wikipedia.org/wiki/Root-mean-square_deviation) between analyst weekly rankings versus the actual position a player finishes for that week. The residuals of this metric will then tell us how far away from the actual rank an analyst's prediction is. The higher the residual, the worse a prediction is.

Sometimes a player that is not ranked ends up in the leaderboards for a given week, so to adjust for that, I replaced a null ranking with the worst ranking an analyst gives for that position, and add one to it. For example, each analyst only ranks the top 25 QBs for a week, so if a player that was unranked ends up in the top 25, I set their predicted rank to 26.

## Reading the Charts

There are three statistics I display on my visual tool. The first is the RMSD calculated per week. I take the rankings for a given week and compare it against the final leaderboard for that week. The second is the average RMSD overall the whole season. This guages how well an analyst has been doing for the course of the season. The final statistic sums up the errors over all positions over the whole season to see which analyst has done the best thus far.

## Running Locally

Coming soon.
