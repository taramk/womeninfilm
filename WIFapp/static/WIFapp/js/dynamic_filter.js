import { createFilmItem } from './create_film_list_item.js';

document.addEventListener('DOMContentLoaded', function() {
    setupPage();
});

function setupPage() {
    const decadeSelector = document.getElementById('decade-selector');
    const genreSelector = document.getElementById('genre-selector');
    const bechdelCheckbox = document.getElementById('bechdel-checkbox');
    const womenWrittenCheckbox = document.getElementById('women-written-checkbox');
    const womenDirectedCheckbox = document.getElementById('women-directed-checkbox');
    const sortByRatingCheckbox = document.getElementById('sort-by-rating-checkbox');

    function fetchFilteredFilms() {
        const selectedGenres = Array.from(genreSelector.selectedOptions, option => option.value).join(',');
        fetch(`/filter_films/?decade=${decadeSelector.value}&genres=${selectedGenres}&passes_bechdel=${bechdelCheckbox.checked}&women_written=${womenWrittenCheckbox.checked}&women_directed=${womenDirectedCheckbox.checked}&sort_by_rating=${sortByRatingCheckbox.checked}`)
            .then(response => response.json())
            .then(data => {
                const filmListContainer = document.getElementById('film-list');
                filmListContainer.innerHTML = data.films.map(film => createFilmItem(film)).join('');
            })
            .catch(error => {
                console.error('Error fetching films:', error);
            });
    }

    function saveFilterState() {
        const selectedGenres = Array.from(genreSelector.selectedOptions, option => option.value);
        const filterState = {
            decade: decadeSelector.value,
            genres: selectedGenres,
            bechdelChecked: bechdelCheckbox.checked,
            womenWrittenChecked: womenWrittenCheckbox.checked,
            womenDirectedChecked: womenDirectedCheckbox.checked,
            sortByRatingChecked: sortByRatingCheckbox.checked
        };
        localStorage.setItem('filterState', JSON.stringify(filterState));
    }

    function restoreFilterState() {
        const savedState = JSON.parse(localStorage.getItem('filterState'));
        if (savedState) {
            decadeSelector.value = savedState.decade;
            Array.from(genreSelector.options).forEach(option => {
                option.selected = savedState.genres.includes(option.value);
            });
            bechdelCheckbox.checked = savedState.bechdelChecked;
            womenWrittenCheckbox.checked = savedState.womenWrittenChecked;
            womenDirectedCheckbox.checked = savedState.womenDirectedChecked;
            sortByRatingCheckbox.checked = savedState.sortByRatingChecked;
        }
    }

    function handleFilterChange() {
        fetchFilteredFilms();
        saveFilterState();
    }

    // set up filter event listeners
    [decadeSelector, genreSelector, bechdelCheckbox, womenWrittenCheckbox, womenDirectedCheckbox, sortByRatingCheckbox].forEach(element => {
        element.addEventListener('change', handleFilterChange);
    });

    restoreFilterState(); // restore filters on page load
    fetchFilteredFilms(); // initial fetch for the default state
}