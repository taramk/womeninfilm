export function createFilmItem(film) {

    // this is also used in the all_women template, so keep them synced
    return `
        <a href="/film/${film.id}">
            <div class="film-item">
                <div class="image-container">
                    <img src='https://image.tmdb.org/t/p/w400/${film.poster_path}'>
                </div>

            </div>
        </a>
    `;
}