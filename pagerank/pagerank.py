import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Set of all pages the current page links to
    pageLinks = corpus[page]

    # List holding all page names
    pageNames = list(corpus.keys())

    # Holds each page as a key and their random rates of being chosen as values, will be returned
    pageChosenRates = {}

    # If the current page does not link to any other page, every other page has an equal chance of being chosen
    if len(pageLinks) < 1:

        # Fills chosen rates dict with every page having an equal value of being chosen
        for pageName in pageNames:
            pageChosenRates[pageName] = 1 / len(corpus)
    # Else the current page contains links to other pages, page chances will be calculated based on those links
    else:
        # For every page, if the page is found in the links on the current page, that pages rate of being chosen
        # is the first formula, else its the second formula
        for pageName in pageNames:
            if pageName in pageLinks:
                pageChosenRates[pageName] = damping_factor / len(pageLinks)
            else:
                pageChosenRates[pageName] = (1 - damping_factor) / len(corpus)

    # Returns a dictionary containing the name of each page as a key and its chance of being chosen as a value
    return pageChosenRates

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Holds list of all page names
    pageNames = list(corpus.keys())

    # Dict that will hold all page names as keys and their calculated ranks as values, sums to 1.
    # Will hold amount of times page was chosen in following for loop before being translated to pagerank
    estimatedPageRanks = {}

    # Chooses a random page out of all the page names and sets 1 to the amount of times it was chosen
    pageChosen = random.choice(list(corpus.keys()))
    estimatedPageRanks[pageChosen] = 1

    # For each iteration minus the first one which was randomly chosen, choses a new page based on its probability
    # of being chosen as calculated by transition_model
    for i in range(n - 1):

        # Calculates and holds the chances of the next page being chosen
        pageChances = transition_model(corpus, pageChosen, damping_factor)

        # Randomly selects a page based on its probability of being chosen
        pageChosen = random.choices(list(pageChances.keys()), weights = list(pageChances.values()), k = 1)[0]

        # If the page that was chosen has not been chosen before adds its key to the ranks dict with a value of 1
        # else the key is already in the dictionary and it 1 is added to the amount of times that page was chosen
        if pageChosen not in list(estimatedPageRanks.keys()):
            estimatedPageRanks[pageChosen] = 1
        else:
            estimatedPageRanks[pageChosen] += 1
    
    # Assigns page ranks based on amount of times the page was visited / the total amount of pages visited
    for pageName, pageCount in estimatedPageRanks.items():
        estimatedPageRanks[pageName] = pageCount / n
    
    # Returns dictionary containing page names as keys and their estimated page ranks as values
    return estimatedPageRanks

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Holds list of all page names
    pageNames = list(corpus.keys())

    # Dict to be returned, key = page name, value = page rank
    estimatedPageRanks = {}

    # Initializes the first half of the calculation
    half1 = (1 - damping_factor) / len(corpus)

    # Fills ranks dict with all the page names as keys and their initial even rankings as values
    for pageName in corpus.keys():
        estimatedPageRanks[pageName] = 1 / len(corpus)

    # Utilizes probability formula to calculate page ranks, breaks when convergence is reached
    endFlag = False
    while endFlag == False:

        # Copies the initial page ranks, used for convergence testing later
        initialValues = estimatedPageRanks.copy()

        # Iterates through each page calculating that pages new page rank
        for pageName in pageNames:

            # Dict that holds the pages that link to pageName, key = page that links to this one, 
            # value = total number of links on that page
            linksToPage = {}

            # Fills linksToPage dict
            for corpusPageName, links in corpus.items():
                # If current page being calculated is found in a sites links, adds that site and its number
                # of links to the linksToPage dict
                if pageName in links:
                    linksToPage[corpusPageName] = len(links)
                # If current page has no links at all, adds that site and a link for every page in the corpus
                # to the linksToPage dict
                elif len(links) < 1:
                    linksToPage[corpusPageName] = len(corpus)

            # Calculates the sum of i as shown in the second half of the equation
            sum = 0
            for corpusPageName, links in linksToPage.items():
                sum += estimatedPageRanks[corpusPageName] / links

            # Finishes calculating second half of the equation
            half2 = damping_factor * (sum)

            # Utilizes both halfs of the equation to calculate the current pages new page rank
            estimatedPageRanks[pageName] = half1 + half2

        # Calculates total variation between the initial page ranks and the newly calculated ones
        totalVariation = 0
        for corpusPageName, rank in estimatedPageRanks.items():
            totalVariation += abs(initialValues[corpusPageName] - rank)

        # If variation is within a small margin, ends loop
        if totalVariation < .001:
            endFlag = True
    
    # Returns a dict containing the estimated page ranks for each page
    return estimatedPageRanks


if __name__ == "__main__":
    main()
