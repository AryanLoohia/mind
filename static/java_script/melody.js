document.addEventListener('DOMContentLoaded', function () {
    const menuButton = document.getElementById('menuButton');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    menuButton.addEventListener('click', function () {
        sidebar.classList.toggle('active');
        mainContent.classList.toggle('with-sidebar');
        menuButton.classList.toggle('active');
    });

    // Existing player controls code
    const playButton = document.getElementById('playButton');
    const pauseButton = document.getElementById('pauseButton');
    const audioPlayer = new Audio();
    const previousButton = document.getElementById('previousButton');
    const nextButton = document.getElementById('nextButton');
    const seekBar = document.getElementById('seekBar');
    const currentTime = document.getElementById('currentTime');
    const duration = document.getElementById('duration');
    const volumeControl = document.getElementById('volumeControl');
    const trackTitle = document.getElementById('trackTitle');
    const trackArtist = document.getElementById('trackArtist');
    const albumArt = document.getElementById('albumArt');

    const songs = [
        {
            title: 'Track 1',
            artist: 'Artist 1',
            albumCover: '/static/images/cover1.png',
            track: '/static/music/track1.mp3'
        },
        {
            title: 'Track 2',
            artist: 'Artist 2',
            albumCover: '/static/images/cover2.jpg',
            track: '/static/music/track2.mp3'
        }
    ];

    let currentTrackIndex = 0;

    function loadTrack(song) {
        trackTitle.textContent = song.title;
        trackArtist.textContent = song.artist;
        albumArt.src = song.albumCover;
        audioPlayer.src = song.track;
        audioPlayer.load();
    }

    playButton.addEventListener('click', function () {
        audioPlayer.play();
        playButton.style.display = 'none';
        pauseButton.style.display = 'inline';
    });

    pauseButton.addEventListener('click', function () {
        audioPlayer.pause();
        playButton.style.display = 'inline';
        pauseButton.style.display = 'none';
    });

    previousButton.addEventListener('click', function () {
        currentTrackIndex = (currentTrackIndex - 1 + songs.length) % songs.length;
        loadTrack(songs[currentTrackIndex]);
        audioPlayer.play();
        playButton.style.display = 'none';
        pauseButton.style.display = 'inline';
    });

    nextButton.addEventListener('click', function () {
        currentTrackIndex = (currentTrackIndex + 1) % songs.length;
        loadTrack(songs[currentTrackIndex]);
        audioPlayer.play();
        playButton.style.display = 'none';
        pauseButton.style.display = 'inline';
    });

    audioPlayer.addEventListener('timeupdate', function () {
        const value = (audioPlayer.currentTime / audioPlayer.duration) * 100;
        seekBar.value = value;
        currentTime.textContent = formatTime(audioPlayer.currentTime);
        duration.textContent = formatTime(audioPlayer.duration);
    });

    seekBar.addEventListener('input', function () {
        const time = (seekBar.value / 100) * audioPlayer.duration;
        audioPlayer.currentTime = time;
    });

    volumeControl.addEventListener('input', function () {
        audioPlayer.volume = volumeControl.value / 100;
    });

    function formatTime(time) {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }

    loadTrack(songs[currentTrackIndex]);
});
