# Power BI Climbing Grade Converter

This is an interactive dashboard built in Power BI that acts as a universal climbing grade converter.

<img width="1523" height="859" alt="image" src="https://github.com/user-attachments/assets/03e28ad6-89e4-4d5c-9262-0e3bce793352" />


## Features
* **Interactive Converter:** Select any grade from one of 7 climbing disciplines (Bouldering, Free, Alpine, etc.) and see the equivalent grades across all other systems.
* **Live Filtering:** The dashboard filters a database of over 12,000 routes in real-time.
* **Data Visualization:** Includes a pie chart for route distribution, and a scatter plot analyzing difficulty vs. popularity (ascents) and a reset button.

## Technical Details

* **Tools:** Power BI, Python (Pandas, NumPy, Selenium)
* **Data Source:** Raw route data was scraped from a dynamic, JavaScript-heavy climbing website using **Selenium** to automate browser interaction and extract data.
* **Data Cleaning (ETL):** The raw, unstructured data was processed using **pandas** and **numpy**. This involved:
    * Parsing and standardizing varied grade formats across 7 climbing disciplines.
    * Cleaning text data (`Route Name`) and handling missing values.
    * Aggregating ascent data and structuring the final clean dataset for analysis.
* **Data Modeling:** The clean dataset was loaded into Power BI. A star schema was built to connect the `All_Routes` fact table to a master `Grade_Str` dimension table but was later scrapped.
* **Key DAX Measures:** Developed custom DAX measures (like `[IsEquivalent]`) to handle the complex, multi-slicer filtering logic and enable the "converter" functionality.


## How to View

You can [**view the live, interactive dashboard here**](https://tinyurl.com/ClimbingConverter).

You can also download the [project .pbix file](https://github.com/Stan-Flavius/Climbing-Grade-Converter/blob/main/Grade%20Converter.pbix) and the [source Excel data](https://github.com/Stan-Flavius/Climbing-Grade-Converter/blob/main/crag_routes.csv) from this repository.
