const token = document.currentScript.getAttribute('data-access-token');
let deviceId = null;

window.onSpotifyWebPlaybackSDKReady = callback => {
    const player = new Spotify.Player({
        name: 'Spotify Wrapper',
        getOAuthToken: cb => { cb(token); },
        volume: 0.2
    });

    player.on('ready', ({ device_id }) => {
        deviceId = device_id;
    });

    player.on('initialization_error', e => console.error(e));
    player.on('authentication_error', e => console.error(e));
    player.on('account_error', e => console.error(e));
    player.on('playback_error', e => console.error(e));

    player.connect();
};

function play(trackUri) {
    if (!deviceId) {
        setTimeout(() => play(trackUri), 500);
        return;
    }
    fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
        method: 'PUT',
        body: JSON.stringify({ uris: [trackUri] }),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
    }).catch(e => console.error('Failed to play track:', e));
}