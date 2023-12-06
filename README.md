# What is it
Women in Film is a movie database where you can explore films where women have had a significant contribution. You can dynamically filter by woman directed, woman written, and other aspects like "passes Bechdel test", as well as release year and genre. You can also explore women actors, directors, and writers.

## Why I did it
I am very interested in film, and I watch a lot of movies. The majority of movies that are considered classics/are well-known are male-centered: stories about men, written by men, and directed by men. I'd like to watch more movies centered on the female experience, and I want to support female creators by watching their films. So, I created this site to make it easier to explore films where women are involved in some significant capacity: stars, writers, and/or directors. I've also incorporated Bechdel test data, and hope to help make that dataset more complete.
As a side note, it has been an interesting philosophical question to determine what counts as a "significant contribution by women". Aside from checking director and writer credits, I've decided to check whether the top-billed actor is a woman, as well as whether 2 out of 3 of the top billed actors are women. 

# Distinctiveness and Complexity
Compared to other projects in CS50 Web, the work I've done for Women in Film focuses heavily on data retrieval, database design, and dynamic filtering.

### Data retrieval
A significant part of my work on this project was on the "generate film data" script. The script pulls data from The Movie Database's API and inserts it into my SQLite database. It then cleans up the data and adds some boolean columns to help with filtering.
The script became especially complex as the database evolved and grew. I had to write scripts to update existing records (when I decided to add more metadata), as well as maintain the "generate data" script so it would include everything when starting from scratch.
I learned how to handle API errors like missing data without having my script break. The script needed to be resilient enough to handle errors and move on, because it takes a long time to run and the data is not perfectly clean/consistent.
I decided to store the data myself for several reasons.
- The entire app relies on the data, so I didn't feel comfortable relying on the API as a single point of failure
- This is more secure, because I don't have to store my API token in the codebase.
- It's a free API, so I didn't want to use more server resources than I needed to
- The way the API is structured, I would need to pull large amounts of movies into memories and then filter them down to a small subset; it didn't feel like the most efficient choice.
- Because there is a lot of filtering and customization, it's more performant to store the data myself and augment it. 

### Database design
I built a tailored database schema to manage complex relationships between entities including Person, Film, Genre, Star, and Crew. I added custom fields like "starring_women" to flag specific attributes for filtering. I also added custom functions to the Film model in particular to make data retrieval easier in the views; for example, I created functions to return a list of directors or writers.
I learned about indexes, and applied them to the columns that would be filtered on most often.
I chose to keep the SQLite database because ultimately I don't have that much data; There are about 3,000 films and 10,000 people in the database.

### Dynamic filtering
I implemented an advanced filtering system to dynamically search films based on decade, genre, and specific boolean attributes like "written by women" and "passes Bechdel test".
I'm also doing some advanced Javascript to save their filter settings in local storage so they can use browser back to view the films in the last-filtered state.
Additionally, I'm shuffling the films on each view to make it easier to discover new movies.

# File descriptions
* models.py: Defines the database models for Person, Film, Genre, Star, and Crew.
* views.py: Contains the views for rendering the film list, individual film details, and filtered results based on user selections. Also has a people view used to generate lists of actors, writers, and directors.
* urls.py: Maps URLs to their corresponding views in the application.
* templates/: Holds HTML templates for different pages of the application, using Django's template language for dynamic content rendering.
* static/: Contains static files like CSS, JavaScript, and images. JavaScript files here are responsible for handling dynamic filtering and AJAX requests.
* static/scripts/: Contains Python scripts for updating the database from external APIs and processing data.
requirements.txt: Lists all Python dependencies for the project.

# How to run
* To use the existing database, all you need to do is run python manage.py runserver from the top level directory.

# What else to know
Any other additional information the staff should know about your project.

# Requirements.txt
If you’ve added any Python packages that need to be installed in order to run your web application, be sure to add them to a requirements.txt file!


