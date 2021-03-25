## Confluence macro migration script

This script uses the Confluence REST API to search for and replaces the following macros:

| Search  | Replace |
|:--- |:--- |
|tdp-fragment|multiexcerpt-macro|
|tdp-fragment-include|multiexcerpt-macro-include|

---

In order to run the script, install the required packages using `pip` in the environment of your choosing. 
`conda` is used as the environment manager throughout this project

```bash
conda create --name confluence-macro-mig python=3.8
conda activate confluence-macro-mig
pip install -r requirements.txt
```

Once the required packages have been installed, run the script with the required arguments

```shell script
python main.py --help
python main.py --username=FOO --password=BAR --method=xml --spaces DOM DOMARCHIVE ESAS LOVARK DAP DRL 
```
---

### Search / Replace methods

Two methods are available for search / replace and one should be supplied to the `--method` argument. 

#### Regex
A set of varying regex patterns are defined in `regex.py`. This method is much faster than the alternate `xml` method 
however it does not successfully manage to identify all possible macros. This is because the macro-parameters may come in different order
and though it is possible to write a regex that matches each case, it is quite ugly and hard to maintain

#### XML
Alternatively, the body of the page can be parsed as XML. This allows for exact hits for each macro but it is a bit slower.
It is recommended to use this method

---

### The major flaw with this method

Each macro has a unique ID. During replacement these id's are preserved. That is a tdp-fragment with ID: "ABC123" will be replace with a multiexcerpt with the same ID: "ABC123"
This could lead to potential errors in the future, as I believe these ID's are generated and saved in the database that confluence is connected to. (I think this database is running on-premise).
A more robust method of replacing these macros would be to look at the database tables and see how they are structured and make sure that this script runs without side effects 
(or alternatively do the search / replace directly on the db)

### Future Work
- Investigate the use of CQL (Confluence Query Language) instead of scraping every page in a space
- 


