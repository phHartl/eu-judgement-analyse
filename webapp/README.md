

# Run the Web-App

-	Open a command line and navigate to the repository's ./webapp/ folder
-	Run `npm install` in order to install all needed node modules
-	Run `npm start` (see below)

### `npm start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.


# Available Functions

The Web-App will look like this:
![startpage](./demo_screenshots/home.png)

It features **two main views**: the **Search Filter** view and the **Analysis Options** view. A new query is submitted by clicking the *Submit Query* button.

## Search Filter view

By default the Search Filter view contains two inputs: *Quick Search* and *Language*. 

### Quick Search
*Quick Search* can be used to quickly search the database for *Document Titles*, European Case Law Identifier (*ECLI*) and *CELEX* number. The Web App will intelligently match the entered parameters, so separation or trailing typos do not influence the search. Leave the Quick Search empty if you do not wish to include any of these modifiers in your search.

#### Example Quick Search:
A user wants to quickly search for two documents they have bookmarked. They enter their CELEX numbers into the Quick Search:

![Quick Search Example 1](./demo_screenshots/quick_search_example_1.png)

The Web App identifies the entered paramters as CELEX numbers and returns the matching documents from the database. In this case, the user separated the two parameters using a comma. The parameter matching function is able to handle many ways of input seperation, including typos. For example, the following query would match and return the same results as the previous one:

![Quick Search Example 2](./demo_screenshots/quick_search_example_2.png)


### Language

The *Language* dropdown allows the user to switch between matching English and German documents.

![Language Selection Example](./demo_screenshots/quick_search_language.png)

### Advanced Search Filters
By clicking the *+ Add Search Filter Button*, the user can open a menu that allows adding additional filters to the search.

![Advanced Search Filters](./demo_screenshots/advanced_filters_1.png)

A new filter is added by clicking on its respective Button. In the following example, a new *Subject* filter was added:
![Added Subject Filter](./demo_screenshots/advanced_filters_subject.png)

These advanced filters offer additional actions: they can be removed from the query by clicking the *trash can* icon, and they can be negated/excluded by clicking the *Include* toggle. Including a filter means all documents that match the filter will be returned, while excluding a filter means that all documents that do *not* match the filter will be returned.

## Analysis Options

By clicking on the *+ Add Analysis Option* button, the user can open a menu that allows adding different kinds of text analysis options to the query. Every query must contain at least one selected Analysis Option.
![Analysis Options](./demo_screenshots/analysis_options_1.png)

Some Analysis Options include customizable parameters that can be interacted with. For example, the "Token Count" option provides toggles for removing stop words and punctuation, as well as inclusion or exclusion of certain PoS tags.

For a full explanation of all available options see the documentation in the repository's root folder.

![Analysis Options Parameter Example](./demo_screenshots/analysis_options_2.png)


## Results

After a brief processing time (dependent on the size of the corpus and the chosen Analysis Options) the results will be shown at the bottom of the page. Some options allow the user to choose a visualization style, for example N-Grams can be viewed as either a wordcloud (recommended for a large set of data) or a bar chart.

The user can also *Download* the entire result set by clicking the *Download* button, or download only a single result by clicking its respective button (e.g. "Download N-Grams" button to download only the N-Grams result). The downloaded file will be a .json file that contains all retrieved information.

