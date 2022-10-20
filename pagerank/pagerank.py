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
    # 0.0 - 1.0
    randomNumber = random.random()

    # All pages the current page links to
    pageLinks = corpus[page]

    # Holds pages and their random rates of being chosen
    pageRandomRates = {}

    # Holds all page names
    pageNames = list(corpus.keys())

    if len(pageLinks) < 1:
        # Fills dict with chance for random page out of all pages
        for pageName in pageNames:
            pageRandomRates[pageName] = 1 / len(corpus)
    
    # If number is within damping factor, and page contains links, choose from links, else randomly from all pages
    else:
        for pageName in pageNames:
            # If page linked to current page
            if pageName in pageLinks:
                pageRandomRates[pageName] = damping_factor / len(pageLinks)
            else:
                pageRandomRates[pageName] = (1 - damping_factor) / len(corpus)

    #print(f"initial: {page}")
    #print(pageRandomRates.keys())
    #print(pageRandomRates.values())
    return pageRandomRates


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Holds all page names
    pageNames = list(corpus.keys())

    # Dict holds all pages and their calculated rank, sums to 1
    estimatedPageRanks = {}

    # Chooses a random page out of all the page names
    pageChosen = random.choice(list(corpus.keys()))
    estimatedPageRanks[pageChosen] = 1

    # For each iteration minus the first random one
    for i in range(n - 1):
        pageChances = transition_model(corpus, pageChosen, damping_factor)
        pageNames = list(pageChances.keys())
        pageWeights = list(pageChances.values())
        #print(pageChances.keys())
        #print(pageChances.values())
        pageChosen = random.choices(pageNames, weights = pageWeights, k = 1)[0]
        #print(f"chosen: {pageChosen}\n")
        if pageChosen not in list(estimatedPageRanks.keys()):
            estimatedPageRanks[pageChosen] = 1
        else:
            estimatedPageRanks[pageChosen] += 1
    
    # Assigns values based on amount of times page visited
    for pageName, pageCount in estimatedPageRanks.items():
        # Amount of times page visited / total chances
        estimatedPageRanks[pageName] = pageCount / n
    
    return estimatedPageRanks



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
