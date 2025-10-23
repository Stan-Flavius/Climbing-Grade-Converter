# Power BI Climbing Grade Converter

This is an interactive dashboard built in Power BI that acts as a universal climbing grade converter.

<img width="1523" height="859" alt="image" src="https://github.com/user-attachments/assets/03e28ad6-89e4-4d5c-9262-0e3bce793352" />


## Features
* **Interactive Converter:** Select any grade from one of 7 climbing disciplines (Bouldering, Free, Alpine, etc.) and see the equivalent grades across all other systems.
* **Live Filtering:** The dashboard filters a database of over 12,000 routes in real-time.
* **Data Visualization:** Includes a pie chart for route distribution, and a scatter plot analyzing difficulty vs. popularity (ascents) and a reset button.


## Technical Details

* **Tools & Technologies:**
    * **Data Scraping:** Python, Selenium, undetected-chromedriver
    * **Data Cleaning & Analysis:** Python, Pandas, NumPy, Regular Expressions (re)
    * **Dashboarding:** Power BI, Power Query (M), DAX
    * **File Handling:** openpyxl (for Excel export)

* **Data Source (Script 1):**
    * Raw route data was scraped from `thecrag.com`, a dynamic, JavaScript-heavy site.
    * Used **`undetected-chromedriver`** to bypass bot-detection measures and **`Selenium`** to automate login, pagination, and data extraction.

* **Data Cleaning & Classification (Script 2):**
    * The raw CSV was processed using **pandas** and **numpy**.
    * A complex classification engine using **Regular Expressions (re)** was built to parse unstructured grade strings and successfully categorize over 8,000 routes into 7 distinct climbing disciplines (Mixed, Ice, Aid, Bouldering, Alpine, Free, and Unclassified).
    * Standardized French and UIAA grades to a single `Standard_Grade` for comparison.
    * The final, clean datasets were exported to a multi-sheet Excel file using `openpyxl`.

* **Data Modeling (Power BI):**
    * The 7 classified sheets were imported and appended into a single `All_Routes` fact table using **Power Query**.
    * A "star schema" with a Many-to-One relationship was initially built but was **purposefully scrapped** as it over-complicated the DAX filtering logic.
    * **Final Model:** Adopted a more robust model where the `DifficultyIndex` was "stamped" onto the `All_Routes` table at the query stage. This simplified the DAX and improved performance.

* **Key DAX Measures:**
    * Developed a complex `[IsEquivalent]` measure to power the entire dashboard.
    * This measure uses `CALCULATE(..., ALLSELECTED())` to "hop out" of the visual filter context, allowing it to read slicer selections even when "Edit Interactions" is set to "None".
    * This "disconnected slicer" pattern is what allows the slicers to filter all visuals without directly interacting with them.


## How to View

You can [**view the live, interactive dashboard here**](https://tinyurl.com/ClimbingConverter).

You can also download the [project .pbix file](https://github.com/Stan-Flavius/Climbing-Grade-Converter/blob/main/Grade%20Converter.pbix) and the [source Excel data](https://github.com/Stan-Flavius/Climbing-Grade-Converter/blob/main/crag_routes.csv) from this repository.
