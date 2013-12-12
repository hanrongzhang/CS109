#Media Bias in the 2012 Presidential Election: Did the Media Really Help Obama Win?</h1>
###CS109 Final Project: Ben Zauzmer, Daniel Taylor, Jonathan Marks, and Michael Suo</h3>

---

###Background
After President Barack Obama was reelected on November 6, 2012, it took Fox News just one day to publish an article titled <a href="http://www.foxnews.com/opinion/2012/11/07/five-ways-mainstream-media-tipped-scales-in-favor-obama/">"Five ways the mainstream media tipped the scales in favor of Obama."</a> The left was just as blunt, such as Salon's article two months later, <a href="http://www.salon.com/2013/01/05/12_most_despicable_things_fox_news_did_in_2012/">"12 most despicable things Fox News did in 2012."</a>

Both sides in this debate are correct that a functioning democracy relies heavily on a fair and free press during elections, so it is important to use the data from 2012 to answer a few key questions: How does Presidential election coverage among major media outlets? Which ones print articles that are the most positive for one candidate or the other, or the most supportive, or the most subjective? Is there a distincitive style of writing associated with an individual newspaper?

###Methods
We gathered 2011-2012 article data from many major news sources. Specifically, we used APIs from the New York Times, USA Today, The Guardian, and Bing. We wrote web scrapers to gather data from the Wall Street Journal, the New York Daily News, Boston Globe, the Washington Post, and the Los Angeles Times. We then cleaned the data so that all of the articles from different sources could be standardized and combined into one dataframe containing over 30,000 rows.

We wrote a script to determine which, if either, of the two candidates (Obama or Romney) the article related to. We also used both pre-written sentiment databases and manual sentiment training to determine the probability that each article is positive for the candidate it relates to, that it supports that candidate, and how subjective or objective it is.

Next, we cross-validated our data to choose the optimum of 240 combinations, looping through different scoring methods, vectorizers, n-grams, min_dfs, and alphas. After intial cross validation, we redefined the parameter search space to more accurately encompass the peak scores and reperformed cross validation.

Finally, we visualized our data set in a variety of ways to determine what insights we could find about 2012 election coverage. We graphed article counts by source, candidate, and date. We graphed the frequencies of word count, abstract length, and headline length. We graphed our sentiment analysis results by source, candidate, and date. We also used contour plots and clustering to examine how closely related articles from the same source are to each other.

###Results
Contrary to the hyperbolic claims of media bias following the 2012 election, we found a surprising lack of difference in the positivity and support of candidates across different newspapers and across time. While some metrics, most notably media subjectivity, did increase as the election came closer, there does not appear to be a consistent bias for or against either candidate within the news media as a whole. Similarly, there is not a significant relationship between polling results for each candidate and the media's portrayal of that candidate. This suggests the media did not, at least in a way noticable by our tests, tip the scales in favor of Barack Obama.

###Conculusions
There are two ways to explain these findings. The more cynical one is that newspapers want to make coverage more exciting as the election approaches to sell more papers, so they become more subjective over time. A more realistic justification is that there is simply more election coverage as the big day approaches - the objectives coverage is still the same, so most of the additional coverage is filled with subjective pieces.

In summary, the outpouring of media coverage concerning media bias and the effect that differential coverage had on the election's results seems to be overblown. While one can easily point at particularly devisive or slanted pieces, looking at newspaper coverage as a whole there does not seem to be a large difference between the media's coverage of Barack Obama or Mitt Romney.